# LedOn

Dùng mã Python điều khiển đèn 4 Led bật tắt.

## Các thành phần

- Cấu hình FPGA trên Vivado để tạo khối **AXI GPIO** điều khiển LED.\
  _Lưu ý: Dự án sử dụng cấu hình mặc định trong PYNQ-Z2 board file. Vì vậy các chân PIN của 4 Led không được đính nghĩa chiều dữ liệu ra hay vào, và buộc phải thiết lập bằng mã Python._
- Lập trình Python để gửi giá trị phù hợp tới địa chỉ MMIO của **AXI GPIO**.

## Mã Python

[Mã nguồn](./LedOn.ipynb)
