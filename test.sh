export SOURCE_DIR="/data/home/riverjjiang/vscode_remote_dir/simple-starlette/"
export TASK_REQUEST="task_request.json"
export PYRIGHT_PYTHONVERSION=3.8

echo "- * - * - *        - * - * - * - * - * - * - * - * - * -* -* -* -* -* -* -"
python3 src/main.py check

echo "- * - * - * - * - * - * - * - * - * - * - * - * -* -* -* -* -* -* -"
python3 src/main.py scan
echo "- * - * - * - * - * - * - * - * - * - * - * - * -* -* -* -* -* -* -"
