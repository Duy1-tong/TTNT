"""
Dich vu Diem Danh: tao/mo/dong buoi hoc, thuc hien diem danh bang khuon mat
hoac thu cong, chong diem danh trung, va truy van lich su diem danh.
"""

from __future__ import annotations

import datetime as _datetime
import logging
from dataclasses import dataclass

import numpy as np
from sqlalchemy.exc import IntegrityError

from app.co_so_du_lieu.ket_noi import mo_phien_lam_viec
from app.dich_vu.khuon_mat import lay_bo_nhan_dien, lay_toan_bo_embedding_de_nhan_dien
from app.dich_vu.nhat_ky import ghi_nhat_ky
from app.dich_vu.phan_quyen import QuyenHeThong, yeu_cau_quyen
from app.mo_hinh.buoi_hoc import BuoiHoc, TrangThaiBuoiHoc
from app.mo_hinh.diem_danh import DiemDanh, PhuongThucDiemDanh, TrangThaiDiemDanh
from app.mo_hinh.sinh_vien import SinhVien
from app.mo_hinh.sinh_vien_lop import SinhVienLop, TrangThaiDangKy

_bo_ghi_log = logging.getLogger(__name__)

PHUT_DI_MUON_CHO_PHEP_MAC_DINH = 15


class LoiDiemDanh(Exception):
    """Loi nghiep vu lien quan den diem danh."""


@dataclass
class ThongTinBuoiHoc:
    """DTO the hien mot buoi hoc."""

    id: int
    lop_mon_hoc_id: int
    ma_lop_mon: str | None
    ngay_hoc: _datetime.date
    gio_bat_dau: _datetime.time
    gio_ket_thuc: _datetime.time
    phong_hoc: str | None
    trang_thai: str
    si_so_da_diem_danh: int


@dataclass
class ThongTinDiemDanh:
    """DTO the hien mot ban ghi diem danh, dung de hien thi danh sach/lich su."""

    id: int
    buoi_hoc_id: int
    sinh_vien_id: int
    ma_sinh_vien: str
    ho_ten_sinh_vien: str
    thoi_gian_diem_danh: _datetime.datetime | _datetime.date
    trang_thai: str
    phuong_thuc: str
    do_tuong_dong: float | None
    ghi_chu: str | None


@dataclass
class KetQuaDiemDanhBangKhuonMat:
    """Ket qua tra ve sau khi thu diem danh mot khung hinh camera bang khuon mat."""

    thanh_cong: bool
    sinh_vien_id: int | None
    ma_sinh_vien: str | None
    ho_ten_sinh_vien: str | None
    do_tuong_dong: float | None
    thong_bao: str


def _cong_phut(gio: _datetime.time, so_phut: int) -> _datetime.time:
    """Cong them mot so phut vao mot doi tuong time, tra ve time moi (khong qua ngay)."""
    thoi_diem = _datetime.datetime.combine(_datetime.date.today(), gio) + _datetime.timedelta(
        minutes=so_phut
    )
    return thoi_diem.time()


# ---------------------------------------------------------------------
# QUAN LY BUOI HOC
# ---------------------------------------------------------------------
def tao_buoi_hoc(
    vai_tro_nguoi_thuc_hien: str,
    lop_mon_hoc_id: int,
    ngay_hoc: _datetime.date,
    gio_bat_dau: _datetime.time,
    gio_ket_thuc: _datetime.time,
    phong_hoc: str | None,
    phut_mo_diem_danh_truoc_gio_hoc: int = 10,
    nguoi_thuc_hien_id: int | None = None,
) -> int:
    """Tao mot buoi hoc moi cho mot lop hoc phan. Tra ve id buoi hoc vua tao."""
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.QUAN_LY_BUOI_HOC)
    if gio_ket_thuc <= gio_bat_dau:
        raise LoiDiemDanh("Gio ket thuc phai sau gio bat dau.")

    thoi_diem_bat_dau = _datetime.datetime.combine(ngay_hoc, gio_bat_dau)
    gio_mo_diem_danh = thoi_diem_bat_dau - _datetime.timedelta(
        minutes=phut_mo_diem_danh_truoc_gio_hoc
    )
    gio_dong_diem_danh = _datetime.datetime.combine(ngay_hoc, gio_ket_thuc)

    with mo_phien_lam_viec() as phien:
        buoi_hoc_moi = BuoiHoc(
            lop_mon_hoc_id=lop_mon_hoc_id,
            ngay_hoc=ngay_hoc,
            gio_bat_dau=gio_bat_dau,
            gio_ket_thuc=gio_ket_thuc,
            gio_mo_diem_danh=gio_mo_diem_danh,
            gio_dong_diem_danh=gio_dong_diem_danh,
            phong_hoc=phong_hoc,
            trang_thai=TrangThaiBuoiHoc.CHUA_BAT_DAU,
            nguoi_tao_id=nguoi_thuc_hien_id,
        )
        phien.add(buoi_hoc_moi)
        phien.commit()

        ghi_nhat_ky(
            hanh_dong="TAO_BUOI_HOC",
            nguoi_dung_id=nguoi_thuc_hien_id,
            doi_tuong="buoi_hoc",
            doi_tuong_id=buoi_hoc_moi.id,
            noi_dung=f"Tao buoi hoc ngay {ngay_hoc} cho lop hoc phan id={lop_mon_hoc_id}.",
        )
        return buoi_hoc_moi.id


