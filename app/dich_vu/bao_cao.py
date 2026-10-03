"""
Dich vu Bao Cao: tong hop thong ke diem danh theo sinh vien / lop / mon /
ngay / thang / hoc ky, va xuat ra file Excel hoac PDF.
"""

from __future__ import annotations

import datetime as _datetime
from dataclasses import dataclass
from pathlib import Path

from app.cau_hinh.cai_dat import lay_cau_hinh
from app.co_so_du_lieu.ket_noi import mo_phien_lam_viec
from app.dich_vu.nhat_ky import ghi_nhat_ky
from app.dich_vu.phan_quyen import QuyenHeThong, yeu_cau_quyen
from app.mo_hinh.buoi_hoc import BuoiHoc
from app.mo_hinh.diem_danh import DiemDanh, TrangThaiDiemDanh
from app.mo_hinh.lop_mon_hoc import LopMonHoc
from app.mo_hinh.mon_hoc import MonHoc
from app.mo_hinh.sinh_vien import SinhVien
from app.mo_hinh.sinh_vien_lop import SinhVienLop, TrangThaiDangKy
from app.tien_ich.xuat_excel import xuat_bang_du_lieu_ra_excel
from app.tien_ich.xuat_pdf import xuat_bang_du_lieu_ra_pdf


@dataclass
class DongBaoCaoSinhVien:
    """Mot dong thong ke diem danh cua mot sinh vien trong lop hoc phan."""

    ma_sinh_vien: str
    ho_ten: str
    so_buoi_co_mat: int
    so_buoi_di_muon: int
    so_buoi_vang: int
    so_buoi_co_phep: int
    tong_so_buoi: int
    ty_le_co_mat_phan_tram: float


def _lay_khoang_thoi_gian_theo_thang(nam: int, thang: int) -> tuple[_datetime.date, _datetime.date]:
    """Tra ve (ngay dau thang, ngay cuoi thang) cho mot thang/nam cho truoc."""
    ngay_dau = _datetime.date(nam, thang, 1)
    if thang == 12:
        ngay_cuoi = _datetime.date(nam, 12, 31)
    else:
        ngay_cuoi = _datetime.date(nam, thang + 1, 1) - _datetime.timedelta(days=1)
    return ngay_dau, ngay_cuoi


