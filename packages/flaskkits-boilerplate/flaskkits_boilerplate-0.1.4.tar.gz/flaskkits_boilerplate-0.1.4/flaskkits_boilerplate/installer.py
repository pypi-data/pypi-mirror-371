import platform
import os
import subprocess
import sys

def install_python_requirements(project_path):
    print("Installing Python dependencies...")
    req_file = os.path.abspath(os.path.join(project_path, "requirements.txt"))
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file], check=True)

def install_npm_dependencies(project_path):
    print("Installing Tailwind CSS via npm...")
    
    # Cek OS
    current_os = platform.system()
    if current_os == "Windows":
        # Windows biasanya butuh shell=True untuk npm
        subprocess.run("npm install", cwd=project_path, shell=True, check=True)
    else:
        # Linux / macOS
        subprocess.run(["npm", "install"], cwd=project_path, check=True)