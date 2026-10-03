"""Model NguoiDung: tai khoan dang nhap he thong (ADMIN / GIANG_VIEN / SINH_VIEN)."""

from __future__ import annotations

import datetime as _datetime
import enum

from sqlalchemy import Enum as SAEnum
from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.co_so_du_lieu.mo_hinh import Base, ThoiGianMixin


class VaiTro(str, enum.Enum):
    """Vai tro nguoi dung trong he thong, dung cho phan quyen RBAC."""

    ADMIN = "ADMIN"
    GIANG_VIEN = "GIANG_VIEN"
    SINH_VIEN = "SINH_VIEN"


class TrangThaiTaiKhoan(str, enum.Enum):
    """Trang thai hoat dong cua tai khoan."""

    HOAT_DONG = "HOAT_DONG"
    KHOA = "KHOA"
    NGUNG_HOAT_DONG = "NGUNG_HOAT_DONG"


class NguoiDung(ThoiGianMixin, Base):
    """Bang nguoi_dung: luu tai khoan dang nhap va thong tin bao mat lien quan."""

    __tablename__ = "nguoi_dung"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ten_dang_nhap: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    mat_khau_bam: Mapped[str] = mapped_column(String(255), nullable=False)
    ho_ten: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str | None] = mapped_column(String(150), unique=True, nullable=True)
    vai_tro: Mapped[VaiTro] = mapped_column(SAEnum(VaiTro, native_enum=True), nullable=False)
    trang_thai: Mapped[TrangThaiTaiKhoan] = mapped_column(
        SAEnum(TrangThaiTaiKhoan, native_enum=True),
        nullable=False,
        default=TrangThaiTaiKhoan.HOAT_DONG,
    )
    so_lan_dang_nhap_sai: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    thoi_diem_khoa: Mapped[_datetime.datetime | None] = mapped_column(nullable=True)
    lan_dang_nhap_cuoi: Mapped[_datetime.datetime | None] = mapped_column(nullable=True)

    def __repr__(self) -> str:  # pragma: no cover - chi phuc vu debug
        return f"<NguoiDung id={self.id} ten_dang_nhap={self.ten_dang_nhap!r} vai_tro={self.vai_tro}>"
