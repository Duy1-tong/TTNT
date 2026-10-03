-- =====================================================================
-- DU LIEU MAU
-- HE THONG DIEM DANH SINH VIEN BANG KHUON MAT
-- Chay SAU KHI da import schema.sql
-- Mat khau da duoc bam bang bcrypt (khong luu dang van ban ro)
-- =====================================================================

USE diem_danh_khuon_mat;

-- ----- Tai khoan mau -----
-- admin / Admin@123
-- giangvien01 / GiangVien@123
-- sinhvien01 / SinhVien@123
INSERT INTO nguoi_dung (ten_dang_nhap, mat_khau_bam, ho_ten, email, vai_tro, trang_thai) VALUES
('admin', '$2b$12$zGPqxNQq8kD9qC8zhrQl..sv3Z8sHQRMlO/rNHu5fj1Rt.1ptZBoO', 'Quan Tri Vien He Thong', 'admin@truong.edu.vn', 'ADMIN', 'HOAT_DONG'),
('giangvien01', '$2b$12$q4/11EYuvF.rcOiJKGaEW.uTyd6i8rAhvyQTZCKZlGHLW0NSUsjT6', 'Nguyen Van An', 'giangvien01@truong.edu.vn', 'GIANG_VIEN', 'HOAT_DONG'),
('sinhvien01', '$2b$12$DrK3oADt2fC14Z2VhlIEMucZrdZbNGDi61jlnxCEDdwefPqPHttAm', 'Tran Thi Bich', 'sinhvien01@truong.edu.vn', 'SINH_VIEN', 'HOAT_DONG');

-- ----- Khoa -----
INSERT INTO khoa (ma_khoa, ten_khoa, mo_ta) VALUES
('CNTT', 'Khoa Cong Nghe Thong Tin', 'Dao tao nganh Cong nghe thong tin'),
('DTVT', 'Khoa Dien Tu Vien Thong', 'Dao tao nganh Dien tu - Vien thong');

-- ----- Lop hanh chinh -----
INSERT INTO lop_hoc (ma_lop, ten_lop, khoa_id, khoa_hoc) VALUES
('CNTT_K17A', 'Cong Nghe Thong Tin K17A', 1, '2021-2025'),
('CNTT_K17B', 'Cong Nghe Thong Tin K17B', 1, '2021-2025');

-- ----- Giang vien -----
INSERT INTO giang_vien (nguoi_dung_id, ma_giang_vien, ho_ten, email, so_dien_thoai, khoa_id, hoc_vi) VALUES
(2, 'GV0001', 'Nguyen Van An', 'giangvien01@truong.edu.vn', '0900000001', 1, 'Thac Si');

-- ----- Sinh vien -----
INSERT INTO sinh_vien (nguoi_dung_id, ma_sinh_vien, ho_ten, ngay_sinh, gioi_tinh, email, so_dien_thoai, dia_chi, lop_id, khoa_id, trang_thai) VALUES
(3, 'SV0001', 'Tran Thi Bich', '2003-05-12', 'NU', 'sinhvien01@truong.edu.vn', '0900000002', 'Ha Noi', 1, 1, 'DANG_HOC'),
(NULL, 'SV0002', 'Le Van Cuong', '2003-08-20', 'NAM', 'svcuong@truong.edu.vn', '0900000003', 'Hai Phong', 1, 1, 'DANG_HOC'),
(NULL, 'SV0003', 'Pham Thi Dung', '2003-02-02', 'NU', 'svdung@truong.edu.vn', '0900000004', 'Nam Dinh', 1, 1, 'DANG_HOC'),
(NULL, 'SV0004', 'Hoang Van Em', '2003-11-30', 'NAM', 'svem@truong.edu.vn', '0900000005', 'Thanh Hoa', 2, 1, 'DANG_HOC');

-- ----- Mon hoc -----
INSERT INTO mon_hoc (ma_mon, ten_mon, so_tin_chi, khoa_id) VALUES
('IT101', 'Nhap Mon Lap Trinh', 3, 1),
('IT205', 'Tri Tue Nhan Tao', 3, 1);

-- ----- Lop hoc phan -----
INSERT INTO lop_mon_hoc (ma_lop_mon, mon_hoc_id, giang_vien_id, hoc_ky, nam_hoc) VALUES
('IT101_HK1_2024', 1, 1, 'HK1', '2024-2025'),
('IT205_HK1_2024', 2, 1, 'HK1', '2024-2025');

-- ----- Sinh vien dang ky lop hoc phan -----
INSERT INTO sinh_vien_lop (sinh_vien_id, lop_mon_hoc_id, trang_thai) VALUES
(1, 1, 'DANG_HOC'),
(2, 1, 'DANG_HOC'),
(3, 1, 'DANG_HOC'),
(4, 1, 'DANG_HOC'),
(1, 2, 'DANG_HOC'),
(2, 2, 'DANG_HOC');

-- ----- Buoi hoc mau -----
INSERT INTO buoi_hoc (lop_mon_hoc_id, ngay_hoc, gio_bat_dau, gio_ket_thuc, gio_mo_diem_danh, gio_dong_diem_danh, phong_hoc, trang_thai, nguoi_tao_id) VALUES
(1, CURDATE(), '07:00:00', '09:30:00', CONCAT(CURDATE(), ' 06:50:00'), CONCAT(CURDATE(), ' 09:30:00'), 'A101', 'CHUA_BAT_DAU', 2);

-- ----- Camera mau -----
INSERT INTO camera (ten_camera, nguon, vi_tri, trang_thai) VALUES
('Camera Webcam May Tinh', '0', 'Phong A101', 'HOAT_DONG');

-- ----- Cau hinh mac dinh -----
INSERT INTO cau_hinh (khoa_cau_hinh, gia_tri, mo_ta) VALUES
('NGUONG_DO_TUONG_DONG', '0.45', 'Nguong cosine similarity de xac nhan cung mot nguoi'),
('SO_LAN_DANG_NHAP_SAI_TOI_DA', '5', 'So lan dang nhap sai toi da truoc khi khoa tai khoan'),
('THOI_GIAN_KHOA_TAI_KHOAN_PHUT', '15', 'Thoi gian khoa tai khoan tinh bang phut'),
('PHUT_TINH_DI_MUON', '15', 'So phut sau gio bat dau duoc tinh la di muon');
