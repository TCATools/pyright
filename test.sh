export SOURCE_DIR="/xxx/xxx"
export TASK_REQUEST="task_request.json"

echo "- * - * - * - * - * - * - * - * - * - * - * - * -* -* -* -* -* -* -"
python3 src/main.py check

echo "- * - * - * - * - * - * - * - * - * - * - * - * -* -* -* -* -* -* -"
python3 src/main.py scan
echo "- * - * - * - * - * - * - * - * - * - * - * - * -* -* -* -* -* -* -"
