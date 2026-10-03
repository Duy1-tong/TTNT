"""
Dich vu Danh Muc: quan ly du lieu dung chung — Khoa, Lop hanh chinh, Mon hoc,
Lop hoc phan va dang ky hoc phan cua sinh vien.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.co_so_du_lieu.ket_noi import mo_phien_lam_viec
from app.dich_vu.nhat_ky import ghi_nhat_ky
from app.dich_vu.phan_quyen import QuyenHeThong, yeu_cau_quyen
from app.mo_hinh.giang_vien import GiangVien
from app.mo_hinh.khoa import Khoa
from app.mo_hinh.lop_hoc import LopHoc
from app.mo_hinh.lop_mon_hoc import LopMonHoc
from app.mo_hinh.mon_hoc import MonHoc
from app.mo_hinh.sinh_vien import SinhVien
from app.mo_hinh.sinh_vien_lop import SinhVienLop, TrangThaiDangKy
from app.tien_ich.kiem_tra_du_lieu import kiem_tra_chuoi_khong_rong, kiem_tra_dinh_dang_ma_dinh_danh


class LoiDuLieuDanhMuc(Exception):
    """Loi nghiep vu lien quan den du lieu danh muc dung chung."""


@dataclass
class ThongTinKhoa:
    id: int
    ma_khoa: str
    ten_khoa: str
    mo_ta: str | None


@dataclass
class ThongTinLopHoc:
    id: int
    ma_lop: str
    ten_lop: str
    khoa_id: int
    ten_khoa: str | None
    khoa_hoc: str | None
    si_so: int


@dataclass
class ThongTinMonHoc:
    id: int
    ma_mon: str
    ten_mon: str
    so_tin_chi: int
    khoa_id: int | None


@dataclass
class ThongTinLopMonHoc:
    id: int
    ma_lop_mon: str
    mon_hoc_id: int
    ten_mon: str | None
    giang_vien_id: int | None
    ten_giang_vien: str | None
    hoc_ky: str
    nam_hoc: str
    si_so_dang_ky: int


# ---------------------------------------------------------------------
# KHOA
# ---------------------------------------------------------------------
def lay_danh_sach_khoa() -> list[ThongTinKhoa]:
    with mo_phien_lam_viec() as phien:
        danh_sach = phien.query(Khoa).order_by(Khoa.ten_khoa).all()
        return [ThongTinKhoa(id=k.id, ma_khoa=k.ma_khoa, ten_khoa=k.ten_khoa, mo_ta=k.mo_ta) for k in danh_sach]


def them_khoa(vai_tro_nguoi_thuc_hien: str, ma_khoa: str, ten_khoa: str, mo_ta: str | None = None) -> int:
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.QUAN_LY_KHOA)
    hop_le, thong_bao = kiem_tra_dinh_dang_ma_dinh_danh(ma_khoa, "Ma khoa")
    if not hop_le:
        raise LoiDuLieuDanhMuc(thong_bao)
    with mo_phien_lam_viec() as phien:
        if phien.query(Khoa).filter_by(ma_khoa=ma_khoa).first() is not None:
            raise LoiDuLieuDanhMuc(f"Ma khoa '{ma_khoa}' da ton tai.")
        khoa_moi = Khoa(ma_khoa=ma_khoa, ten_khoa=ten_khoa, mo_ta=mo_ta)
        phien.add(khoa_moi)
        phien.commit()
        ghi_nhat_ky(hanh_dong="THEM_KHOA", nguoi_dung_id=None, doi_tuong="khoa", doi_tuong_id=khoa_moi.id, noi_dung=f"Them khoa {ma_khoa}.")
        return khoa_moi.id


# ---------------------------------------------------------------------
# LOP HANH CHINH
# ---------------------------------------------------------------------
def lay_danh_sach_lop_hoc(khoa_id: int | None = None) -> list[ThongTinLopHoc]:
    with mo_phien_lam_viec() as phien:
        truy_van = phien.query(LopHoc)
        if khoa_id is not None:
            truy_van = truy_van.filter_by(khoa_id=khoa_id)
        danh_sach = truy_van.order_by(LopHoc.ten_lop).all()
        ket_qua = []
        for lop in danh_sach:
            khoa = phien.get(Khoa, lop.khoa_id)
            si_so = phien.query(SinhVien).filter_by(lop_id=lop.id).count()
            ket_qua.append(
                ThongTinLopHoc(
                    id=lop.id, ma_lop=lop.ma_lop, ten_lop=lop.ten_lop, khoa_id=lop.khoa_id,
                    ten_khoa=khoa.ten_khoa if khoa else None, khoa_hoc=lop.khoa_hoc, si_so=si_so,
                )
            )
        return ket_qua


def them_lop_hoc(
    vai_tro_nguoi_thuc_hien: str, ma_lop: str, ten_lop: str, khoa_id: int, khoa_hoc: str | None = None
) -> int:
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.QUAN_LY_LOP)
    hop_le, thong_bao = kiem_tra_dinh_dang_ma_dinh_danh(ma_lop, "Ma lop")
    if not hop_le:
        raise LoiDuLieuDanhMuc(thong_bao)
    with mo_phien_lam_viec() as phien:
        if phien.query(LopHoc).filter_by(ma_lop=ma_lop).first() is not None:
            raise LoiDuLieuDanhMuc(f"Ma lop '{ma_lop}' da ton tai.")
        if phien.get(Khoa, khoa_id) is None:
            raise LoiDuLieuDanhMuc("Khoa duoc chon khong ton tai.")
        lop_moi = LopHoc(ma_lop=ma_lop, ten_lop=ten_lop, khoa_id=khoa_id, khoa_hoc=khoa_hoc)
        phien.add(lop_moi)
        phien.commit()
        ghi_nhat_ky(hanh_dong="THEM_LOP_HOC", nguoi_dung_id=None, doi_tuong="lop_hoc", doi_tuong_id=lop_moi.id, noi_dung=f"Them lop hanh chinh {ma_lop}.")
        return lop_moi.id


# ---------------------------------------------------------------------
# MON HOC
# ---------------------------------------------------------------------
def lay_danh_sach_mon_hoc() -> list[ThongTinMonHoc]:
    with mo_phien_lam_viec() as phien:
        danh_sach = phien.query(MonHoc).order_by(MonHoc.ten_mon).all()
        return [
            ThongTinMonHoc(id=m.id, ma_mon=m.ma_mon, ten_mon=m.ten_mon, so_tin_chi=m.so_tin_chi, khoa_id=m.khoa_id)
            for m in danh_sach
        ]


def them_mon_hoc(
    vai_tro_nguoi_thuc_hien: str, ma_mon: str, ten_mon: str, so_tin_chi: int, khoa_id: int | None = None
) -> int:
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.QUAN_LY_MON_HOC)
    for hop_le, thong_bao in (
        kiem_tra_dinh_dang_ma_dinh_danh(ma_mon, "Ma mon"),
        kiem_tra_chuoi_khong_rong(ten_mon, "Ten mon"),
    ):
        if not hop_le:
            raise LoiDuLieuDanhMuc(thong_bao)
    if so_tin_chi <= 0:
        raise LoiDuLieuDanhMuc("So tin chi phai lon hon 0.")
    with mo_phien_lam_viec() as phien:
        if phien.query(MonHoc).filter_by(ma_mon=ma_mon).first() is not None:
            raise LoiDuLieuDanhMuc(f"Ma mon '{ma_mon}' da ton tai.")
        mon_moi = MonHoc(ma_mon=ma_mon, ten_mon=ten_mon, so_tin_chi=so_tin_chi, khoa_id=khoa_id)
        phien.add(mon_moi)
        phien.commit()
        ghi_nhat_ky(hanh_dong="THEM_MON_HOC", nguoi_dung_id=None, doi_tuong="mon_hoc", doi_tuong_id=mon_moi.id, noi_dung=f"Them mon hoc {ma_mon}.")
        return mon_moi.id


# ---------------------------------------------------------------------
# LOP HOC PHAN
# ---------------------------------------------------------------------
def lay_danh_sach_lop_mon_hoc(giang_vien_id: int | None = None) -> list[ThongTinLopMonHoc]:
    with mo_phien_lam_viec() as phien:
        truy_van = phien.query(LopMonHoc)
        if giang_vien_id is not None:
            truy_van = truy_van.filter_by(giang_vien_id=giang_vien_id)
        danh_sach = truy_van.order_by(LopMonHoc.nam_hoc.desc(), LopMonHoc.ma_lop_mon).all()
        ket_qua = []
        for lop_mon in danh_sach:
            mon = phien.get(MonHoc, lop_mon.mon_hoc_id)
            giang_vien = (
                phien.get(GiangVien, lop_mon.giang_vien_id) if lop_mon.giang_vien_id else None
            )
            si_so = phien.query(SinhVienLop).filter_by(
                lop_mon_hoc_id=lop_mon.id, trang_thai=TrangThaiDangKy.DANG_HOC
            ).count()
            ket_qua.append(
                ThongTinLopMonHoc(
                    id=lop_mon.id, ma_lop_mon=lop_mon.ma_lop_mon, mon_hoc_id=lop_mon.mon_hoc_id,
                    ten_mon=mon.ten_mon if mon else None, giang_vien_id=lop_mon.giang_vien_id,
                    ten_giang_vien=giang_vien.ho_ten if giang_vien else None,
                    hoc_ky=lop_mon.hoc_ky, nam_hoc=lop_mon.nam_hoc, si_so_dang_ky=si_so,
                )
            )
        return ket_qua


def them_lop_mon_hoc(
    vai_tro_nguoi_thuc_hien: str,
    ma_lop_mon: str,
    mon_hoc_id: int,
    giang_vien_id: int | None,
    hoc_ky: str,
    nam_hoc: str,
) -> int:
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.QUAN_LY_MON_HOC)
    with mo_phien_lam_viec() as phien:
        if phien.query(LopMonHoc).filter_by(ma_lop_mon=ma_lop_mon).first() is not None:
            raise LoiDuLieuDanhMuc(f"Ma lop hoc phan '{ma_lop_mon}' da ton tai.")
        if phien.get(MonHoc, mon_hoc_id) is None:
            raise LoiDuLieuDanhMuc("Mon hoc duoc chon khong ton tai.")
        lop_mon_moi = LopMonHoc(
            ma_lop_mon=ma_lop_mon, mon_hoc_id=mon_hoc_id, giang_vien_id=giang_vien_id,
            hoc_ky=hoc_ky, nam_hoc=nam_hoc,
        )
        phien.add(lop_mon_moi)
        phien.commit()
        ghi_nhat_ky(hanh_dong="THEM_LOP_MON_HOC", nguoi_dung_id=None, doi_tuong="lop_mon_hoc", doi_tuong_id=lop_mon_moi.id, noi_dung=f"Mo lop hoc phan {ma_lop_mon}.")
        return lop_mon_moi.id


def dang_ky_sinh_vien_vao_lop_mon_hoc(
    vai_tro_nguoi_thuc_hien: str, sinh_vien_id: int, lop_mon_hoc_id: int
) -> None:
    """Dang ky mot sinh vien vao mot lop hoc phan. Chong dang ky trung."""
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.QUAN_LY_MON_HOC)
    with mo_phien_lam_viec() as phien:
        da_dang_ky = phien.query(SinhVienLop).filter_by(
            sinh_vien_id=sinh_vien_id, lop_mon_hoc_id=lop_mon_hoc_id
        ).first()
        if da_dang_ky is not None:
            raise LoiDuLieuDanhMuc("Sinh vien nay da dang ky lop hoc phan nay roi.")
        phien.add(
            SinhVienLop(
                sinh_vien_id=sinh_vien_id, lop_mon_hoc_id=lop_mon_hoc_id, trang_thai=TrangThaiDangKy.DANG_HOC
            )
        )
        phien.commit()
