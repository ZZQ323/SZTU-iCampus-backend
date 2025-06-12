@echo off
echo 正在清理缓存文件...

:: 删除所有 .pyc 文件
del /s /q *.pyc

:: 删除所有 __pycache__ 目录
rmdir /s /q __pycache__
rmdir /s /q app\__pycache__
rmdir /s /q app\api\__pycache__
rmdir /s /q app\api\v1\__pycache__
rmdir /s /q app\api\v1\endpoints\__pycache__
rmdir /s /q app\core\__pycache__
rmdir /s /q app\crud\__pycache__
rmdir /s /q app\db\__pycache__
rmdir /s /q app\models\__pycache__
rmdir /s /q app\schemas\__pycache__
rmdir /s /q alembic\__pycache__
rmdir /s /q alembic\versions\__pycache__

:: 删除数据库文件
del /f /q sztu_icampus.db

echo 清理完成！
pause 