def lay_danh_sach_buoi_hoc(
    lop_mon_hoc_id: int | None = None, ngay_hoc: _datetime.date | None = None
) -> list[ThongTinBuoiHoc]:
    """Lay danh sach buoi hoc, co the loc theo lop hoc phan va/hoac ngay hoc."""
    from app.mo_hinh.lop_mon_hoc import LopMonHoc

    with mo_phien_lam_viec() as phien:
        truy_van = phien.query(BuoiHoc)
        if lop_mon_hoc_id is not None:
            truy_van = truy_van.filter(BuoiHoc.lop_mon_hoc_id == lop_mon_hoc_id)
        if ngay_hoc is not None:
            truy_van = truy_van.filter(BuoiHoc.ngay_hoc == ngay_hoc)
        danh_sach = truy_van.order_by(BuoiHoc.ngay_hoc.desc(), BuoiHoc.gio_bat_dau.desc()).all()

        ket_qua: list[ThongTinBuoiHoc] = []
        for buoi in danh_sach:
            lop_mon = phien.get(LopMonHoc, buoi.lop_mon_hoc_id)
            so_da_diem_danh = (
                phien.query(DiemDanh).filter(DiemDanh.buoi_hoc_id == buoi.id).count()
            )
            ket_qua.append(
                ThongTinBuoiHoc(
                    id=buoi.id,
                    lop_mon_hoc_id=buoi.lop_mon_hoc_id,
                    ma_lop_mon=lop_mon.ma_lop_mon if lop_mon else None,
                    ngay_hoc=buoi.ngay_hoc,
                    gio_bat_dau=buoi.gio_bat_dau,
                    gio_ket_thuc=buoi.gio_ket_thuc,
                    phong_hoc=buoi.phong_hoc,
                    trang_thai=buoi.trang_thai.value,
                    si_so_da_diem_danh=so_da_diem_danh,
                )
            )
        return ket_qua


def mo_diem_danh_cho_buoi_hoc(
    vai_tro_nguoi_thuc_hien: str, buoi_hoc_id: int, nguoi_thuc_hien_id: int | None = None
) -> None:
    """Chuyen trang thai buoi hoc sang DANG_DIEM_DANH."""
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.QUAN_LY_BUOI_HOC)
    with mo_phien_lam_viec() as phien:
        buoi_hoc = phien.get(BuoiHoc, buoi_hoc_id)
        if buoi_hoc is None:
            raise LoiDiemDanh("Khong tim thay buoi hoc.")
        buoi_hoc.trang_thai = TrangThaiBuoiHoc.DANG_DIEM_DANH
        phien.commit()
        ghi_nhat_ky(
            hanh_dong="MO_DIEM_DANH",
            nguoi_dung_id=nguoi_thuc_hien_id,
            doi_tuong="buoi_hoc",
            doi_tuong_id=buoi_hoc_id,
            noi_dung="Mo diem danh cho buoi hoc.",
        )