def bao_cao_theo_lop_mon_hoc(
    vai_tro_nguoi_thuc_hien: str,
    lop_mon_hoc_id: int,
    tu_ngay: _datetime.date | None = None,
    den_ngay: _datetime.date | None = None,
) -> list[DongBaoCaoSinhVien]:
    """Thong ke diem danh cua toan bo sinh vien trong mot lop hoc phan.

    Co the loc theo khoang thoi gian (dung chung cho bao cao theo ngay/thang/
    hoc ky — chi khac nhau o cach nguoi dung chon `tu_ngay`/`den_ngay`).
    """
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.XUAT_BAO_CAO)

    with mo_phien_lam_viec() as phien:
        truy_van_buoi_hoc = phien.query(BuoiHoc.id).filter(
            BuoiHoc.lop_mon_hoc_id == lop_mon_hoc_id
        )
        if tu_ngay is not None:
            truy_van_buoi_hoc = truy_van_buoi_hoc.filter(BuoiHoc.ngay_hoc >= tu_ngay)
        if den_ngay is not None:
            truy_van_buoi_hoc = truy_van_buoi_hoc.filter(BuoiHoc.ngay_hoc <= den_ngay)
        cac_buoi_hoc_id = [hang[0] for hang in truy_van_buoi_hoc.all()]
        tong_so_buoi = len(cac_buoi_hoc_id)

        cac_sinh_vien = (
            phien.query(SinhVien)
            .join(SinhVienLop, SinhVienLop.sinh_vien_id == SinhVien.id)
            .filter(
                SinhVienLop.lop_mon_hoc_id == lop_mon_hoc_id,
                SinhVienLop.trang_thai == TrangThaiDangKy.DANG_HOC,
            )
            .order_by(SinhVien.ho_ten)
            .all()
        )

        ket_qua: list[DongBaoCaoSinhVien] = []
        for sinh_vien in cac_sinh_vien:
            if cac_buoi_hoc_id:
                cac_ban_ghi = (
                    phien.query(DiemDanh)
                    .filter(
                        DiemDanh.sinh_vien_id == sinh_vien.id,
                        DiemDanh.buoi_hoc_id.in_(cac_buoi_hoc_id),
                    )
                    .all()
                )
            else:
                cac_ban_ghi = []

            so_co_mat = sum(1 for bg in cac_ban_ghi if bg.trang_thai == TrangThaiDiemDanh.CO_MAT)
            so_di_muon = sum(1 for bg in cac_ban_ghi if bg.trang_thai == TrangThaiDiemDanh.DI_MUON)
            so_vang = sum(1 for bg in cac_ban_ghi if bg.trang_thai == TrangThaiDiemDanh.VANG)
            so_co_phep = sum(1 for bg in cac_ban_ghi if bg.trang_thai == TrangThaiDiemDanh.CO_PHEP)
            # Buoi hoc chua co ban ghi nao cung duoc tinh la vang cho toi khi buoi hoc ket thuc.
            so_chua_diem_danh = max(tong_so_buoi - len(cac_ban_ghi), 0)
            so_vang_tong = so_vang + so_chua_diem_danh

            so_buoi_tinh_ty_le = tong_so_buoi if tong_so_buoi > 0 else 1
            ty_le_co_mat = round(
                (so_co_mat + so_di_muon + so_co_phep) / so_buoi_tinh_ty_le * 100, 1
            )

            ket_qua.append(
                DongBaoCaoSinhVien(
                    ma_sinh_vien=sinh_vien.ma_sinh_vien,
                    ho_ten=sinh_vien.ho_ten,
                    so_buoi_co_mat=so_co_mat,
                    so_buoi_di_muon=so_di_muon,
                    so_buoi_vang=so_vang_tong,
                    so_buoi_co_phep=so_co_phep,
                    tong_so_buoi=tong_so_buoi,
                    ty_le_co_mat_phan_tram=ty_le_co_mat,
                )
            )
        return ket_qua


def bao_cao_theo_sinh_vien(
    vai_tro_nguoi_thuc_hien: str,
    sinh_vien_id: int,
    tu_ngay: _datetime.date | None = None,
    den_ngay: _datetime.date | None = None,
) -> list[dict]:
    """Bao cao chi tiet lich su diem danh cua MOT sinh vien theo tung mon hoc."""
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.XUAT_BAO_CAO)

    with mo_phien_lam_viec() as phien:
        truy_van = (
            phien.query(DiemDanh, BuoiHoc, LopMonHoc, MonHoc)
            .join(BuoiHoc, DiemDanh.buoi_hoc_id == BuoiHoc.id)
            .join(LopMonHoc, BuoiHoc.lop_mon_hoc_id == LopMonHoc.id)
            .join(MonHoc, LopMonHoc.mon_hoc_id == MonHoc.id)
            .filter(DiemDanh.sinh_vien_id == sinh_vien_id)
        )
        if tu_ngay is not None:
            truy_van = truy_van.filter(BuoiHoc.ngay_hoc >= tu_ngay)
        if den_ngay is not None:
            truy_van = truy_van.filter(BuoiHoc.ngay_hoc <= den_ngay)

        danh_sach = truy_van.order_by(BuoiHoc.ngay_hoc.desc()).all()
        return [
            {
                "ngay_hoc": buoi.ngay_hoc,
                "ten_mon": mon.ten_mon,
                "ma_lop_mon": lop_mon.ma_lop_mon,
                "trang_thai": diem_danh.trang_thai.value,
                "phuong_thuc": diem_danh.phuong_thuc.value,
                "thoi_gian_diem_danh": diem_danh.thoi_gian_diem_danh,
            }
            for diem_danh, buoi, lop_mon, mon in danh_sach
        ]


