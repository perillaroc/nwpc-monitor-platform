# coding=utf-8

import datetime
import gzip

import requests
from flask import json, current_app

from nmp_broker.common import weixin, data_store
from nwpc_workflow_model.ecflow import Bunch, ErrorStatusTaskVisitor, pre_order_travel, NodeStatus

from nmp_broker.common.workflow.status_strategy import is_new_abort_task_found, is_new_abort_root_found

REQUEST_POST_TIME_OUT = 20


def handle_status_message(message_data: dict) -> None:
    """
    message_data:
    {
        "name": "ecflow_status_message_data",
        "type": "record",
        "fields": [
            {"name": "owner", "type": "string"},
            {"name": "repo", "type": "string"},
            {"name": "time", "type": "string"},
            {
                "name": "status",
                "doc": "bunch status",
                "type": { "type": "node" }
            }
        ]
    }
    """
    owner = message_data['owner']
    repo = message_data['repo']
    ecflow_name = message_data['repo']
    message_time = message_data['time']

    bunch_dict = message_data['status']
    message_datetime = datetime.datetime.strptime(message_time, "%Y-%m-%dT%H:%M:%S.%f")

    # warn_user_list = data_store.get_ding_talk_warn_user_list(owner, repo)

    nmp_model_system_store_flag = False
    nmp_model_system_dict = None

    if len(bunch_dict) == 0:
        return

    print('building bunch from message...')

    bunch = Bunch.create_from_dict(bunch_dict)

    # NOTE: Because Bunch.create_from_dict will use Bunch.name as path prefix, We need to set it to empty string.
    # So that its path begins with '/' as the same as path in bunch_dict generated by nwpc-log-collector.
    bunch.name = ''

    print('building bunch from message...Done')

    # find error tasks every suite
    suite_error_map = dict()
    error_task_dict_list = []
    for a_suite in bunch.children:
        error_visitor = ErrorStatusTaskVisitor()
        pre_order_travel(a_suite, error_visitor)
        suite_error_map[a_suite.name] = {
            'name': a_suite.name,
            'status': a_suite.status,
            'error_task_list': error_visitor.error_task_list
        }
        for a_task in error_visitor.error_task_list:
            error_task_dict_list.append(a_task.to_dict())

    server_status = bunch.status

    if server_status == NodeStatus.aborted:
        cached_sms_server_status = data_store.mongodb.workflow.get_server_status_from_cache(owner, repo, ecflow_name)
        if cached_sms_server_status is not None:

            print('building bunch from cache message...')
            cached_bunch = Bunch.create_from_dict(cached_sms_server_status['data']['status'])
            print('building bunch from cache message...Done')

            previous_server_status = cached_bunch.status

            if True:
            # if is_new_abort_task_found(owner, repo, previous_server_status, error_task_dict_list):
                nmp_model_system_dict = data_store.save_server_status_to_nmp_model_system(
                    owner, repo, ecflow_name,
                    message_data, error_task_dict_list
                )

                nmp_model_system_store_flag = True

                aborted_tasks_blob_id = None
                for a_blob in nmp_model_system_dict['blobs']:
                    if a_blob['data']['type'] == 'aborted_tasks':
                        aborted_tasks_blob_id = a_blob['id']

                warning_data = {
                    'owner': owner,
                    'repo': repo,
                    'server_name': ecflow_name,  # bunch.name
                    'message_datetime': message_datetime,
                    'suite_error_map': suite_error_map,
                    'aborted_tasks_blob_id': aborted_tasks_blob_id
                }

                # ding_talk_app = ding_talk.DingTalkApp(
                #     ding_talk_config=app.config['BROKER_CONFIG']['ding_talk_app'],
                #     cloud_config=app.config['BROKER_CONFIG']['cloud']
                # )
                #
                # ding_talk_app.send_warning_message(warning_data)

                weixin_app = weixin.WeixinApp(
                    weixin_config=current_app.config['BROKER_CONFIG']['weixin_app'],
                    cloud_config=current_app.config['BROKER_CONFIG']['cloud']
                )
                weixin_app.send_warning_message(warning_data)

    # 保存 error_task_list 到缓存
    error_task_value = {
        'timestamp': datetime.datetime.utcnow(),
        'error_task_list': error_task_dict_list
    }
    data_store.redis.save_error_task_list_to_cache(owner, repo, error_task_value)

    data_store.mongodb.workflow.save_server_status_to_cache(owner, repo, ecflow_name, message_data)

    # 发送给外网服务器
    website_url = current_app.config['BROKER_CONFIG']['cloud']['put']['url'].format(
        owner=owner,
        repo=repo
    )
    if nmp_model_system_store_flag:
        post_message = {
            'app': 'nmp_broker',
            'event': 'post_ecflow_status',
            'timestamp': datetime.datetime.utcnow(),
            'data': {
                'type': 'takler_object',
                'blobs': nmp_model_system_dict['blobs'],
                'trees': nmp_model_system_dict['trees'],
                'commits': nmp_model_system_dict['commits']
            }
        }

        website_post_data = {
            'message': json.dumps(post_message)
        }
    else:
        message_data['type'] = 'status'
        post_message = {
            'app': 'nmp_broker',
            'event': 'post_ecflow_status',
            'timestamp': datetime.datetime.utcnow(),
            'data': message_data
        }
        website_post_data = {
            'message': json.dumps(post_message)
        }

    print('gzip the data...')
    gzipped_post_data = gzip.compress(bytes(json.dumps(website_post_data), 'utf-8'))
    print('gzip the data...done')

    response = requests.post(
        website_url,
        data=gzipped_post_data,
        headers={
            'content-encoding': 'gzip'
        },
        timeout=REQUEST_POST_TIME_OUT
    )
    print(response)
    return
