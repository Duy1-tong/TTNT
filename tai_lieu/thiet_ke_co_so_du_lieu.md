# Thiết Kế Cơ Sở Dữ Liệu — `diem_danh_khuon_mat`

Cơ sở dữ liệu chạy trên **MySQL/MariaDB** (qua XAMPP), charset
`utf8mb4`, collation `utf8mb4_unicode_ci`. Gồm **14 bảng**.

## 1. Sơ đồ quan hệ thực thể (ERD)

```mermaid
erDiagram
    NGUOI_DUNG ||--o| SINH_VIEN : "co the co"
    NGUOI_DUNG ||--o| GIANG_VIEN : "co the co"
    NGUOI_DUNG ||--o{ NHAT_KY_HE_THONG : "thuc hien"
    NGUOI_DUNG ||--o{ BUOI_HOC : "tao"
    NGUOI_DUNG ||--o{ DIEM_DANH : "thuc hien"

    KHOA ||--o{ LOP_HOC : "co"
    KHOA ||--o{ GIANG_VIEN : "thuoc"
    KHOA ||--o{ SINH_VIEN : "thuoc"
    KHOA ||--o{ MON_HOC : "thuoc"

    LOP_HOC ||--o{ SINH_VIEN : "co"

    MON_HOC ||--o{ LOP_MON_HOC : "duoc mo thanh"
    GIANG_VIEN ||--o{ LOP_MON_HOC : "phu trach"

    LOP_MON_HOC ||--o{ SINH_VIEN_LOP : "co"
    SINH_VIEN ||--o{ SINH_VIEN_LOP : "dang ky"

    LOP_MON_HOC ||--o{ BUOI_HOC : "co cac"
    BUOI_HOC ||--o{ DIEM_DANH : "ghi nhan"
    SINH_VIEN ||--o{ DIEM_DANH : "co"
    SINH_VIEN ||--o{ KHUON_MAT : "dang ky"

    NGUOI_DUNG {
        int id PK
        varchar ten_dang_nhap UK
        varchar mat_khau_bam
        varchar ho_ten
        varchar email UK
        enum vai_tro
        enum trang_thai
        smallint so_lan_dang_nhap_sai
        datetime thoi_diem_khoa
        datetime lan_dang_nhap_cuoi
    }
    KHOA {
        int id PK
        varchar ma_khoa UK
        varchar ten_khoa
        varchar mo_ta
    }
    LOP_HOC {
        int id PK
        varchar ma_lop UK
        varchar ten_lop
        int khoa_id FK
        varchar khoa_hoc
    }
    GIANG_VIEN {
        int id PK
        int nguoi_dung_id FK_UK
        varchar ma_giang_vien UK
        varchar ho_ten
        int khoa_id FK
        enum trang_thai
    }
    SINH_VIEN {
        int id PK
        int nguoi_dung_id FK_UK
        varchar ma_sinh_vien UK
        varchar ho_ten
        date ngay_sinh
        enum gioi_tinh
        varchar email UK
        int lop_id FK
        int khoa_id FK
        enum trang_thai
    }
    MON_HOC {
        int id PK
        varchar ma_mon UK
        varchar ten_mon
        tinyint so_tin_chi
        int khoa_id FK
    }
    LOP_MON_HOC {
        int id PK
        varchar ma_lop_mon UK
        int mon_hoc_id FK
        int giang_vien_id FK
        varchar hoc_ky
        varchar nam_hoc
    }
    SINH_VIEN_LOP {
        int id PK
        int sinh_vien_id FK
        int lop_mon_hoc_id FK
        enum trang_thai
    }
    BUOI_HOC {
        int id PK
        int lop_mon_hoc_id FK
        date ngay_hoc
        time gio_bat_dau
        time gio_ket_thuc
        datetime gio_mo_diem_danh
        datetime gio_dong_diem_danh
        varchar phong_hoc
        enum trang_thai
        int nguoi_tao_id FK
    }
    DIEM_DANH {
        int id PK
        int buoi_hoc_id FK
        int sinh_vien_id FK
        datetime thoi_gian_diem_danh
        enum trang_thai
        enum phuong_thuc
        float do_tuong_dong
        int nguoi_thuc_hien_id FK
    }
    KHUON_MAT {
        int id PK
        int sinh_vien_id FK
        longblob embedding
        varchar mo_hinh
        varchar phien_ban_mo_hinh
    }
    CAMERA {
        int id PK
        varchar ten_camera
        varchar nguon
        varchar vi_tri
        enum trang_thai
    }
    NHAT_KY_HE_THONG {
        bigint id PK
        int nguoi_dung_id FK
        varchar hanh_dong
        varchar doi_tuong
        int doi_tuong_id
        varchar noi_dung
        varchar dia_chi_ip
        datetime thoi_gian
        enum ket_qua
    }
    CAU_HINH {
        int id PK
        varchar khoa_cau_hinh UK
        varchar gia_tri
        varchar mo_ta
    }
```

## 2. Mô tả chi tiết từng bảng

### 2.1. `nguoi_dung`
Tài khoản đăng nhập hệ thống. `vai_tro` ∈ {ADMIN, GIANG_VIEN, SINH_VIEN}.
`trang_thai` ∈ {HOAT_DONG, KHOA, NGUNG_HOAT_DONG}. Chống brute-force bằng
`so_lan_dang_nhap_sai` + `thoi_diem_khoa`. **Unique:** `ten_dang_nhap`, `email`.

### 2.2. `khoa`
Danh mục khoa/viện. **Unique:** `ma_khoa`.

### 2.3. `lop_hoc`
Lớp hành chính, thuộc một `khoa`. **Unique:** `ma_lop`. **FK:** `khoa_id`
→ `khoa.id` (ON DELETE RESTRICT — không cho xóa khoa còn lớp).

