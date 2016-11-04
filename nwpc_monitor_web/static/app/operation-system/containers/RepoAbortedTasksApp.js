import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';

import { NodeStatusImage } from '../../base/components/NodeStatusImage'

import { fetchOperationSystemRepoAbortedTasks } from '../actions/repo';
import { Util } from '../../base/util/util'

class RepoAbortedTasksApp extends Component{
    componentDidMount(){
        const { dispatch, params } = this.props;
        let owner = params.owner;
        let repo = params.repo;
        let aborted_task_id = params.aborted_task_id;

        dispatch(fetchOperationSystemRepoAbortedTasks(owner, repo, aborted_task_id));
    }

    render() {
        const { params, aborted_tasks } = this.props;
        if(aborted_tasks===null)
        {
            return (
                <div>
                    <p>不存在</p>
                </div>
            )
        }

        let owner = params.owner;
        let repo = params.repo;
        let aborted_task_id = params.aborted_task_id;

        let repo_last_update_time = '未知';
        let cur_time = new Date();
        if(aborted_tasks['update_time']!=null) {
            let last_updated_time = new Date(aborted_tasks['update_time']);
            repo_last_update_time = Util.getDelayTime(last_updated_time, cur_time);
        }

        let task_nodes = aborted_tasks['tasks'].map(function(a_task, i){
            let a_task_status = "unk";
            if(a_task['status']!=null)
                a_task_status = a_task['status'];

            let image_style = {
                width:'40px',
                marginRight:'5px'
            };

            return (
                <p key={i} >
                    <NodeStatusImage node_status={ a_task_status } image_style={ image_style } />
                    { a_task['path'] }
                </p>
            )
        });

        return (
            <div>
                <p>更新时间：{ repo_last_update_time }</p>

                <article className="weui-article">
                    <section>
                        <h1>出错任务</h1>
                        { task_nodes }
                    </section>
                </article>

                <div className="weui-cells__title">链接</div>
                <div className="weui-cells weui-cells_access">
                    <a className="weui-cell" href="/{{ owner }}/{{ repo }}">
                        <div className="weui-cell__bd weui-cell_primary">
                            <p>最新状态</p>
                        </div>
                        <div className="weui-cell__ft">
                        </div>
                    </a>
                </div>
            </div>
        );
    }
}

RepoAbortedTasksApp.propTypes = {
    aborted_tasks: PropTypes.shape({
        collected_time: PropTypes.string,
        status_blob_id: PropTypes.number,
        tasks: PropTypes.arrayOf(PropTypes.shape({
            children: PropTypes.array,
            name: PropTypes.string,
            'node_path': PropTypes.string,
            'node_type': PropTypes.number,
            path: PropTypes.string,
            status: PropTypes.string
        })),
        'update_time': PropTypes.string
    })
};

function mapStateToProps(state){
    return {
        aborted_tasks: state.operation_system.repo.aborted_tasks
    }
}

export default connect(mapStateToProps)(RepoAbortedTasksApp)