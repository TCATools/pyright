# Demo 工具示例

功能: 检查 xxx 场景下的 xxx 问题

## 本地调试步骤:

本地调试步骤:
1. 添加环境变量: `export SOURCE_DIR="xxx/src_dir"`
2. 添加环境变量: `export TASK_REQUEST="xxx/task_request.json"`
3. 按需修改`task_request.json`文件中各字段的内容:
   - `checktool`中的`scm_url`、`run_cmd`
   - `rule_list`中的工具规则信息（可选，如果工具中有用到规则信息的话）
4. 命令行`cd`到项目根目录,执行命令:  `python3 src/main.py`

## CodeDog工具配置示例：

* `GIT仓库地址`: http://xxx/xxx/demo-tool.git
* `执行命令`: python src/main.py
* `环境变量`: python_version=3
