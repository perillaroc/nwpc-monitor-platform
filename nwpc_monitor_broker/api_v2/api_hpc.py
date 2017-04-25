from flask import request, jsonify, json
import datetime
import requests
import gzip

from nwpc_monitor_broker import app

from nwpc_monitor_broker.api_v2 import api_v2_app
from nwpc_monitor_broker.api_v2 import cache

from nwpc_monitor_broker.plugins.loadleveler import loadleveler_filter

REQUEST_POST_TIME_OUT = 60


@api_v2_app.route('/hpc/users/<user>/disk/usage', methods=['POST'])
def receive_disk_usage_message(user):
    start_time = datetime.datetime.now()

    content_encoding = request.headers.get('content-encoding', '').lower()
    if content_encoding == 'gzip':
        gzipped_data = request.data
        data_string = gzip.decompress(gzipped_data)
        body = json.loads(data_string.decode('utf-8'))
    else:
        body = request.form

    message = json.loads(body['message'])

    if 'error' in message:
        result = {
            'status': 'ok'
        }
        return jsonify(result)

    message_data = message['data']

    key, value = cache.save_hpc_disk_usage_status_to_cache(user, message)

    print("post disk usage to cloud: user=", user)
    post_data = {
        'message': json.dumps(value)
    }
    post_url = app.config['BROKER_CONFIG']['hpc']['disk_usage']['cloud']['put']['url'].format(
        user=user
    )

    print('gzip the data...')
    gzipped_post_data = gzip.compress(bytes(json.dumps(post_data), 'utf-8'))
    print('gzip the data...done')

    response = requests.post(
        post_url,
        data=gzipped_post_data,
        headers={
            'content-encoding': 'gzip'
        },
        timeout=REQUEST_POST_TIME_OUT
    )

    print("post disk usage to cloud done: response=", response)

    result = {
        'status': 'ok'
    }
    end_time = datetime.datetime.now()
    print(end_time - start_time)

    return jsonify(result)


@api_v2_app.route('/hpc/users/<user>/disk/usage', methods=['GET'])
def get_disk_usage_message(user: str):
    start_time = datetime.datetime.now()

    result = cache.get_hpc_disk_usage_status_from_cache(user)

    end_time = datetime.datetime.now()
    print(end_time - start_time)

    return jsonify(result)


@api_v2_app.route('/hpc/info/disk/space', methods=['POST'])
def receive_disk_space_message():
    start_time = datetime.datetime.now()

    content_encoding = request.headers.get('content-encoding', '').lower()
    if content_encoding == 'gzip':
        gzipped_data = request.data
        data_string = gzip.decompress(gzipped_data)
        body = json.loads(data_string.decode('utf-8'))
    else:
        body = request.form

    message = json.loads(body['message'])

    if 'error' in message:
        result = {
            'status': 'ok'
        }
        return jsonify(result)

    message_data = message['data']

    key, value = cache.save_hpc_disk_space_status_to_cache(message)

    print("post disk usage to cloud")
    post_data = {
        'message': json.dumps(value)
    }
    post_url = app.config['BROKER_CONFIG']['hpc']['disk_space']['cloud']['put']['url']

    print('gzip the data...')
    gzipped_post_data = gzip.compress(bytes(json.dumps(post_data), 'utf-8'))
    print('gzip the data...done')

    response = requests.post(
        post_url,
        data=gzipped_post_data,
        headers={
            'content-encoding': 'gzip'
        },
        timeout=REQUEST_POST_TIME_OUT
    )
    print("post disk space to cloud done: response=", response)

    result = {
        'status': 'ok'
    }
    end_time = datetime.datetime.now()
    print(end_time - start_time)

    return jsonify(result)


@api_v2_app.route('/hpc/info/disk/space', methods=['GET'])
def get_disk_space_message():
    start_time = datetime.datetime.now()

    result = cache.get_hpc_disk_space_status_from_cache()

    end_time = datetime.datetime.now()
    print(end_time - start_time)

    return jsonify(result)


@api_v2_app.route('/hpc/users/<user>/loadleveler/status', methods=['POST'])
def receive_loadleveler_status(user):
    start_time = datetime.datetime.now()

    content_encoding = request.headers.get('content-encoding', '').lower()
    if content_encoding == 'gzip':
        gzipped_data = request.data
        data_string = gzip.decompress(gzipped_data)
        body = json.loads(data_string.decode('utf-8'))
    else:
        body = request.form

    message = json.loads(body['message'])

    if 'error' in message:
        result = {
            'status': 'ok'
        }
        return jsonify(result)

    message_data = message['data']

    key, value = cache.save_hpc_loadleveler_status_to_cache(user, message)

    if 'error' not in message:
        job_items = message_data['response']['items']
        filter_results = loadleveler_filter.apply_filters(job_items)
        print(filter_results)

    print("post loadleveler status to cloud: user=", user)
    post_data = {
        'message': json.dumps(value)
    }
    post_url = app.config['BROKER_CONFIG']['hpc']['loadleveler_status']['cloud']['put']['url'].format(
        user=user
    )

    print('gzip the data...')
    gzipped_post_data = gzip.compress(bytes(json.dumps(post_data), 'utf-8'))
    print('gzip the data...done')
    response = requests.post(
        post_url,
        data=gzipped_post_data,
        headers={
            'content-encoding': 'gzip'
        },
        timeout = REQUEST_POST_TIME_OUT
    )
    print("post loadleveler status to cloud done:  response=", response)

    result = {
        'status': 'ok'
    }
    end_time = datetime.datetime.now()
    print(end_time - start_time)

    return jsonify(result)
