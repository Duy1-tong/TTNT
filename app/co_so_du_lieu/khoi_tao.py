"""
Module khoi tao co so du lieu: tao database (neu chua co), tao toan bo
bang bang SQLAlchemy ORM, va nap du lieu mau (tai khoan Admin mac dinh...).

Duoc su dung boi ca `cai_dat.py` va `tao_co_so_du_lieu.py` o thu muc goc.
"""

from __future__ import annotations

import datetime as _datetime
import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.cau_hinh.cai_dat import lay_cau_hinh
from app.co_so_du_lieu.ket_noi import lay_dong_co, mo_phien_lam_viec
from app.co_so_du_lieu.mo_hinh import Base
from app.mo_hinh import (  # noqa: F401 - import de dang ky toan bo bang voi Base
    BuoiHoc,
    Camera,
    CauHinh,
    DiemDanh,
    GiangVien,
    Khoa,
    KhuonMat,
    LopHoc,
    LopMonHoc,
    MonHoc,
    NguoiDung,
    NhatKyHeThong,
    SinhVien,
    SinhVienLop,
)
from app.mo_hinh.buoi_hoc import TrangThaiBuoiHoc
from app.mo_hinh.giang_vien import TrangThaiGiangVien
from app.mo_hinh.nguoi_dung import TrangThaiTaiKhoan, VaiTro
from app.mo_hinh.sinh_vien import GioiTinh, TrangThaiSinhVien
from app.mo_hinh.sinh_vien_lop import TrangThaiDangKy
from app.mo_hinh.camera import TrangThaiCamera
from app.tien_ich.bao_mat import bam_mat_khau

_bo_ghi_log = logging.getLogger(__name__)


