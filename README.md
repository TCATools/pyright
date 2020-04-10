demo 工具示例

功能: 检查 xxx 场景下的 xxx 问题

本地调试步骤:
1. 构造环境变量:  export SOURCE_DIR="/src/benson_test"
2. 按需修改task_request.json文件中各字段的内容
3. 命令行执行  python3 src/main.py

在CodeDog自定义工具配置以下信息：
1. GIT仓库地址: http://git.code.oa.com/codedog_group/demo-tool.git
2. 执行命令: python src/main.py
3. 环境变量: python_version=3

如有疑问,请咨询 bensonqin.