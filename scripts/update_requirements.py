import os
import subprocess

def update_requirements():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    requirements_file = os.path.join(project_root, "requirements.txt")
    
    try:
        with open(requirements_file, "w") as f:
            subprocess.check_call(["pip", "freeze"], stdout=f)
        print(f"{requirements_file} 文件已更新！")
    except subprocess.CalledProcessError as e:
        print(f"更新 {requirements_file} 时出错: {e}")

if __name__ == "__main__":
    update_requirements()
