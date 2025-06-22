@echo off
echo 🚀 SZTU-iCampus Mock数据生成器
echo ==========================================
echo.
echo 📍 当前位置: data-service目录
echo 🎯 目标: 生成完整的校园测试数据
echo.
echo 📊 预计生成数据量:
echo   - 13个学院
echo   - 78个专业
echo   - 1,248个班级  
echo   - 15,600个学生
echo   - 1,040个教师
echo   - 20个管理员
echo.
echo ⚠️  注意: 请确保已安装Python环境和所需依赖
echo.
pause

python run_mock_generation.py

echo.
echo 按任意键退出...
pause > nul 