def dong_diem_danh_cho_buoi_hoc(
    vai_tro_nguoi_thuc_hien: str, buoi_hoc_id: int, nguoi_thuc_hien_id: int | None = None
) -> None:
    """Chuyen trang thai buoi hoc sang DA_KET_THUC va tu dong danh dau VANG cho
    nhung sinh vien dang ky hoc phan nhung chua co ban ghi diem danh nao."""
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.QUAN_LY_BUOI_HOC)
    with mo_phien_lam_viec() as phien:
        buoi_hoc = phien.get(BuoiHoc, buoi_hoc_id)
        if buoi_hoc is None:
            raise LoiDiemDanh("Khong tim thay buoi hoc.")

        cac_sinh_vien_id_dang_ky = [
            hang[0]
            for hang in phien.query(SinhVienLop.sinh_vien_id)
            .filter(
                SinhVienLop.lop_mon_hoc_id == buoi_hoc.lop_mon_hoc_id,
                SinhVienLop.trang_thai == TrangThaiDangKy.DANG_HOC,
            )
            .all()
        ]
        cac_sinh_vien_id_da_diem_danh = {
            hang[0]
            for hang in phien.query(DiemDanh.sinh_vien_id)
            .filter(DiemDanh.buoi_hoc_id == buoi_hoc_id)
            .all()
        }
        for sinh_vien_id in cac_sinh_vien_id_dang_ky:
            if sinh_vien_id in cac_sinh_vien_id_da_diem_danh:
                continue
            phien.add(
                DiemDanh(
                    buoi_hoc_id=buoi_hoc_id,
                    sinh_vien_id=sinh_vien_id,
                    trang_thai=TrangThaiDiemDanh.VANG,
                    phuong_thuc=PhuongThucDiemDanh.THU_CONG,
                    ghi_chu="Tu dong danh dau vang khi ket thuc buoi hoc.",
                    nguoi_thuc_hien_id=nguoi_thuc_hien_id,
                )
            )

        buoi_hoc.trang_thai = TrangThaiBuoiHoc.DA_KET_THUC
        phien.commit()

        ghi_nhat_ky(
            hanh_dong="DONG_DIEM_DANH",
            nguoi_dung_id=nguoi_thuc_hien_id,
            doi_tuong="buoi_hoc",
            doi_tuong_id=buoi_hoc_id,
            noi_dung="Dong diem danh, tu dong danh dau VANG cho sinh vien chua diem danh.",
        )