def tao_database_neu_chua_co() -> tuple[bool, str]:
    """Tao database `diem_danh_khuon_mat` neu chua ton tai tren may chu MySQL."""
    cau_hinh = lay_cau_hinh().co_so_du_lieu
    try:
        dong_co_server = create_engine(
            cau_hinh.chuoi_ket_noi_khong_co_database,
            connect_args={"connect_timeout": 5},
            future=True,
        )
        with dong_co_server.connect() as ket_noi:
            ket_noi.execute(
                text(
                    f"CREATE DATABASE IF NOT EXISTS `{cau_hinh.ten_co_so_du_lieu}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            )
            ket_noi.commit()
        dong_co_server.dispose()
        return True, f"Da dam bao database '{cau_hinh.ten_co_so_du_lieu}' ton tai."
    except Exception as loi:  # noqa: BLE001
        thong_bao = f"Khong the tao database: {loi}"
        _bo_ghi_log.error(thong_bao)
        return False, thong_bao


def tao_toan_bo_bang() -> tuple[bool, str]:
    """Tao toan bo bang con thieu trong database bang SQLAlchemy metadata."""
    try:
        dong_co = lay_dong_co(buoc_lai=True)
        Base.metadata.create_all(bind=dong_co)
        return True, "Da tao (hoac xac nhan da co) toan bo bang can thiet."
    except Exception as loi:  # noqa: BLE001
        thong_bao = f"Khong the tao bang: {loi}"
        _bo_ghi_log.error(thong_bao)
        return False, thong_bao


def _da_co_du_lieu_mau(phien: Session) -> bool:
    """Kiem tra xem du lieu mau da ton tai hay chua (tranh nap trung)."""
    return phien.query(NguoiDung).filter_by(ten_dang_nhap="admin").first() is not None


def nap_du_lieu_mau() -> tuple[bool, str]:
    """Nap du lieu mau: tai khoan Admin/Giang vien/Sinh vien, khoa, lop, mon hoc...

    Ham nay AN TOAN de goi nhieu lan: neu du lieu mau da ton tai se bo qua.
    """
    try:
        with mo_phien_lam_viec() as phien:
            if _da_co_du_lieu_mau(phien):
                return True, "Du lieu mau da ton tai tu truoc, bo qua buoc nap."

            # ----- Tai khoan -----
            tai_khoan_admin = NguoiDung(
                ten_dang_nhap="admin",
                mat_khau_bam=bam_mat_khau("Admin@123"),
                ho_ten="Quan Tri Vien He Thong",
                email="admin@truong.edu.vn",
                vai_tro=VaiTro.ADMIN,
                trang_thai=TrangThaiTaiKhoan.HOAT_DONG,
            )
            tai_khoan_giang_vien = NguoiDung(
                ten_dang_nhap="giangvien01",
                mat_khau_bam=bam_mat_khau("GiangVien@123"),
                ho_ten="Nguyen Van An",
                email="giangvien01@truong.edu.vn",
                vai_tro=VaiTro.GIANG_VIEN,
                trang_thai=TrangThaiTaiKhoan.HOAT_DONG,
            )
            tai_khoan_sinh_vien = NguoiDung(
                ten_dang_nhap="sinhvien01",
                mat_khau_bam=bam_mat_khau("SinhVien@123"),
                ho_ten="Tran Thi Bich",
                email="sinhvien01@truong.edu.vn",
                vai_tro=VaiTro.SINH_VIEN,
                trang_thai=TrangThaiTaiKhoan.HOAT_DONG,
            )
            phien.add_all([tai_khoan_admin, tai_khoan_giang_vien, tai_khoan_sinh_vien])
            phien.flush()

            # ----- Khoa -----
            khoa_cntt = Khoa(ma_khoa="CNTT", ten_khoa="Khoa Cong Nghe Thong Tin")
            khoa_dtvt = Khoa(ma_khoa="DTVT", ten_khoa="Khoa Dien Tu Vien Thong")
            phien.add_all([khoa_cntt, khoa_dtvt])
            phien.flush()

            # ----- Lop hanh chinh -----
            lop_a = LopHoc(
                ma_lop="CNTT_K17A", ten_lop="Cong Nghe Thong Tin K17A",
                khoa_id=khoa_cntt.id, khoa_hoc="2021-2025",
            )
            lop_b = LopHoc(
                ma_lop="CNTT_K17B", ten_lop="Cong Nghe Thong Tin K17B",
                khoa_id=khoa_cntt.id, khoa_hoc="2021-2025",
            )
            phien.add_all([lop_a, lop_b])
            phien.flush()

            # ----- Giang vien -----
            giang_vien = GiangVien(
                nguoi_dung_id=tai_khoan_giang_vien.id,
                ma_giang_vien="GV0001",
                ho_ten="Nguyen Van An",
                email="giangvien01@truong.edu.vn",
                so_dien_thoai="0900000001",
                khoa_id=khoa_cntt.id,
                hoc_vi="Thac Si",
                trang_thai=TrangThaiGiangVien.DANG_CONG_TAC,
            )
            phien.add(giang_vien)
            phien.flush()

            # ----- Sinh vien -----
            sinh_vien_01 = SinhVien(
                nguoi_dung_id=tai_khoan_sinh_vien.id,
                ma_sinh_vien="SV0001",
                ho_ten="Tran Thi Bich",
                ngay_sinh=_datetime.date(2003, 5, 12),
                gioi_tinh=GioiTinh.NU,
                email="sinhvien01@truong.edu.vn",
                so_dien_thoai="0900000002",
                dia_chi="Ha Noi",
                lop_id=lop_a.id,
                khoa_id=khoa_cntt.id,
                trang_thai=TrangThaiSinhVien.DANG_HOC,
            )
            sinh_vien_02 = SinhVien(
                ma_sinh_vien="SV0002", ho_ten="Le Van Cuong",
                ngay_sinh=_datetime.date(2003, 8, 20), gioi_tinh=GioiTinh.NAM,
                email="svcuong@truong.edu.vn", so_dien_thoai="0900000003",
                dia_chi="Hai Phong", lop_id=lop_a.id, khoa_id=khoa_cntt.id,
                trang_thai=TrangThaiSinhVien.DANG_HOC,
            )
            sinh_vien_03 = SinhVien(
                ma_sinh_vien="SV0003", ho_ten="Pham Thi Dung",
                ngay_sinh=_datetime.date(2003, 2, 2), gioi_tinh=GioiTinh.NU,
                email="svdung@truong.edu.vn", so_dien_thoai="0900000004",
                dia_chi="Nam Dinh", lop_id=lop_a.id, khoa_id=khoa_cntt.id,
                trang_thai=TrangThaiSinhVien.DANG_HOC,
            )
            sinh_vien_04 = SinhVien(
                ma_sinh_vien="SV0004", ho_ten="Hoang Van Em",
                ngay_sinh=_datetime.date(2003, 11, 30), gioi_tinh=GioiTinh.NAM,
                email="svem@truong.edu.vn", so_dien_thoai="0900000005",
                dia_chi="Thanh Hoa", lop_id=lop_b.id, khoa_id=khoa_cntt.id,
                trang_thai=TrangThaiSinhVien.DANG_HOC,
            )
            phien.add_all([sinh_vien_01, sinh_vien_02, sinh_vien_03, sinh_vien_04])
            phien.flush()

            # ----- Mon hoc -----
            mon_lap_trinh = MonHoc(ma_mon="IT101", ten_mon="Nhap Mon Lap Trinh", so_tin_chi=3, khoa_id=khoa_cntt.id)
            mon_tri_tue = MonHoc(ma_mon="IT205", ten_mon="Tri Tue Nhan Tao", so_tin_chi=3, khoa_id=khoa_cntt.id)
            phien.add_all([mon_lap_trinh, mon_tri_tue])
            phien.flush()

            # ----- Lop hoc phan -----
            lop_mon_lap_trinh = LopMonHoc(
                ma_lop_mon="IT101_HK1_2024", mon_hoc_id=mon_lap_trinh.id,
                giang_vien_id=giang_vien.id, hoc_ky="HK1", nam_hoc="2024-2025",
            )
            lop_mon_tri_tue = LopMonHoc(
                ma_lop_mon="IT205_HK1_2024", mon_hoc_id=mon_tri_tue.id,
                giang_vien_id=giang_vien.id, hoc_ky="HK1", nam_hoc="2024-2025",
            )
            phien.add_all([lop_mon_lap_trinh, lop_mon_tri_tue])
            phien.flush()

            # ----- Dang ky hoc phan -----
            for sinh_vien in (sinh_vien_01, sinh_vien_02, sinh_vien_03, sinh_vien_04):
                phien.add(
                    SinhVienLop(
                        sinh_vien_id=sinh_vien.id,
                        lop_mon_hoc_id=lop_mon_lap_trinh.id,
                        trang_thai=TrangThaiDangKy.DANG_HOC,
                    )
                )
            for sinh_vien in (sinh_vien_01, sinh_vien_02):
                phien.add(
                    SinhVienLop(
                        sinh_vien_id=sinh_vien.id,
                        lop_mon_hoc_id=lop_mon_tri_tue.id,
                        trang_thai=TrangThaiDangKy.DANG_HOC,
                    )
                )

            # ----- Buoi hoc mau (hom nay) -----
            hom_nay = _datetime.date.today()
            buoi_hoc_mau = BuoiHoc(
                lop_mon_hoc_id=lop_mon_lap_trinh.id,
                ngay_hoc=hom_nay,
                gio_bat_dau=_datetime.time(7, 0),
                gio_ket_thuc=_datetime.time(9, 30),
                gio_mo_diem_danh=_datetime.datetime.combine(hom_nay, _datetime.time(6, 50)),
                gio_dong_diem_danh=_datetime.datetime.combine(hom_nay, _datetime.time(9, 30)),
                phong_hoc="A101",
                trang_thai=TrangThaiBuoiHoc.CHUA_BAT_DAU,
                nguoi_tao_id=tai_khoan_giang_vien.id,
            )
            phien.add(buoi_hoc_mau)

            # ----- Camera mau -----
            phien.add(
                Camera(
                    ten_camera="Camera Webcam May Tinh",
                    nguon="0",
                    vi_tri="Phong A101",
                    trang_thai=TrangThaiCamera.HOAT_DONG,
                )
            )

            # ----- Cau hinh mac dinh -----
            cau_hinh_ai = lay_cau_hinh()
            phien.add_all(
                [
                    CauHinh(
                        khoa_cau_hinh="NGUONG_DO_TUONG_DONG",
                        gia_tri=str(cau_hinh_ai.ai.nguong_do_tuong_dong),
                        mo_ta="Nguong cosine similarity de xac nhan cung mot nguoi",
                    ),
                    CauHinh(
                        khoa_cau_hinh="SO_LAN_DANG_NHAP_SAI_TOI_DA",
                        gia_tri=str(cau_hinh_ai.bao_mat.so_lan_dang_nhap_sai_toi_da),
                        mo_ta="So lan dang nhap sai toi da truoc khi khoa tai khoan",
                    ),
                    CauHinh(
                        khoa_cau_hinh="THOI_GIAN_KHOA_TAI_KHOAN_PHUT",
                        gia_tri=str(cau_hinh_ai.bao_mat.thoi_gian_khoa_tai_khoan_phut),
                        mo_ta="Thoi gian khoa tai khoan tinh bang phut",
                    ),
                    CauHinh(
                        khoa_cau_hinh="PHUT_TINH_DI_MUON",
                        gia_tri="15",
                        mo_ta="So phut sau gio bat dau duoc tinh la di muon",
                    ),
                ]
            )

            phien.commit()
        return True, "Da nap du lieu mau thanh cong."
    except Exception as loi:  # noqa: BLE001
        _bo_ghi_log.error("Loi khi nap du lieu mau: %s", loi)
        return False, f"Loi khi nap du lieu mau: {loi}"


def khoi_tao_toan_bo(nap_mau: bool = True) -> list[tuple[bool, str]]:
    """Chay tuan tu: tao database -> tao bang -> nap du lieu mau.

    Tra ve danh sach ket qua tung buoc de hien thi cho nguoi dung.
    """
    ket_qua: list[tuple[bool, str]] = []

    thanh_cong_db, thong_bao_db = tao_database_neu_chua_co()
    ket_qua.append((thanh_cong_db, thong_bao_db))
    if not thanh_cong_db:
        return ket_qua

    thanh_cong_bang, thong_bao_bang = tao_toan_bo_bang()
    ket_qua.append((thanh_cong_bang, thong_bao_bang))
    if not thanh_cong_bang:
        return ket_qua

    if nap_mau:
        thanh_cong_mau, thong_bao_mau = nap_du_lieu_mau()
        ket_qua.append((thanh_cong_mau, thong_bao_mau))

    return ket_qua
