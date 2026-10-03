"""Module tien ich kiem tra tinh hop le cua du lieu dau vao tu giao dien."""

from __future__ import annotations

import re
from datetime import date

_MAU_EMAIL = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
_MAU_SO_DIEN_THOAI = re.compile(r"^0[0-9]{9,10}$")
_MAU_MA_DINH_DANH = re.compile(r"^[A-Za-z0-9_]{2,20}$")


def kiem_tra_chuoi_khong_rong(gia_tri: str | None, ten_truong: str) -> tuple[bool, str]:
    """Kiem tra mot chuoi khong duoc de trong (sau khi strip khoang trang)."""
    if gia_tri is None or gia_tri.strip() == "":
        return False, f"{ten_truong} khong duoc de trong."
    return True, ""


def kiem_tra_dinh_dang_email(email: str | None) -> tuple[bool, str]:
    """Kiem tra dinh dang email hop le. Cho phep de trong (email khong bat buoc)."""
    if not email:
        return True, ""
    if not _MAU_EMAIL.match(email):
        return False, "Dinh dang email khong hop le."
    return True, ""


def kiem_tra_dinh_dang_so_dien_thoai(so_dien_thoai: str | None) -> tuple[bool, str]:
    """Kiem tra so dien thoai Viet Nam (bat dau bang 0, 10-11 chu so). Cho phep de trong."""
    if not so_dien_thoai:
        return True, ""
    if not _MAU_SO_DIEN_THOAI.match(so_dien_thoai):
        return False, "So dien thoai khong hop le (vi du: 0912345678)."
    return True, ""


def kiem_tra_dinh_dang_ma_dinh_danh(ma: str | None, ten_truong: str) -> tuple[bool, str]:
    """Kiem tra ma sinh vien/ma giang vien/ma lop... chi gom chu, so, gach duoi."""
    if not ma:
        return False, f"{ten_truong} khong duoc de trong."
    if not _MAU_MA_DINH_DANH.match(ma):
        return False, f"{ten_truong} chi duoc gom chu cai, chu so va dau gach duoi (2-20 ky tu)."
    return True, ""


def kiem_tra_ngay_sinh_hop_le(ngay_sinh: date | None) -> tuple[bool, str]:
    """Kiem tra ngay sinh khong o tuong lai va tuoi nam trong khoang hop ly (10-100 tuoi)."""
    if ngay_sinh is None:
        return True, ""
    hom_nay = date.today()
    if ngay_sinh > hom_nay:
        return False, "Ngay sinh khong duoc o tuong lai."
    tuoi = hom_nay.year - ngay_sinh.year - (
        (hom_nay.month, hom_nay.day) < (ngay_sinh.month, ngay_sinh.day)
    )
    if tuoi < 10 or tuoi > 100:
        return False, "Ngay sinh khong hop ly."
    return True, ""


def kiem_tra_khoang_thoi_gian(gio_bat_dau, gio_ket_thuc) -> tuple[bool, str]:
    """Kiem tra gio bat dau phai truoc gio ket thuc."""
    if gio_bat_dau is None or gio_ket_thuc is None:
        return False, "Gio bat dau va gio ket thuc khong duoc de trong."
    if gio_bat_dau >= gio_ket_thuc:
        return False, "Gio bat dau phai truoc gio ket thuc."
    return True, ""