# ---------------------------------------------------------------------
# DIEM DANH BANG KHUON MAT
# ---------------------------------------------------------------------
def diem_danh_bang_khuon_mat(
    buoi_hoc_id: int,
    danh_sach_khung_hinh_gan_nhat: list[np.ndarray],
    nguong_do_tuong_dong: float,
    nguoi_thuc_hien_id: int | None = None,
    yeu_cau_kiem_tra_nguoi_that: bool = True,
) -> KetQuaDiemDanhBangKhuonMat:
    """Chay pipeline AI tren khung hinh camera va tu dong tao ban ghi diem danh
    neu nhan dien thanh cong. Tu dong chong diem danh trung (UNIQUE constraint)
    va tu dong xac dinh CO_MAT/DI_MUON dua theo gio bat dau buoi hoc.
    """
    with mo_phien_lam_viec() as phien:
        buoi_hoc = phien.get(BuoiHoc, buoi_hoc_id)
        if buoi_hoc is None:
            return KetQuaDiemDanhBangKhuonMat(
                False, None, None, None, None, "Khong tim thay buoi hoc."
            )
        if buoi_hoc.trang_thai != TrangThaiBuoiHoc.DANG_DIEM_DANH:
            return KetQuaDiemDanhBangKhuonMat(
                False, None, None, None, None,
                "Buoi hoc hien khong o trang thai dang mo diem danh.",
            )
        thoi_gian_hien_tai = _datetime.datetime.now()
        if buoi_hoc.gio_mo_diem_danh and thoi_gian_hien_tai < buoi_hoc.gio_mo_diem_danh:
            return KetQuaDiemDanhBangKhuonMat(
                False, None, None, None, None, "Chua den gio mo diem danh cho buoi hoc nay."
            )
        if buoi_hoc.gio_dong_diem_danh and thoi_gian_hien_tai > buoi_hoc.gio_dong_diem_danh:
            return KetQuaDiemDanhBangKhuonMat(
                False, None, None, None, None, "Da qua gio dong diem danh cho buoi hoc nay."
            )
        lop_mon_hoc_id = buoi_hoc.lop_mon_hoc_id
        gio_bat_dau_buoi_hoc = buoi_hoc.gio_bat_dau

    danh_sach_embedding = lay_toan_bo_embedding_de_nhan_dien(lop_mon_hoc_id=lop_mon_hoc_id)
    if not danh_sach_embedding:
        return KetQuaDiemDanhBangKhuonMat(
            False, None, None, None, None,
            "Chua co sinh vien nao trong lop hoc phan nay dang ky khuon mat.",
        )

    bo_nhan_dien = lay_bo_nhan_dien()
    ket_qua_nhan_dien = bo_nhan_dien.nhan_dien_de_diem_danh(
        danh_sach_khung_hinh_gan_nhat=danh_sach_khung_hinh_gan_nhat,
        danh_sach_embedding_da_dang_ky=danh_sach_embedding,
        nguong_do_tuong_dong=nguong_do_tuong_dong,
        yeu_cau_kiem_tra_nguoi_that=yeu_cau_kiem_tra_nguoi_that,
    )

    if ket_qua_nhan_dien.ket_qua_so_sanh is None:
        return KetQuaDiemDanhBangKhuonMat(
            False, None, None, None, None, ket_qua_nhan_dien.thong_bao
        )

    sinh_vien_id = ket_qua_nhan_dien.ket_qua_so_sanh.sinh_vien_id
    do_tuong_dong = ket_qua_nhan_dien.ket_qua_so_sanh.do_tuong_dong

    with mo_phien_lam_viec() as phien:
        sinh_vien = phien.get(SinhVien, sinh_vien_id)
        if sinh_vien is None:
            return KetQuaDiemDanhBangKhuonMat(
                False, None, None, None, do_tuong_dong, "Sinh vien khong con ton tai trong he thong."
            )

        da_dang_ky_lop = (
            phien.query(SinhVienLop)
            .filter(
                SinhVienLop.sinh_vien_id == sinh_vien_id,
                SinhVienLop.lop_mon_hoc_id == lop_mon_hoc_id,
                SinhVienLop.trang_thai == TrangThaiDangKy.DANG_HOC,
            )
            .first()
        )
        if da_dang_ky_lop is None:
            return KetQuaDiemDanhBangKhuonMat(
                False, sinh_vien_id, sinh_vien.ma_sinh_vien, sinh_vien.ho_ten, do_tuong_dong,
                f"Sinh vien {sinh_vien.ma_sinh_vien} khong thuoc lop hoc phan nay.",
            )

        ban_ghi_da_co = (
            phien.query(DiemDanh)
            .filter(DiemDanh.buoi_hoc_id == buoi_hoc_id, DiemDanh.sinh_vien_id == sinh_vien_id)
            .first()
        )
        if ban_ghi_da_co is not None:
            return KetQuaDiemDanhBangKhuonMat(
                False, sinh_vien_id, sinh_vien.ma_sinh_vien, sinh_vien.ho_ten, do_tuong_dong,
                f"Sinh vien {sinh_vien.ma_sinh_vien} da diem danh truoc do luc "
                f"{ban_ghi_da_co.thoi_gian_diem_danh.strftime('%H:%M:%S')}.",
            )

        thoi_gian_hien_tai = _datetime.datetime.now()
        trang_thai_diem_danh = TrangThaiDiemDanh.CO_MAT
        if thoi_gian_hien_tai.time() > _cong_phut(
            gio_bat_dau_buoi_hoc, PHUT_DI_MUON_CHO_PHEP_MAC_DINH
        ):
            trang_thai_diem_danh = TrangThaiDiemDanh.DI_MUON

        try:
            ban_ghi_moi = DiemDanh(
                buoi_hoc_id=buoi_hoc_id,
                sinh_vien_id=sinh_vien_id,
                thoi_gian_diem_danh=thoi_gian_hien_tai,
                trang_thai=trang_thai_diem_danh,
                phuong_thuc=PhuongThucDiemDanh.KHUON_MAT,
                do_tuong_dong=do_tuong_dong,
                nguoi_thuc_hien_id=nguoi_thuc_hien_id,
            )
            phien.add(ban_ghi_moi)
            phien.commit()
        except IntegrityError:
            phien.rollback()
            return KetQuaDiemDanhBangKhuonMat(
                False, sinh_vien_id, sinh_vien.ma_sinh_vien, sinh_vien.ho_ten, do_tuong_dong,
                "Sinh vien nay vua duoc diem danh (trung luc). Vui long thu lai.",
            )

        ghi_nhat_ky(
            hanh_dong="DIEM_DANH",
            nguoi_dung_id=nguoi_thuc_hien_id,
            doi_tuong="diem_danh",
            doi_tuong_id=ban_ghi_moi.id,
            noi_dung=(
                f"Diem danh bang khuon mat: sinh vien {sinh_vien.ma_sinh_vien} - "
                f"{sinh_vien.ho_ten}, do tuong dong={do_tuong_dong:.3f}, "
                f"trang thai={trang_thai_diem_danh.value}."
            ),
        )

        return KetQuaDiemDanhBangKhuonMat(
            True, sinh_vien_id, sinh_vien.ma_sinh_vien, sinh_vien.ho_ten, do_tuong_dong,
            f"Diem danh thanh cong: {sinh_vien.ho_ten} ({trang_thai_diem_danh.value}).",
        )


