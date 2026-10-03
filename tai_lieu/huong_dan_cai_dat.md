# Hướng Dẫn Cài Đặt Chi Tiết

## 1. Yêu cầu môi trường

- Hệ điều hành: Windows 10/11, macOS, hoặc Linux.
- Python 3.11 hoặc 3.12 (khuyến nghị).
- XAMPP (bao gồm MySQL/MariaDB + phpMyAdmin).
- Webcam (để sử dụng chức năng điểm danh/đăng ký khuôn mặt).
- Tối thiểu 4 GB RAM trống (nếu dùng InsightFace/YOLO thay vì bản dự phòng OpenCV).

## 2. Cài đặt XAMPP

1. Tải XAMPP tại: https://www.apachefriends.org/
2. Cài đặt theo hướng dẫn mặc định của trình cài đặt.
3. Mở **XAMPP Control Panel**.
4. Nhấn **Start** ở dòng **MySQL** (bắt buộc).
5. Nhấn **Start** ở dòng **Apache** (khuyến nghị, để dùng được phpMyAdmin qua trình duyệt).
6. Kiểm tra truy cập: mở trình duyệt tới địa chỉ phpMyAdmin của máy bạn (thường hiển thị ngay trong XAMPP Control Panel sau khi Start Apache).

## 3. Lấy mã nguồn dự án

Giải nén file `du_an_diem_danh_khuon_mat.zip` vào một thư mục bất kỳ, ví dụ:
```
C:\du_an\du_an_diem_danh_khuon_mat\      (Windows)
~/du_an/du_an_diem_danh_khuon_mat/       (macOS/Linux)
```

## 4. Tạo môi trường ảo Python (khuyến nghị)

```bash
cd du_an_diem_danh_khuon_mat
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

## 5. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

> **Lưu ý:** `insightface`, `onnxruntime`, `ultralytics` là các thư viện AI
> nâng cao, có thể cài chậm hoặc thất bại trên một số máy (đặc biệt máy
> cấu hình thấp hoặc Python phiên bản quá mới/cũ). Nếu ba thư viện này cài
> thất bại, **không sao cả** — chương trình vẫn chạy đầy đủ chức năng nhờ
> cơ chế dự phòng bằng OpenCV. Bạn có thể bỏ qua bằng cách xóa 3 dòng đó
> khỏi `requirements.txt` trước khi `pip install` nếu muốn cài nhanh hơn.

## 6. Cấu hình file `.env`

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Mở file `.env` bằng trình soạn thảo văn bản, kiểm tra các giá trị mặc định:
```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=diem_danh_khuon_mat
DB_USER=root
DB_PASSWORD=
```

Nếu máy bạn đã đặt mật khẩu cho tài khoản `root` của MySQL (không phải mặc
định của XAMPP), hãy điền mật khẩu đó vào `DB_PASSWORD`.

## 7. Khởi tạo cơ sở dữ liệu

**Cách 1 — Tự động (khuyến nghị):**
```bash
python cai_dat.py
```
Script sẽ tự kiểm tra Python, thư viện, kết nối MySQL, tự tạo database
`diem_danh_khuon_mat`, tạo toàn bộ 14 bảng, nạp dữ liệu mẫu, và kiểm tra
model AI. Nếu tất cả các bước đều có dấu ✔, quá trình cài đặt hoàn tất.

**Cách 2 — Thủ công qua phpMyAdmin:**
Xem chi tiết trong `database/README.md`. Tóm tắt: mở phpMyAdmin → Import
→ chọn `database/schema.sql` → Thực hiện → Import tiếp
`database/du_lieu_mau.sql`.

## 8. Chạy chương trình

```bash
python run.py
```

Đăng nhập bằng một trong các tài khoản mẫu:

| Vai trò | Tên đăng nhập | Mật khẩu |
|---|---|---|
| Quản trị viên | `admin` | `Admin@123` |
| Giảng viên | `giangvien01` | `GiangVien@123` |
| Sinh viên | `sinhvien01` | `SinhVien@123` |

## 9. Xử lý sự cố thường gặp

### "Không thể kết nối đến MySQL"
- Kiểm tra XAMPP Control Panel: dòng MySQL phải có màu xanh (đang chạy).
- Kiểm tra cổng 3306 không bị chương trình khác chiếm dụng (ví dụ một
  MySQL Server cài riêng đang chạy cùng cổng).
- Chạy lại: `python cai_dat.py`.

### "ModuleNotFoundError: No module named 'PySide6'" (hoặc thư viện khác)
- Đảm bảo đã kích hoạt đúng môi trường ảo (`.venv`) trước khi chạy.
- Chạy lại: `pip install -r requirements.txt`.

### Camera không mở được / màn hình đen
- Kiểm tra `CHI_SO_CAMERA_MAC_DINH` trong `.env` (thường là `0`; nếu máy
  có nhiều camera, thử `1`, `2`...).
- Đảm bảo không có phần mềm khác đang chiếm dụng webcam.
- Kiểm tra quyền truy cập camera của hệ điều hành cho Python/Terminal.

### Đăng ký khuôn mặt báo "Không phát hiện được khuôn mặt"
- Đảm bảo đủ ánh sáng, khuôn mặt nhìn thẳng vào camera, không đeo khẩu
  trang/kính râm.
- Nếu hệ thống đang dùng phương pháp dự phòng OpenCV Haar Cascade (xem
  thông báo trong `cai_dat.py`), độ chính xác thấp hơn InsightFace — hãy
  thử chụp lại ở góc thẳng, khoảng cách 40–60 cm.

## 10. Chạy bộ kiểm thử (dành cho phát triển)

```bash
python -m pytest kiem_thu/ -v
```

Bộ kiểm thử cần MySQL đang chạy và database đã được khởi tạo. Nên dùng
một database thử nghiệm riêng (đổi `DB_NAME` trong `.env`) để tránh ảnh
hưởng dữ liệu thật.
