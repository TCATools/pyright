# -*- encoding: utf8 -*-

import os
import sys
import json
import typing
import argparse
import subprocess

class DemoTool(object):
    def __parse_args_get_command(self):
        """获取命令行参数"""
        argparser = argparse.ArgumentParser()
        subparsers = argparser.add_subparsers(dest="command", help="Commands")
        # 检查在当前机器环境是否可用
        subparsers.add_parser("check", help="检查在当前机器环境是否可用")
        # 执行代码扫描
        subparsers.add_parser("scan", help="执行代码扫描")
        return argparser.parse_args().command


    def __get_task_params(self) -> typing.Dict:
        """获取需要任务参数"""
        task_request_file = typing.cast(str, os.environ.get("TASK_REQUEST"))
        with open(task_request_file, "r") as rf:
            task_request = json.load(rf)
        task_params = task_request["task_params"]
        print(f"[pyright-info]获取到的任务参数: {task_params}")
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
        """格式化字符串"""
        text = text.strip()
        if isinstance(text, bytes):
            text = text.decode("utf-8")
        return text.strip("'\"")

    def __run_cmd(self, cmd_args):
        """执行命令行"""

        print("[run cmd] %s" % " ".join(cmd_args[:3]))
        p = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutput, erroutput) = p.communicate()
        stdoutput = self.__format_str(stdoutput)
        erroutput = self.__format_str(erroutput)
        if erroutput:
            print("[pyright-error] >> stderr: %s" % erroutput)
        return stdoutput, erroutput

    def __scan(self):
        """扫描入口"""
        # 代码目录直接从环境变量获取
        source_dir = os.environ.get("SOURCE_DIR", None)
        print("[pyright-debug] source_dir: %s" % source_dir)
        if not source_dir:
            return

        # 其他参数从task_request.json文件获取
        task_params = self.__get_task_params()

        # 按需获取环境变量
        print("- * - * - * - * - * - * - * - * - * - * - * - * -* -* -* -* -* -* -")
        envs = task_params["envs"]
        print("[pyright-debug] envs: %s" % envs)
        # 前置命令
        pre_cmd = task_params["pre_cmd"]
        print("[pyright-debug] pre_cmd: %s" % pre_cmd)
        # 编译命令
        build_cmd = task_params["build_cmd"]
        print("[pyright-debug] build_cmd: %s" % build_cmd)
        # 查看path环境变量
        print("[pyright-debug] path: %s" % os.environ.get("PATH"))

        print("- * - * - * - * - * - * - * - * - * - * - * - * -* -* -* -* -* -* -")

        # ------------------------------------------------------------------ #
        # 获取需要扫描的文件列表
        # 此处获取到的文件列表,已经根据项目配置的过滤路径过滤
        # 增量扫描时，从SCAN_FILES获取到的文件列表与从DIFF_FILES获取到的相同
        # ------------------------------------------------------------------ #
        scan_files_env = os.getenv("SCAN_FILES")
        if scan_files_env and os.path.exists(scan_files_env):
            with open(scan_files_env, "r") as rf:
                need_scan_files = typing.cast(typing.List[str],json.load(rf))
        else:
            need_scan_files = self.__get_dir_files(source_dir, ".py")
        print("[pyright-debug] files to scan: %s" % len(need_scan_files))

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
                print("[pyright-debug] get diff files: %s" % diff_files)
                need_scan_files = diff_files
        print(f"[pyright-debug] need scan files: {len(need_scan_files)}")

        
        # step
        # 获取需要检测的规则
        rules = task_params.get("rules", [])
        # ------

        # step
        # 获取可执行工具路径
        tool_cmd = self.__get_tool_cmd()
        # ------

        # step
        # 构造配置文件
        config_file = self.__gen_config_file(source_dir, rules)
        # ------

        # step
        # 调用工具执行分析
        self.__execute_tool_return_result(rules, tool_cmd, config_file, need_scan_files)
        # ------

        # step
        self.__final_step(config_file)
        # ------
    

    def __final_step(self, config_file):
        if os.path.exists(config_file):
            os.remove(config_file)
        return
        
    def __format_result_dict(self, result_dict: typing.Dict[typing.Any, typing.Any], rules: typing.List[str]):
        issues_items = result_dict.get("generalDiagnostics", [])
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
                    line=int(item["range"]["start"]["line"]) + 1,
                    column=int(item["range"]["start"]["character"]) + 1,
                    msg=item["message"],
                    rule=rule,
                    refs=[],
                )
            )
            return result_list
            

    def __execute_tool_return_result(self, rules, tool_cmd: str, config_file: str, scan_files: typing.List[str]):
        with open("result.json", "w") as fp:
            try:
                stdout, _ = self.__run_cmd(
                    [tool_cmd, "-p", config_file, *scan_files, "--outputjson"]
                )
                result_dict = json.loads(stdout)
            except Exception as err:
                print(f"[pyright-error]: pyright工具执行分析出错：{err}")
                result_dict = {}
            result_list = self.__format_result_dict(result_dict, rules)
            json.dump(result_list, fp, indent=2)


    def __gen_config_file(self, source_dir: str, rules: typing.List[str]) -> str:
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

            # 指定待分析项目所使用的python版本
            if os.environ.get("PYRIGHT_PYTHONVERSION"):
                config_dict["pythonVersion"] = os.environ["PYRIGHT_PYTHONVERSION"]

        config_file = os.path.join(source_dir, "toolpyrightconfig.json")
        with open(config_file, "w") as f:
            # 写入到source_dir下的配置文件中
            f.write(json.dumps(config_dict))
        print(f"[pyright-info]: 生成的配置内容: {config_dict}")
        return config_file

    def __get_tool_cmd(self) -> str:
        """根据系统类型获取工具路径"""
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
        """检查工具是否可以正确使用"""
        tool_cmd = self.__get_tool_cmd()
        if not tool_cmd:
            return False
        try:
            sys.stdout, sys.stderr = self.__run_cmd([tool_cmd, "--version"])
        except Exception as err:
            print("[pyright-error] tool is not usable: %s" % str(err))
            return False
        return True

    def run(self):
        command = self.__parse_args_get_command()
        if command == "check":
            # 检查工具是否可用
            print("[pyright-info] >> check tool usable ...")
            is_usable = self.__check_usable()
            result_path = "check_result.json"
            if os.path.exists(result_path):
                os.remove(result_path)
            with open(result_path, "w") as fp:
                data = {"usable": is_usable}
                json.dump(data, fp)
        elif command == "scan":
            # 执行扫描分析任务
            print("[pyright-info] >> start to scan code ...")
            self.__scan()
        else:
            print("[pyright-error] need command(check, scan) ...")


if __name__ == "__main__":
    DemoTool().run()
