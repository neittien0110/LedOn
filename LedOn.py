from pynq import Overlay
import sys

# Nạp Overlay
ol = Overlay("../LedOn/LedOn.bit")
leds = ol.axi_gpio_0

# Ép hướng thành Output (Ghi vào thanh ghi TRI tại offset 0x04)
leds.mmio.write(0x04, 0x0)

# Lấy giá trị từ tham số dòng lệnh (ví dụ: python3 control_led.py 15)
value = int(sys.argv[1]) if len(sys.argv) > 1 else 0

# Ghi dữ liệu
leds.write(0, value)
print(f"✅ Đã ghi giá trị {value} vào LED!")