# Hệ Thống Điểm Danh Sinh Viên Bằng Khuôn Mặt

Phần mềm desktop điểm danh sinh viên bằng nhận diện khuôn mặt (AI), xây
dựng bằng **Python + PySide6 + MySQL/MariaDB (XAMPP)**, chạy offline hoàn
toàn — không phụ thuộc bất kỳ API AI trả phí nào.

## Tính năng chính

- 🔐 Đăng nhập, phân quyền RBAC 3 vai trò (Quản trị viên / Giảng viên / Sinh viên), khóa tài khoản chống dò mật khẩu.
- 🏫 Quản lý Khoa, Lớp hành chính, Môn học, Lớp học phần, đăng ký sinh viên vào lớp.
- 🧑‍🎓 Quản lý hồ sơ Sinh viên / Giảng viên (không xóa vật lý sinh viên đã có lịch sử điểm danh).
- 🪪 Đăng ký khuôn mặt qua webcam, embedding được mã hóa trước khi lưu.
- 📷 Điểm danh tự động bằng khuôn mặt (có kiểm tra người thật — liveness detection), điểm danh thủ công, chống điểm danh trùng (ràng buộc UNIQUE ở CSDL).
- 📈 Báo cáo thống kê theo lớp/ngày/tháng/học kỳ, xuất Excel & PDF.
- 🗒️ Nhật ký hệ thống (audit log) đầy đủ, không ghi mật khẩu.
- ⚙️ Cấu hình động (ngưỡng nhận diện, chính sách khóa tài khoản...) chỉnh được ngay khi ứng dụng đang chạy.

## Công nghệ

Python 3.11/3.12 · PySide6 · OpenCV · YOLO (ultralytics) · InsightFace/ArcFace
· NumPy · SQLAlchemy · PyMySQL · bcrypt · openpyxl · ReportLab · Matplotlib ·
MySQL/MariaDB qua XAMPP.

> Nếu máy bạn không cài được `insightface`/`ultralytics`/`onnxruntime`
> (thường do cấu hình máy hoặc mạng), hệ thống **tự động chuyển sang
> phương pháp dự phòng bằng OpenCV** (Haar Cascade + HOG/Histogram) mà
> không cần chỉnh sửa gì — xem chi tiết ở `tai_lieu/kien_truc_he_thong.md`.

## Bắt đầu nhanh

```bash
# 1. Cài XAMPP, mở XAMPP Control Panel, Start MySQL (và Apache nếu muốn dùng phpMyAdmin)

# 2. Cài thư viện Python
pip install -r requirements.txt

# 3. Tạo file cấu hình
cp .env.example .env      # Windows: copy .env.example .env

# 4. Khởi tạo cơ sở dữ liệu (tự động tạo database + bảng + dữ liệu mẫu)
python cai_dat.py

# 5. Chạy chương trình
python run.py
```

Tài khoản mẫu: `admin` / `Admin@123` · `giangvien01` / `GiangVien@123` ·
`sinhvien01` / `SinhVien@123`.

Xem hướng dẫn chi tiết từng bước tại `HUONG_DAN_CAI_DAT.txt` hoặc
`tai_lieu/huong_dan_cai_dat.md`.

## Cấu trúc dự án

```
du_an_diem_danh_khuon_mat/
├── run.py, cai_dat.py, tao_co_so_du_lieu.py   # Script chạy chính
├── database/          # schema.sql, du_lieu_mau.sql (import qua phpMyAdmin)
├── app/
│   ├── cau_hinh/      # Đọc cấu hình .env
│   ├── co_so_du_lieu/ # Kết nối & khởi tạo MySQL
│   ├── mo_hinh/       # 14 model SQLAlchemy ORM
│   ├── dich_vu/       # Toàn bộ nghiệp vụ (Service layer)
│   ├── tri_tue_nhan_tao/ # Pipeline AI nhận diện khuôn mặt
│   ├── giao_dien/     # 12 màn hình PySide6
│   └── tien_ich/      # Bảo mật, xuất Excel/PDF, log
├── kiem_thu/          # Bộ kiểm thử pytest
└── tai_lieu/          # Tài liệu: đặc tả, kiến trúc, CSDL, hướng dẫn
```

## Tài liệu

| File | Nội dung |
|---|---|
| `tai_lieu/dac_ta_yeu_cau.md` | Đặc tả yêu cầu chức năng/phi chức năng |
| `tai_lieu/kien_truc_he_thong.md` | Kiến trúc phân tầng, pipeline AI |
| `tai_lieu/thiet_ke_co_so_du_lieu.md` | Thiết kế CSDL, sơ đồ ERD |
| `tai_lieu/huong_dan_cai_dat.md` | Hướng dẫn cài đặt chi tiết |
| `tai_lieu/huong_dan_su_dung.md` | Hướng dẫn sử dụng theo từng vai trò |
| `database/README.md` | Hướng dẫn import CSDL bằng phpMyAdmin |

## Kiểm thử

```bash
python -m pytest kiem_thu/ -v
```

## Giấy phép & lưu ý

Dự án phục vụ mục đích học tập/đồ án. Dữ liệu mẫu trong
`database/du_lieu_mau.sql` là dữ liệu giả định, không phải dữ liệu cá nhân
thật. Không đưa file `.env` (chứa cấu hình môi trường của bạn) hay dữ liệu
sinh viên thật lên các kho mã nguồn công khai.
