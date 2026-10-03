-- =====================================================================
-- SCHEMA CO SO DU LIEU
-- HE THONG DIEM DANH SINH VIEN BANG KHUON MAT
-- Co the import truc tiep bang phpMyAdmin (Import) hoac chay bang MySQL CLI:
--   mysql -u root -p < schema.sql
-- =====================================================================

CREATE DATABASE IF NOT EXISTS diem_danh_khuon_mat
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE diem_danh_khuon_mat;

SET FOREIGN_KEY_CHECKS = 0;

-- ---------------------------------------------------------------------
-- BANG NGUOI_DUNG: tai khoan dang nhap he thong (ADMIN / GIANG_VIEN / SINH_VIEN)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS nguoi_dung;
CREATE TABLE nguoi_dung (
    id                      INT UNSIGNED NOT NULL AUTO_INCREMENT,
    ten_dang_nhap           VARCHAR(50)  NOT NULL,
    mat_khau_bam            VARCHAR(255) NOT NULL,
    ho_ten                  VARCHAR(150) NOT NULL,
    email                   VARCHAR(150) NULL,
    vai_tro                 ENUM('ADMIN', 'GIANG_VIEN', 'SINH_VIEN') NOT NULL,
    trang_thai              ENUM('HOAT_DONG', 'KHOA', 'NGUNG_HOAT_DONG') NOT NULL DEFAULT 'HOAT_DONG',
    so_lan_dang_nhap_sai    SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    thoi_diem_khoa          DATETIME NULL,
    lan_dang_nhap_cuoi      DATETIME NULL,
    ngay_tao                DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_nguoi_dung_ten_dang_nhap (ten_dang_nhap),
    UNIQUE KEY uk_nguoi_dung_email (email),
    KEY idx_nguoi_dung_vai_tro (vai_tro)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BANG KHOA: don vi khoa/vien trong truong
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS khoa;
CREATE TABLE khoa (
    id              INT UNSIGNED NOT NULL AUTO_INCREMENT,
    ma_khoa         VARCHAR(20)  NOT NULL,
    ten_khoa        VARCHAR(150) NOT NULL,
    mo_ta           VARCHAR(500) NULL,
    ngay_tao        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_khoa_ma_khoa (ma_khoa)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BANG LOP_HOC: lop hanh chinh cua sinh vien
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS lop_hoc;
CREATE TABLE lop_hoc (
    id              INT UNSIGNED NOT NULL AUTO_INCREMENT,
    ma_lop          VARCHAR(20)  NOT NULL,
    ten_lop         VARCHAR(150) NOT NULL,
    khoa_id         INT UNSIGNED NOT NULL,
    khoa_hoc        VARCHAR(20)  NULL,
    ngay_tao        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_lop_hoc_ma_lop (ma_lop),
    KEY idx_lop_hoc_khoa_id (khoa_id),
    CONSTRAINT fk_lop_hoc_khoa FOREIGN KEY (khoa_id) REFERENCES khoa(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BANG GIANG_VIEN
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS giang_vien;
CREATE TABLE giang_vien (
    id              INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nguoi_dung_id   INT UNSIGNED NULL,
    ma_giang_vien   VARCHAR(20)  NOT NULL,
    ho_ten          VARCHAR(150) NOT NULL,
    email           VARCHAR(150) NULL,
    so_dien_thoai   VARCHAR(20)  NULL,
    khoa_id         INT UNSIGNED NULL,
    hoc_vi          VARCHAR(50)  NULL,
    trang_thai      ENUM('DANG_CONG_TAC', 'NGHI_VIEC') NOT NULL DEFAULT 'DANG_CONG_TAC',
    ngay_tao        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_giang_vien_ma_giang_vien (ma_giang_vien),
    UNIQUE KEY uk_giang_vien_nguoi_dung_id (nguoi_dung_id),
    KEY idx_giang_vien_khoa_id (khoa_id),
    CONSTRAINT fk_giang_vien_nguoi_dung FOREIGN KEY (nguoi_dung_id) REFERENCES nguoi_dung(id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_giang_vien_khoa FOREIGN KEY (khoa_id) REFERENCES khoa(id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BANG SINH_VIEN
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS sinh_vien;
CREATE TABLE sinh_vien (
    id              INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nguoi_dung_id   INT UNSIGNED NULL,
    ma_sinh_vien    VARCHAR(20)  NOT NULL,
    ho_ten          VARCHAR(150) NOT NULL,
    ngay_sinh       DATE NULL,
    gioi_tinh       ENUM('NAM', 'NU', 'KHAC') NULL,
    email           VARCHAR(150) NULL,
    so_dien_thoai   VARCHAR(20)  NULL,
    dia_chi         VARCHAR(255) NULL,
    lop_id          INT UNSIGNED NULL,
    khoa_id         INT UNSIGNED NULL,
    anh_dai_dien    VARCHAR(255) NULL,
    trang_thai      ENUM('DANG_HOC', 'NGHI_HOC', 'BAO_LUU', 'TOT_NGHIEP') NOT NULL DEFAULT 'DANG_HOC',
    ngay_tao        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_sinh_vien_ma_sinh_vien (ma_sinh_vien),
    UNIQUE KEY uk_sinh_vien_email (email),
    UNIQUE KEY uk_sinh_vien_nguoi_dung_id (nguoi_dung_id),
    KEY idx_sinh_vien_lop_id (lop_id),
    KEY idx_sinh_vien_khoa_id (khoa_id),
    KEY idx_sinh_vien_trang_thai (trang_thai),
    CONSTRAINT fk_sinh_vien_nguoi_dung FOREIGN KEY (nguoi_dung_id) REFERENCES nguoi_dung(id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_sinh_vien_lop FOREIGN KEY (lop_id) REFERENCES lop_hoc(id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_sinh_vien_khoa FOREIGN KEY (khoa_id) REFERENCES khoa(id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BANG MON_HOC
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS mon_hoc;
CREATE TABLE mon_hoc (
    id              INT UNSIGNED NOT NULL AUTO_INCREMENT,
    ma_mon          VARCHAR(20)  NOT NULL,
    ten_mon         VARCHAR(150) NOT NULL,
    so_tin_chi      TINYINT UNSIGNED NOT NULL DEFAULT 0,
    khoa_id         INT UNSIGNED NULL,
    ngay_tao        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_mon_hoc_ma_mon (ma_mon),
    KEY idx_mon_hoc_khoa_id (khoa_id),
    CONSTRAINT fk_mon_hoc_khoa FOREIGN KEY (khoa_id) REFERENCES khoa(id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BANG LOP_MON_HOC: lop hoc phan (mot mon hoc mo trong mot hoc ky do 1 GV day)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS lop_mon_hoc;
CREATE TABLE lop_mon_hoc (
    id              INT UNSIGNED NOT NULL AUTO_INCREMENT,
    ma_lop_mon      VARCHAR(30)  NOT NULL,
    mon_hoc_id      INT UNSIGNED NOT NULL,
    giang_vien_id   INT UNSIGNED NULL,
    hoc_ky          VARCHAR(20)  NOT NULL,
    nam_hoc         VARCHAR(20)  NOT NULL,
    ngay_tao        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_lop_mon_hoc_ma (ma_lop_mon),
    KEY idx_lop_mon_hoc_mon_hoc_id (mon_hoc_id),
    KEY idx_lop_mon_hoc_giang_vien_id (giang_vien_id),
    CONSTRAINT fk_lop_mon_hoc_mon_hoc FOREIGN KEY (mon_hoc_id) REFERENCES mon_hoc(id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_lop_mon_hoc_giang_vien FOREIGN KEY (giang_vien_id) REFERENCES giang_vien(id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BANG SINH_VIEN_LOP: sinh vien dang ky hoc lop hoc phan nao
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS sinh_vien_lop;
CREATE TABLE sinh_vien_lop (
    id                  INT UNSIGNED NOT NULL AUTO_INCREMENT,
    sinh_vien_id        INT UNSIGNED NOT NULL,
    lop_mon_hoc_id      INT UNSIGNED NOT NULL,
    ngay_dang_ky        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    trang_thai          ENUM('DANG_HOC', 'DA_HUY') NOT NULL DEFAULT 'DANG_HOC',
    PRIMARY KEY (id),
    UNIQUE KEY uk_sinh_vien_lop (sinh_vien_id, lop_mon_hoc_id),
    KEY idx_sinh_vien_lop_lop_mon_hoc_id (lop_mon_hoc_id),
    CONSTRAINT fk_sinh_vien_lop_sinh_vien FOREIGN KEY (sinh_vien_id) REFERENCES sinh_vien(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_sinh_vien_lop_lop_mon_hoc FOREIGN KEY (lop_mon_hoc_id) REFERENCES lop_mon_hoc(id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BANG BUOI_HOC: mot buoi hoc cu the cua mot lop hoc phan
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS buoi_hoc;
CREATE TABLE buoi_hoc (
    id                  INT UNSIGNED NOT NULL AUTO_INCREMENT,
    lop_mon_hoc_id      INT UNSIGNED NOT NULL,
    ngay_hoc            DATE NOT NULL,
    gio_bat_dau         TIME NOT NULL,
    gio_ket_thuc        TIME NOT NULL,
    gio_mo_diem_danh    DATETIME NULL,
    gio_dong_diem_danh  DATETIME NULL,
    phong_hoc           VARCHAR(50) NULL,
    trang_thai          ENUM('CHUA_BAT_DAU', 'DANG_DIEM_DANH', 'DA_KET_THUC') NOT NULL DEFAULT 'CHUA_BAT_DAU',
    nguoi_tao_id        INT UNSIGNED NULL,
    ngay_tao            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_buoi_hoc_lop_mon_hoc_id (lop_mon_hoc_id),
    KEY idx_buoi_hoc_ngay_hoc (ngay_hoc),
    KEY idx_buoi_hoc_trang_thai (trang_thai),
    CONSTRAINT fk_buoi_hoc_lop_mon_hoc FOREIGN KEY (lop_mon_hoc_id) REFERENCES lop_mon_hoc(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_buoi_hoc_nguoi_tao FOREIGN KEY (nguoi_tao_id) REFERENCES nguoi_dung(id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BANG DIEM_DANH
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS diem_danh;
CREATE TABLE diem_danh (
    id                      INT UNSIGNED NOT NULL AUTO_INCREMENT,
    buoi_hoc_id             INT UNSIGNED NOT NULL,
    sinh_vien_id            INT UNSIGNED NOT NULL,
    thoi_gian_diem_danh     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    trang_thai              ENUM('CO_MAT', 'DI_MUON', 'VANG', 'CO_PHEP') NOT NULL DEFAULT 'CO_MAT',
    phuong_thuc             ENUM('KHUON_MAT', 'THU_CONG') NOT NULL DEFAULT 'KHUON_MAT',
    do_tuong_dong           FLOAT NULL,
    ghi_chu                 VARCHAR(500) NULL,
    nguoi_thuc_hien_id      INT UNSIGNED NULL,
    ngay_tao                DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_diem_danh_buoi_sinh_vien (buoi_hoc_id, sinh_vien_id),
    KEY idx_diem_danh_sinh_vien_id (sinh_vien_id),
    KEY idx_diem_danh_trang_thai (trang_thai),
    CONSTRAINT fk_diem_danh_buoi_hoc FOREIGN KEY (buoi_hoc_id) REFERENCES buoi_hoc(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_diem_danh_sinh_vien FOREIGN KEY (sinh_vien_id) REFERENCES sinh_vien(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_diem_danh_nguoi_thuc_hien FOREIGN KEY (nguoi_thuc_hien_id) REFERENCES nguoi_dung(id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BANG KHUON_MAT: embedding khuon mat da dang ky cua sinh vien
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS khuon_mat;
CREATE TABLE khuon_mat (
    id                  INT UNSIGNED NOT NULL AUTO_INCREMENT,
    sinh_vien_id        INT UNSIGNED NOT NULL,
    embedding           LONGBLOB NOT NULL,
    mo_hinh             VARCHAR(50) NOT NULL,
    phien_ban_mo_hinh   VARCHAR(20) NOT NULL,
    ngay_tao            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_khuon_mat_sinh_vien_id (sinh_vien_id),
    CONSTRAINT fk_khuon_mat_sinh_vien FOREIGN KEY (sinh_vien_id) REFERENCES sinh_vien(id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BANG CAMERA
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS camera;
CREATE TABLE camera (
    id              INT UNSIGNED NOT NULL AUTO_INCREMENT,
    ten_camera      VARCHAR(100) NOT NULL,
    nguon           VARCHAR(255) NOT NULL,
    vi_tri          VARCHAR(150) NULL,
    trang_thai      ENUM('HOAT_DONG', 'NGUNG_SU_DUNG') NOT NULL DEFAULT 'HOAT_DONG',
    ngay_tao        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ngay_cap_nhat   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BANG NHAT_KY_HE_THONG: audit log
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS nhat_ky_he_thong;
CREATE TABLE nhat_ky_he_thong (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    nguoi_dung_id   INT UNSIGNED NULL,
    hanh_dong       VARCHAR(100) NOT NULL,
    doi_tuong       VARCHAR(100) NULL,
    doi_tuong_id    INT UNSIGNED NULL,
    noi_dung        VARCHAR(1000) NULL,
    dia_chi_ip      VARCHAR(50) NULL,
    thoi_gian       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ket_qua         ENUM('THANH_CONG', 'THAT_BAI') NOT NULL DEFAULT 'THANH_CONG',
    PRIMARY KEY (id),
    KEY idx_nhat_ky_nguoi_dung_id (nguoi_dung_id),
    KEY idx_nhat_ky_thoi_gian (thoi_gian),
    KEY idx_nhat_ky_hanh_dong (hanh_dong),
    CONSTRAINT fk_nhat_ky_nguoi_dung FOREIGN KEY (nguoi_dung_id) REFERENCES nguoi_dung(id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- BANG CAU_HINH: cau hinh he thong dang khoa - gia tri
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS cau_hinh;
CREATE TABLE cau_hinh (
    id              INT UNSIGNED NOT NULL AUTO_INCREMENT,
    khoa_cau_hinh   VARCHAR(100) NOT NULL,
    gia_tri         VARCHAR(500) NULL,
    mo_ta           VARCHAR(255) NULL,
    ngay_cap_nhat   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_cau_hinh_khoa (khoa_cau_hinh)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
