import os
import subprocess
import sys

def install_dependencies():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    requirements_file = os.path.join(project_root, "requirements.txt")
    
    if os.path.exists(requirements_file):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "-r", requirements_file])
            print("依赖安装和更新完成！")
        except subprocess.CalledProcessError as e:
            print(f"安装或更新依赖时出错: {e}")
    else:
        print(f"未找到 {requirements_file} 文件，请确保它存在于项目根目录。")

def update_requirements():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    requirements_file = os.path.join(project_root, "requirements.txt")
    
    if os.path.exists(requirements_file):
        try:
            # 使用 pip freeze 过滤出 requirements.txt 中的依赖
            installed_packages = subprocess.check_output(
                [sys.executable, "-m", "pip", "freeze"], text=True
            ).splitlines()
            
            with open(requirements_file, "r") as f:
                required_packages = f.read().splitlines()
            
            # 仅保留 requirements.txt 中列出的依赖及其版本
            updated_packages = [
                pkg for pkg in installed_packages
                if any(pkg.startswith(req.split("==")[0]) for req in required_packages)
            ]
            
            with open(requirements_file, "w") as f:
                f.write("\n".join(updated_packages) + "\n")
            
            print(f"已将当前工程所需的依赖更新到 {requirements_file} 文件中！")
        except subprocess.CalledProcessError as e:
            print(f"更新 {requirements_file} 文件时出错: {e}")
    else:
        print(f"未找到 {requirements_file} 文件，请确保它存在于项目根目录。")

if __name__ == "__main__":
    install_dependencies()
    update_requirements()
