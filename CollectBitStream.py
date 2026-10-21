import os
import time
from pathlib import Path
import paramiko
from datetime import datetime

# === CẤU HÌNH KẾT NỐI PYNQ ===
PYNQ_IP = "192.168.2.99"
PYNQ_USER = "xilinx"
PYNQ_PASS = "xilinx"
PYNQ_BASE_DIR = "/home/xilinx"  # Các file bit và hwh sẽ được đẩy lên thư mục con trùng tên dự án, trong thư mục này
# =============================
BIT_FILE = "mainsystem_wrapper.bit"
HWH_FILE = "mainsystem.hwh"
OTHER_FILES = ["LedOn.py", "runme.sh"]
COMMANDS = [
    "source /etc/profile.d/pynq_venv.sh && echo xilinx | sudo -S -E python3 LedOn.py 1"
]
COMMANDS = []

# Thư mục dự án trên TUL PYNQ Z2
remote_project_dir = ""
# Thư mục dự án hiện thời trên laptop
current_dir = ""
# Tên dự án, lấy theo thư mục hiện thời
project_name = ""

def init():
    global current_dir, project_name, remote_project_dir
    current_dir = Path.cwd()
    # Thư mục lưu trữ trên Dev-Kit, lấy theo đúng thư mục dự án hiện tại
    project_name = current_dir.name
    remote_project_dir = f"{PYNQ_BASE_DIR}/{project_name}"    

    print(f"🚀 Dự án: {project_name}")
    print("-" * 45)


def get_file_info(file_path):
    """Lấy thời điểm sửa đổi và khoảng thời gian so với hiện tại"""
    mtime = os.path.getmtime(file_path)
    mod_time = datetime.fromtimestamp(mtime)
    diff = datetime.now() - mod_time
    
    if diff.total_seconds() < 60:
        time_str = f"{int(diff.total_seconds())} giây trước"
    else:
        time_str = f"{int(diff.total_seconds() // 60)} phút trước"
        
    return mod_time.strftime("%Y-%m-%d %H:%M:%S"), time_str

def collect_and_upload():   
    # Đường dẫn file nguồn trong cấu trúc Vivado
    bit_src = current_dir / f"{project_name}.runs" / "impl_1" / BIT_FILE
    hwh_src = current_dir / f"{project_name}.gen" / "sources_1" / "bd" / "mainsystem" / "hw_handoff" / HWH_FILE

    # Khởi tạo mảng kiểm tra cơ bản
    files_to_check = [("BIT", bit_src), ("HWH", hwh_src)]
    
    # Đọc mảng OTHER_FILES và thêm vào mảng kiểm tra
    for file_name in OTHER_FILES:
        files_to_check.append(("---", current_dir / file_name))

    all_exists = True

    for label, path in files_to_check:
        if path.exists():
            m_date, diff = get_file_info(path)
            print(f"📝 {label} found: {m_date} ({diff}) - {path.name}")
        else:
            print(f"❌ {label} NOT FOUND at: {path}")
            all_exists = False

    if not all_exists:
        print("\n⚠️ Dừng lại! Vui lòng kiểm tra lại các file nguồn.")
        input("\nBấm phím bất kì để kết thúc...")
        return

    try:
        print("-" * 45)
        print(f"📡 Đang kết nối tới PYNQ ({PYNQ_IP})...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(PYNQ_IP, username=PYNQ_USER, password=PYNQ_PASS)

        # Tạo thư mục dự án trên PYNQ
        ssh.exec_command(f"mkdir -p {remote_project_dir}")

        sftp = ssh.open_sftp()
        
        # Upload BIT
        print(f"📤 Uploading BIT... ", end="", flush=True)
        sftp.put(str(bit_src), f"{remote_project_dir}/{project_name}.bit")
        print("OK")

        # Upload HWH
        print(f"📤 Uploading HWH... ", end="", flush=True)
        sftp.put(str(hwh_src), f"{remote_project_dir}/{project_name}.hwh")
        print("OK")
        
        # Upload các file trong OTHER_FILES
        for file_name in OTHER_FILES:
            print(f"📤 Uploading {file_name}... ", end="", flush=True)
            sftp.put(str(current_dir / file_name), f"{remote_project_dir}/{file_name}")
            print("OK")

        sftp.close()
        
        print("-" * 45)
        print(f"✅ THÀNH CÔNG! File đã nằm tại: {remote_project_dir}")
        
        # Thực hiện các lệnh trong COMMANDS nếu có
        print("-" * 45)
        print(f"THỰC THI LỆNH TRÊN ARM CORE ngay lập tức")
        if COMMANDS:
            print("-" * 45)
            print("⚙️ THỰC THI LỆNH TRÊN KIT:")
            for cmd in COMMANDS:
                print(f"▶ Đang chạy: {cmd}")
                # Chuyển vào thư mục chứa file rồi mới thực thi lệnh
                full_cmd = f"cd {remote_project_dir} && {cmd}"
                stdin, stdout, stderr = ssh.exec_command(full_cmd)
                
                # Đọc output trả về từ kit
                out = stdout.read().decode().strip()
                err = stderr.read().decode().strip()
                
                if out:
                    print(f"[Kết quả]:\n{out}")
                if err:
                    print(f"[Lỗi]:\n{err}")

        ssh.close()
        
        print("-" * 45)
        print(f"💡 Trong Jupyter, bạn gọi: Overlay('{project_name}.bit')")

    except Exception as e:
        print(f"\n❌ LỖI TRUYỀN TẢI / THỰC THI: {e}")

    print("-" * 45)

def ssh_helper():
    print(f'Truy cập Dev Kit qua SSH:  ssh -t {PYNQ_USER}@{PYNQ_IP} "cd {remote_project_dir} && bash"')

if __name__ == "__main__":
    init()
    collect_and_upload()
    ssh_helper()
    input("Bấm phím bất kì để kết thúc...")