def bao_cao_theo_thang(
    vai_tro_nguoi_thuc_hien: str, lop_mon_hoc_id: int, nam: int, thang: int
) -> list[DongBaoCaoSinhVien]:
    """Bao cao diem danh cua mot lop hoc phan trong mot thang cu the."""
    ngay_dau, ngay_cuoi = _lay_khoang_thoi_gian_theo_thang(nam, thang)
    return bao_cao_theo_lop_mon_hoc(
        vai_tro_nguoi_thuc_hien, lop_mon_hoc_id, tu_ngay=ngay_dau, den_ngay=ngay_cuoi
    )


def bao_cao_theo_hoc_ky(
    vai_tro_nguoi_thuc_hien: str,
    lop_mon_hoc_id: int,
    tu_ngay: _datetime.date,
    den_ngay: _datetime.date,
) -> list[DongBaoCaoSinhVien]:
    """Bao cao diem danh cua mot lop hoc phan trong mot khoang thoi gian (hoc ky)."""
    return bao_cao_theo_lop_mon_hoc(
        vai_tro_nguoi_thuc_hien, lop_mon_hoc_id, tu_ngay=tu_ngay, den_ngay=den_ngay
    )


# ---------------------------------------------------------------------
# XUAT FILE
# ---------------------------------------------------------------------
_TEN_CAC_COT_BAO_CAO_LOP = [
    "Ma sinh vien",
    "Ho ten",
    "So buoi co mat",
    "So buoi di muon",
    "So buoi vang",
    "So buoi co phep",
    "Tong so buoi",
    "Ty le co mat (%)",
]


def _chuyen_bao_cao_lop_thanh_hang(du_lieu: list[DongBaoCaoSinhVien]) -> list[list]:
    return [
        [
            dong.ma_sinh_vien,
            dong.ho_ten,
            dong.so_buoi_co_mat,
            dong.so_buoi_di_muon,
            dong.so_buoi_vang,
            dong.so_buoi_co_phep,
            dong.tong_so_buoi,
            dong.ty_le_co_mat_phan_tram,
        ]
        for dong in du_lieu
    ]


def xuat_bao_cao_lop_ra_excel(
    du_lieu: list[DongBaoCaoSinhVien],
    tieu_de: str,
    ten_file: str,
    nguoi_thuc_hien_id: int | None = None,
) -> Path:
    """Xuat bao cao diem danh theo lop hoc phan ra file Excel trong thu muc bao_cao/."""
    cau_hinh = lay_cau_hinh()
    duong_dan = cau_hinh.duong_dan_tuyet_doi(cau_hinh.ung_dung.thu_muc_bao_cao) / ten_file
    ket_qua = xuat_bang_du_lieu_ra_excel(
        duong_dan, tieu_de, _TEN_CAC_COT_BAO_CAO_LOP, _chuyen_bao_cao_lop_thanh_hang(du_lieu)
    )
    ghi_nhat_ky(
        hanh_dong="XUAT_BAO_CAO_EXCEL",
        nguoi_dung_id=nguoi_thuc_hien_id,
        noi_dung=f"Xuat bao cao Excel: {ten_file}.",
    )
    return ket_qua


def xuat_bao_cao_lop_ra_pdf(
    du_lieu: list[DongBaoCaoSinhVien],
    tieu_de: str,
    ten_file: str,
    nguoi_thuc_hien_id: int | None = None,
) -> Path:
    """Xuat bao cao diem danh theo lop hoc phan ra file PDF trong thu muc bao_cao/."""
    cau_hinh = lay_cau_hinh()
    duong_dan = cau_hinh.duong_dan_tuyet_doi(cau_hinh.ung_dung.thu_muc_bao_cao) / ten_file
    ket_qua = xuat_bang_du_lieu_ra_pdf(
        duong_dan,
        tieu_de,
        _TEN_CAC_COT_BAO_CAO_LOP,
        _chuyen_bao_cao_lop_thanh_hang(du_lieu),
        ghi_chu_cuoi_trang=f"Xuat luc: {_datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
    )
    ghi_nhat_ky(
        hanh_dong="XUAT_BAO_CAO_PDF",
        nguoi_dung_id=nguoi_thuc_hien_id,
        noi_dung=f"Xuat bao cao PDF: {ten_file}.",
    )
    return ket_qua
