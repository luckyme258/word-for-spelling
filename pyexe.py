import subprocess
import sys
import shutil
import os

def clean_old_files(target_script):
    """清理旧的打包文件，避免残留配置干扰"""
    # 要删除的文件/文件夹列表
    clean_items = [
        "dist",          # 旧的输出目录
        "build",         # 旧的临时构建目录
        f"{target_script}.spec"  # 旧的打包配置文件
    ]
    
    for item in clean_items:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item, ignore_errors=True)
                print(f"已删除旧目录: {item}")
            else:
                os.remove(item)
                print(f"已删除旧文件: {item}")

def package_application():
    """完整的应用打包逻辑，针对单词拼写练习应用优化"""
    # 1. 配置核心参数（主程序文件名）
    target_script = "exam_choose_dir.py"  # 确保与你的主程序文件名一致
    command = [
        "pyinstaller",
        "--onefile",                # 打包成单个exe
        "--noconsole",              # 隐藏控制台窗口
        "--strip",                  # 减小exe体积
        "--clean",                  # 清理临时文件
        # 收集音频相关依赖
        "--collect-all", "pygame",
        # 收集Windows标题栏自定义依赖
        "--collect-all", "win32gui",
        # 排除无用模块，减小体积
        "--exclude-module", "tkinter.test",
        "--exclude-module", "tkinter.tix",
        "--exclude-module", "pygame.tests",
        "--exclude-module", "win32com.client",
        # 隐藏导入确保兼容性
        "--hidden-import", "pygame.mixer",
        "--hidden-import", "win32gui",
        # 主程序入口
        target_script
    ]
    
    try:
        # 2. 先清理旧文件
        clean_old_files(target_script)
        
        # 3. 执行打包命令
        print(f"开始打包 {target_script}...")
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        
        # 4. 打包成功后的提示
        print("="*50)
        print("打包完成！✅")
        print(f"生成的exe路径：dist/{target_script.replace('.py', '.exe')}")
        print("提示：若运行闪退，可删除--noconsole参数重新打包查看错误")
        print("="*50)
        print("打包日志：")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"打包失败！错误代码: {e.returncode}")
        print("错误详情：")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("错误：未找到pyinstaller！请先执行：pip install pyinstaller")
        return False
    except Exception as e:
        print(f"未知错误：{str(e)}")
        return False

if __name__ == "__main__":
    success = package_application()
    sys.exit(0 if success else 1)
    
