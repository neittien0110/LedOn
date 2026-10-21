#!/bin/bash
# Kích hoạt môi trường PYNQ
source /etc/profile.d/pynq_venv.sh

# Di chuyển hẳn vào thư mục chứa file bit trước khi chạy Python
cd /home/xilinx/LedOn

# Lúc này dùng đường dẫn tương đối trong Python sẽ hoạt động, để lấy file .bit và .hwh cho hợp
# Số thập phân 11 = 1011 ==> 3 đèn sáng, một đèn tăt
sudo -E python3 LedOn.py 11