# ---------------------------------------------------------------------
# DIEM DANH THU CONG
# ---------------------------------------------------------------------
def diem_danh_thu_cong(
    vai_tro_nguoi_thuc_hien: str,
    buoi_hoc_id: int,
    sinh_vien_id: int,
    trang_thai: TrangThaiDiemDanh,
    ghi_chu: str | None = None,
    nguoi_thuc_hien_id: int | None = None,
) -> int:
    """Giang vien/Admin diem danh thu cong (hoac sua ket qua diem danh) cho mot sinh vien.

    Neu sinh vien da co ban ghi diem danh cho buoi hoc nay, ham nay se CAP NHAT
    ban ghi hien co (khong tao ban ghi trung nho co UNIQUE constraint).
    """
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.SUA_DIEM_DANH_THU_CONG)

    with mo_phien_lam_viec() as phien:
        buoi_hoc = phien.get(BuoiHoc, buoi_hoc_id)
        if buoi_hoc is None:
            raise LoiDiemDanh("Khong tim thay buoi hoc.")

        da_dang_ky_lop = (
            phien.query(SinhVienLop)
            .filter(
                SinhVienLop.sinh_vien_id == sinh_vien_id,
                SinhVienLop.lop_mon_hoc_id == buoi_hoc.lop_mon_hoc_id,
            )
            .first()
        )
        if da_dang_ky_lop is None:
            raise LoiDiemDanh("Sinh vien nay khong thuoc lop hoc phan cua buoi hoc.")

        ban_ghi = (
            phien.query(DiemDanh)
            .filter(DiemDanh.buoi_hoc_id == buoi_hoc_id, DiemDanh.sinh_vien_id == sinh_vien_id)
            .first()
        )
        if ban_ghi is None:
            ban_ghi = DiemDanh(
                buoi_hoc_id=buoi_hoc_id,
                sinh_vien_id=sinh_vien_id,
                trang_thai=trang_thai,
                phuong_thuc=PhuongThucDiemDanh.THU_CONG,
                ghi_chu=ghi_chu,
                nguoi_thuc_hien_id=nguoi_thuc_hien_id,
            )
            phien.add(ban_ghi)
            hanh_dong_log = "DIEM_DANH"
        else:
            ban_ghi.trang_thai = trang_thai
            ban_ghi.phuong_thuc = PhuongThucDiemDanh.THU_CONG
            ban_ghi.ghi_chu = ghi_chu
            ban_ghi.nguoi_thuc_hien_id = nguoi_thuc_hien_id
            hanh_dong_log = "SUA_DIEM_DANH"

        phien.commit()

        ghi_nhat_ky(
            hanh_dong=hanh_dong_log,
            nguoi_dung_id=nguoi_thuc_hien_id,
            doi_tuong="diem_danh",
            doi_tuong_id=ban_ghi.id,
            noi_dung=(
                f"Diem danh thu cong sinh vien id={sinh_vien_id} cho buoi hoc id={buoi_hoc_id}: "
                f"trang thai={trang_thai.value}."
            ),
        )
        return ban_ghi.id