### 2.4. `giang_vien`
Hồ sơ giảng viên, có thể liên kết 1-1 với một `nguoi_dung` (để đăng nhập).
**Unique:** `ma_giang_vien`, `nguoi_dung_id`. **FK:** `nguoi_dung_id` →
`nguoi_dung.id` (SET NULL), `khoa_id` → `khoa.id` (SET NULL).

### 2.5. `sinh_vien`
Hồ sơ sinh viên. `trang_thai` ∈ {DANG_HOC, NGHI_HOC, BAO_LUU, TOT_NGHIEP}.
**Không xóa vật lý** sinh viên đã có lịch sử điểm danh — tầng Service
chặn thao tác này, chỉ cho phép đổi `trang_thai`. **Unique:**
`ma_sinh_vien`, `email`, `nguoi_dung_id`. **FK:** `lop_id` → `lop_hoc.id`
(SET NULL), `khoa_id` → `khoa.id` (SET NULL), `nguoi_dung_id` →
`nguoi_dung.id` (SET NULL).

### 2.6. `mon_hoc`
Danh mục môn học. **Unique:** `ma_mon`. **FK:** `khoa_id` → `khoa.id`
(SET NULL).

### 2.7. `lop_mon_hoc`
Lớp học phần: một môn học được mở trong một học kỳ cụ thể, do một giảng
viên phụ trách. **Unique:** `ma_lop_mon`. **FK:** `mon_hoc_id` →
`mon_hoc.id` (RESTRICT), `giang_vien_id` → `giang_vien.id` (SET NULL).

### 2.8. `sinh_vien_lop`
Bảng trung gian: sinh viên đăng ký học lớp học phần nào. **Unique:**
(`sinh_vien_id`, `lop_mon_hoc_id`) — chống đăng ký trùng. **FK:** cả hai
cột đều CASCADE khi xóa bản ghi cha.

### 2.9. `buoi_hoc`
Một buổi học cụ thể của một lớp học phần — đơn vị để điểm danh.
`trang_thai` ∈ {CHUA_BAT_DAU, DANG_DIEM_DANH, DA_KET_THUC}. **FK:**
`lop_mon_hoc_id` → `lop_mon_hoc.id` (CASCADE), `nguoi_tao_id` →
`nguoi_dung.id` (SET NULL).

### 2.10. `diem_danh`
Bản ghi điểm danh của một sinh viên trong một buổi học. **Unique:**
(`buoi_hoc_id`, `sinh_vien_id`) — **ràng buộc quan trọng nhất hệ thống**,
đảm bảo chống điểm danh trùng ngay ở tầng CSDL (không chỉ ở code).
`trang_thai` ∈ {CO_MAT, DI_MUON, VANG, CO_PHEP}. `phuong_thuc` ∈
{KHUON_MAT, THU_CONG}. **FK:** `buoi_hoc_id` (CASCADE), `sinh_vien_id`
(CASCADE), `nguoi_thuc_hien_id` → `nguoi_dung.id` (SET NULL).

### 2.11. `khuon_mat`
Embedding khuôn mặt đã đăng ký của sinh viên, lưu dạng `LONGBLOB` **đã mã
hóa** (không lưu ảnh gốc). `mo_hinh`/`phien_ban_mo_hinh` cho biết embedding
được tạo bởi mô hình AI nào (InsightFace hay fallback OpenCV) để tránh so
sánh chéo giữa hai không gian đặc trưng khác nhau. **FK:** `sinh_vien_id`
→ `sinh_vien.id` (CASCADE — xóa sinh viên thì xóa luôn dữ liệu sinh trắc
học liên quan, tuy nhiên như đã nêu, sinh viên có lịch sử điểm danh sẽ
không xóa được ở tầng Service).

### 2.12. `camera`
Danh mục camera dùng để điểm danh (`nguon` là chỉ số webcam hoặc URL
RTSP).

### 2.13. `nhat_ky_he_thong`
Audit log toàn hệ thống. `id` kiểu `BIGINT` (khối lượng bản ghi lớn theo
thời gian). **FK:** `nguoi_dung_id` → `nguoi_dung.id` (SET NULL — giữ lại
lịch sử ngay cả khi tài khoản gốc bị xóa).

### 2.14. `cau_hinh`
Cấu hình động dạng khóa-giá trị (ngưỡng nhận diện, số lần đăng nhập sai
tối đa...). **Unique:** `khoa_cau_hinh`.

## 3. Chỉ mục (Index)
Ngoài khóa chính/khóa ngoại (tự động có index), các cột thường dùng để
lọc/tìm kiếm đều có index riêng: `nguoi_dung.vai_tro`,
`sinh_vien.trang_thai`, `buoi_hoc.ngay_hoc`, `buoi_hoc.trang_thai`,
`diem_danh.trang_thai`, `nhat_ky_he_thong.thoi_gian`,
`nhat_ky_he_thong.hanh_dong`.

## 4. Hai cách khởi tạo schema

1. **Tự động (khuyến nghị):** `python cai_dat.py` hoặc
   `python tao_co_so_du_lieu.py` — dùng SQLAlchemy ORM
   (`Base.metadata.create_all()`), đọc định nghĩa trực tiếp từ
   `app/mo_hinh/*.py`.
2. **Thủ công qua phpMyAdmin:** Import `database/schema.sql` — file SQL
   thuần, khai báo tường minh từng cột/ràng buộc, dùng khi máy không chạy
   được Python hoặc muốn kiểm tra schema bằng mắt.

Cả hai cách đều tạo ra cùng một cấu trúc 14 bảng, cùng ràng buộc khóa
ngoại và quy tắc `ON DELETE` như mô tả ở trên.
