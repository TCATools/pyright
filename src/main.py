# -*- encoding: utf8 -*-
"""
demo 工具
功能: 检查 xxx 场景下的 xxx 问题
用法: python3 main.py

本地调试步骤:
1. 构造环境变量:  export SOURCE_DIR="/src/benson_test"
2. 按需修改task_request.json文件中各字段的内容
3. 将task_request.json文件绝对路径添加到环境变量中: export TASK_REQUEST="xxxx/task_request.json"
4. 命令行cd到项目根目录,执行命令:  python3 src/main.py
"""

# 2019-08-19    bensonqin    created

import os
import json
import subprocess


class DemoTool(object):
    """demo tool"""
    def __get_task_params(self):
        """
        获取需要任务参数
        :return:
        """
        task_request_file = os.environ.get("TASK_REQUEST")

        with open(task_request_file, 'r') as rf:
            task_request = json.load(rf)

        task_params = task_request["task_params"]

        return task_params

    def run(self):
        """

        :return:
        """
        # 代码目录直接从环境变量获取
        source_dir = os.environ.get("SOURCE_DIR", None)
        print("[debug] source_dir: %s" % source_dir)

        # 其他参数从task_request.json文件获取
        task_params = self.__get_task_params()
        # 环境变量
        envs = task_params["envs"]
        print("[debug] envs: %s" % envs)
        # 前置命令
        pre_cmd = task_params["pre_cmd"]
        print("[debug] pre_cmd: %s" % pre_cmd)
        # 编译命令
        build_cmd = task_params["build_cmd"]
        print("[debug] build_cmd: %s" % build_cmd)
        # 查看path环境变量
        print("[debug] path: %s" % os.environ.get("PATH"))
        # 查看path环境变量
        print("[debug] 查看python version")
        sp = subprocess.Popen(["python", "--version"])
        sp.wait()

        # todo: 此处实现工具逻辑,输出结果,存放到result字典中

        # demo结果
        demo_path = os.path.join(source_dir,"run.py")
        result = [
            {
                "path": demo_path,
                'line': 2,
                'column': 3,
                'msg': "This is a testcase.",
                'rule': "new_rule_demo"
            }
        ]

        # 输出结果到指定的json文件
        with open("result.json", "w") as fp:
            json.dump(result, fp, indent=2)


if __name__=='__main__':
    print("-- start run tool ...")
    DemoTool().run()
    print("-- end ...")