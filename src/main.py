# -*- encoding: utf8 -*-
"""
demo 工具
功能: 检查 xxx 场景下的 xxx 问题
用法: python3 main.py

本地调试步骤:
1. 添加环境变量: export SOURCE_DIR="xxx/src_dir"
2. 添加环境变量: export TASK_REQUEST="xxx/task_request.json"
3. 按需修改task_request.json文件中各字段的内容
4. 命令行cd到项目根目录,执行命令:  python3 src/main.py
"""

import os
import sys
import json
import argparse
import subprocess
import typing


class DemoTool(object):
    def __parse_args_get_command(self):
        """
        解析命令行参数
        :return:
        """
        argparser = argparse.ArgumentParser()
        subparsers = argparser.add_subparsers(dest="command", help="Commands")
        # 检查在当前机器环境是否可用
        subparsers.add_parser("check", help="检查在当前机器环境是否可用")
        # 执行代码扫描
        subparsers.add_parser("scan", help="执行代码扫描")
        return argparser.parse_args().command

    """demo tool"""

    def __get_task_params(self) -> typing.Dict:
        """
        获取需要任务参数
        :return:
        """
        task_request_file = typing.cast(str, os.environ.get("TASK_REQUEST"))

        with open(task_request_file, "r") as rf:
            task_request = json.load(rf)

        task_params = task_request["task_params"]

        return task_params

    def __get_dir_files(self, root_dir, want_suffix=""):
        """
        在指定的目录下,递归获取符合后缀名要求的所有文件
        :param root_dir:
        :param want_suffix:
                    str|tuple,文件后缀名.单个直接传,比如 ".py";多个以元组形式,比如 (".h", ".c", ".cpp")
                    默认为空字符串,会匹配所有文件
        :return: list, 文件路径列表
        """
        files = set()
        for dirpath, _, filenames in os.walk(root_dir):
            for f in filenames:
                if f.lower().endswith(want_suffix):
                    fullpath = os.path.join(dirpath, f)
                    files.add(fullpath)
        files = list(files)
        return files

    def __format_str(self, text):
        """
        格式化字符串
        :param text:
        :return:
        """
        text = text.strip()
        if isinstance(text, bytes):
            text = text.decode("utf-8")
        return text.strip("'\"")

    def __run_cmd(self, cmd_args):
        """
        执行命令行
        """
        print("[run cmd] %s" % " ".join(cmd_args))
        p = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()
        stdoutput = self.__format_str(stdoutput)
        erroutput = self.__format_str(erroutput)
        if erroutput:
            print(">> stderr: %s" % erroutput)
        return stdoutput, erroutput

    def __get_include_exclude_paths(self, task_params) -> typing.Tuple[list, list]:
        wildcard_include_paths = task_params["path_filters"].get("inclusion", [])
        wildcard_exclude_paths = task_params["path_filters"].get("exclusion", [])
        regex_include_paths = task_params["path_filters"].get("re_inclusion", [])
        regex_exlucde_paths = task_params["path_filters"].get("re_exclusion", [])
        return (
            wildcard_exclude_paths + regex_exlucde_paths,
            wildcard_include_paths + regex_include_paths,
        )

    def __scan(self):
        """
        扫码代码
        """
        # 代码目录直接从环境变量获取
        source_dir = os.environ.get("SOURCE_DIR", None)
        print("[debug] source_dir: %s" % source_dir)
        if not source_dir:
            return

        # 其他参数从task_request.json文件获取
        task_params = self.__get_task_params()

        # 按需获取环境变量
        print("- * - * - * - * - * - * - * - * - * - * - * - * -* -* -* -* -* -* -")
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
        # 查看python版本
        print("[debug] 查看python version")
        sp = subprocess.Popen(["python", "--version"])
        sp.wait()
        print("- * - * - * - * - * - * - * - * - * - * - * - * -* -* -* -* -* -* -")
        # 获取过滤路径
        # path_filters = self.__get_path_filters(task_params)
        path_filters = self.__get_include_exclude_paths(task_params)
        print("- * - * - * - * - * - * - * - * - * - * - * - * -* -* -* -* -* -* -")

        # ------------------------------------------------------------------ #
        # 获取需要扫描的文件列表
        # 此处获取到的文件列表,已经根据项目配置的过滤路径过滤
        # 增量扫描时，从SCAN_FILES获取到的文件列表与从DIFF_FILES获取到的相同
        # ------------------------------------------------------------------ #
        scan_files_env = os.getenv("SCAN_FILES")
        if scan_files_env and os.path.exists(scan_files_env):
            with open(scan_files_env, "r") as rf:
                scan_files = json.load(rf)
                print("[debug] files to scan: %s" % len(scan_files))

        # ------------------------------------------------------------------ #
        # 增量扫描时,可以通过环境变量获取到diff文件列表,只扫描diff文件,减少耗时
        # 此处获取到的diff文件列表,已经根据项目配置的过滤路径过滤
        # ------------------------------------------------------------------ #
        # 从 DIFF_FILES 环境变量中获取增量文件列表存放的文件(全量扫描时没有这个环境变量)
        diff_file_env = os.environ.get("DIFF_FILES")
        if diff_file_env and os.path.exists(
            diff_file_env
        ):  # 如果存在 DIFF_FILES, 说明是增量扫描, 直接获取增量文件列表
            with open(diff_file_env, "r") as rf:
                diff_files = json.load(rf)
                print("[debug] get diff files: %s" % diff_files)

        # todo: 此处需要自行实现工具逻辑,输出结果,存放到result列表中

        # step
        # 获取需要检测的规则
        rules = task_params.get("rules", [])
        # ------

        # step
        # 获取可执行工具路径
        tool_cmd = self.__get_tool_cmd()
        # ------

        # step
        # 构造分析配置文件
        rule_name_prefix = "report"
        example_config_file = os.path.join(os.getcwd(), "config", "pyrightconfig.json")
        with open(example_config_file, "r") as f:
            config_dict: typing.Dict[str, typing.Union[list, str]] = json.loads(
                f.read()
            )
            # 启用规则，关闭未选用的规则
            for rule_name in config_dict.keys():
                if not rule_name.startswith(rule_name_prefix):
                    continue
                if rule_name not in rules:
                    config_dict[rule_name] = "none"
            # 路径排除
            config_dict["exclude"], config_dict["include"] = path_filters

            # 指定待分析项目所使用的python版本
            if os.environ.get("PYRIGHT_PYTHONVERSION"):
                config_dict["pythonVersion"] = os.environ["PYRIGHT_PYTHONVERSION"]

        config_file = os.path.join(source_dir, "toolpyrightconfig.json")
        with open(config_file, "w") as f:
            # 写入到source_dir下的配置文件中
            f.write(json.dumps(config_dict))
        # ------

        # step
        # 调用工具执行分析
        try:
            stdout, _ = self.__run_cmd(
                [tool_cmd, "-p", config_file, "--outputjson", source_dir]
            )
            pyright_result_dict = json.loads(stdout)
        except Exception as err:
            print(f"[error]: pyright工具执行分析出错：{err}")
            return
        # ------

        # step
        # 解析分析结果，输出到result.json
        issues_items = pyright_result_dict.get("generalDiagnostics", [])
        result_list = []
        for item in issues_items:
            rule = item.get("rule")
            if not rule:
                continue
            if rule not in rules:
                continue
            result_list.append(
                dict(
                    path=item["file"],
                    line=item["range"]["start"]["line"],
                    column=item["range"]["start"]["character"],
                    msg=item["message"],
                    rule=rule,
                    refs=[],
                )
            )
        with open("result.json", "w") as fp:
            json.dump(result_list, fp, indent=2)
        # ------

    def __get_tool_cmd(self) -> str:
        """
        执行
        """
        platform = sys.platform
        _gen_cmd = lambda file_name: os.path.join(os.getcwd(), "bin", file_name)
        tool_path = ""
        if platform == "win32":
            tool_path = _gen_cmd("pyright-win.exe")
        elif platform == "darwin":
            tool_path = _gen_cmd("pyright-mac")
        elif platform == "linux" or platform == "linux2":
            tool_path = _gen_cmd("pyright-linux")
        return tool_path

    def __check_usable(self) -> bool:
        """
        检查工具在当前机器环境下是否可用
        """
        tool_cmd = self.__get_tool_cmd()
        if not tool_cmd:
            return False
        try:
            sys.stdout, sys.stderr = self.__run_cmd([tool_cmd, "--version"])
        except Exception as err:
            print("tool is not usable: %s" % str(err))
            return False
        return True

    def run(self):
        command = self.__parse_args_get_command()
        if command == "check":
            # 检测工具
            print(">> check tool usable ...")
            is_usable = self.__check_usable()
            result_path = "check_result.json"
            if os.path.exists(result_path):
                os.remove(result_path)
            with open(result_path, "w") as fp:
                data = {"usable": is_usable}
                json.dump(data, fp)
                
        elif command == "scan":
            print(">> start to scan code ...")
            self.__scan()
        else:
            print("[Error] need command(check, scan) ...")


if __name__ == "__main__":
    DemoTool().run()