# ---------------------------------------------------------------------
# TRUY VAN LICH SU
# ---------------------------------------------------------------------
def lay_danh_sach_diem_danh_theo_buoi_hoc(buoi_hoc_id: int) -> list[ThongTinDiemDanh]:
    """Lay danh sach diem danh cua toan bo sinh vien dang ky mot buoi hoc cu the."""
    with mo_phien_lam_viec() as phien:
        buoi_hoc = phien.get(BuoiHoc, buoi_hoc_id)
        if buoi_hoc is None:
            return []

        cac_dang_ky = (
            phien.query(SinhVienLop)
            .filter(
                SinhVienLop.lop_mon_hoc_id == buoi_hoc.lop_mon_hoc_id,
                SinhVienLop.trang_thai == TrangThaiDangKy.DANG_HOC,
            )
            .all()
        )
        cac_ban_ghi_diem_danh = {
            bg.sinh_vien_id: bg
            for bg in phien.query(DiemDanh).filter(DiemDanh.buoi_hoc_id == buoi_hoc_id).all()
        }

        ket_qua: list[ThongTinDiemDanh] = []
        for dang_ky in cac_dang_ky:
            sinh_vien = phien.get(SinhVien, dang_ky.sinh_vien_id)
            if sinh_vien is None:
                continue
            ban_ghi = cac_ban_ghi_diem_danh.get(sinh_vien.id)
            if ban_ghi is not None:
                ket_qua.append(
                    ThongTinDiemDanh(
                        id=ban_ghi.id,
                        buoi_hoc_id=buoi_hoc_id,
                        sinh_vien_id=sinh_vien.id,
                        ma_sinh_vien=sinh_vien.ma_sinh_vien,
                        ho_ten_sinh_vien=sinh_vien.ho_ten,
                        thoi_gian_diem_danh=ban_ghi.thoi_gian_diem_danh,
                        trang_thai=ban_ghi.trang_thai.value,
                        phuong_thuc=ban_ghi.phuong_thuc.value,
                        do_tuong_dong=ban_ghi.do_tuong_dong,
                        ghi_chu=ban_ghi.ghi_chu,
                    )
                )
            else:
                ket_qua.append(
                    ThongTinDiemDanh(
                        id=0,
                        buoi_hoc_id=buoi_hoc_id,
                        sinh_vien_id=sinh_vien.id,
                        ma_sinh_vien=sinh_vien.ma_sinh_vien,
                        ho_ten_sinh_vien=sinh_vien.ho_ten,
                        thoi_gian_diem_danh=buoi_hoc.ngay_hoc,
                        trang_thai="CHUA_DIEM_DANH",
                        phuong_thuc="-",
                        do_tuong_dong=None,
                        ghi_chu=None,
                    )
                )
        return ket_qua


def lay_lich_su_diem_danh_cua_sinh_vien(
    sinh_vien_id: int,
    tu_ngay: _datetime.date | None = None,
    den_ngay: _datetime.date | None = None,
) -> list[ThongTinDiemDanh]:
    """Lay lich su diem danh cua mot sinh vien, co the loc theo khoang thoi gian."""
    with mo_phien_lam_viec() as phien:
        truy_van = phien.query(DiemDanh).filter(DiemDanh.sinh_vien_id == sinh_vien_id)
        if tu_ngay is not None:
            truy_van = truy_van.filter(DiemDanh.thoi_gian_diem_danh >= tu_ngay)
        if den_ngay is not None:
            truy_van = truy_van.filter(
                DiemDanh.thoi_gian_diem_danh
                <= _datetime.datetime.combine(den_ngay, _datetime.time(23, 59, 59))
            )
        danh_sach = truy_van.order_by(DiemDanh.thoi_gian_diem_danh.desc()).all()

        sinh_vien = phien.get(SinhVien, sinh_vien_id)
        if sinh_vien is None:
            return []

        return [
            ThongTinDiemDanh(
                id=bg.id,
                buoi_hoc_id=bg.buoi_hoc_id,
                sinh_vien_id=sinh_vien_id,
                ma_sinh_vien=sinh_vien.ma_sinh_vien,
                ho_ten_sinh_vien=sinh_vien.ho_ten,
                thoi_gian_diem_danh=bg.thoi_gian_diem_danh,
                trang_thai=bg.trang_thai.value,
                phuong_thuc=bg.phuong_thuc.value,
                do_tuong_dong=bg.do_tuong_dong,
                ghi_chu=bg.ghi_chu,
            )
            for bg in danh_sach
        ]
