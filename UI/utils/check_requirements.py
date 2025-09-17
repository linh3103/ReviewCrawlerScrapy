import sys
import subprocess
import pkg_resources

def check_and_install_requirements():
    """
    Đọc file requirements.txt, kiểm tra các gói đã cài, và cài đặt nếu thiếu.
    """
    print(">>> Checking for required packages...")
    
    try:
        with open('requirements.txt', 'r') as f:
            required_packages = f.read().splitlines()
    except FileNotFoundError:
        print("!!! ERROR: requirements.txt not found. Cannot check dependencies.")
        return

    # Lọc ra các dòng trống hoặc comment
    required_packages = [pkg for pkg in required_packages if pkg and not pkg.startswith('#')]
    
    # Lấy danh sách các gói đã được cài đặt trong môi trường hiện tại
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    
    missing_packages = []
    for required in required_packages:
        try:
            # Phân tích yêu cầu (ví dụ: 'requests>=2.0' -> 'requests')
            req = pkg_resources.Requirement.parse(required)
            if req.project_name.lower() not in installed_packages:
                missing_packages.append(required)
        except pkg_resources.RequirementParseError:
            print(f"!!! WARNING: Could not parse requirement: {required}")

    if not missing_packages:
        print(">>> All required packages are already installed.")
    else:
        print(f">>> Found {len(missing_packages)} missing packages: {', '.join(missing_packages)}")
        print(">>> Attempting to install missing packages...")
        
        # Sử dụng sys.executable để đảm bảo dùng đúng 'pip' của môi trường hiện tại
        python_executable = sys.executable
        try:
            # Chạy lệnh pip install cho toàn bộ file requirements
            subprocess.check_call([python_executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print(">>> Successfully installed/updated packages.")
        except subprocess.CalledProcessError as e:
            print(f"!!! ERROR: Failed to install packages. Please run 'pip install -r requirements.txt' manually.")
            print(f"!!! Pip Error: {e}")
            # Thoát chương trình nếu không cài được thư viện cần thiết
            sys.exit(1)

# --- CHẠY HÀM KIỂM TRA NGAY LẬP TỨC ---
check_and_install_requirements()