"""Model SinhVien: ho so sinh vien."""

from __future__ import annotations

import datetime as _datetime
import enum

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.co_so_du_lieu.mo_hinh import Base, ThoiGianMixin


class GioiTinh(str, enum.Enum):
    """Gioi tinh sinh vien."""

    NAM = "NAM"
    NU = "NU"
    KHAC = "KHAC"


class TrangThaiSinhVien(str, enum.Enum):
    """Trang thai hoc tap cua sinh vien."""

    DANG_HOC = "DANG_HOC"
    NGHI_HOC = "NGHI_HOC"
    BAO_LUU = "BAO_LUU"
    TOT_NGHIEP = "TOT_NGHIEP"


class SinhVien(ThoiGianMixin, Base):
    """Bang sinh_vien.

    Luu y: KHONG xoa vat ly sinh vien da co lich su diem danh, chi chuyen
    trang_thai sang NGHI_HOC/BAO_LUU/TOT_NGHIEP (xoa mem).
    """

    __tablename__ = "sinh_vien"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nguoi_dung_id: Mapped[int | None] = mapped_column(
        ForeignKey("nguoi_dung.id", ondelete="SET NULL"), unique=True, nullable=True
    )
    ma_sinh_vien: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    ho_ten: Mapped[str] = mapped_column(String(150), nullable=False)
    ngay_sinh: Mapped[_datetime.date | None] = mapped_column(Date, nullable=True)
    gioi_tinh: Mapped[GioiTinh | None] = mapped_column(
        SAEnum(GioiTinh, native_enum=True), nullable=True
    )
    email: Mapped[str | None] = mapped_column(String(150), unique=True, nullable=True)
    so_dien_thoai: Mapped[str | None] = mapped_column(String(20), nullable=True)
    dia_chi: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lop_id: Mapped[int | None] = mapped_column(ForeignKey("lop_hoc.id", ondelete="SET NULL"), nullable=True)
    khoa_id: Mapped[int | None] = mapped_column(ForeignKey("khoa.id", ondelete="SET NULL"), nullable=True)
    anh_dai_dien: Mapped[str | None] = mapped_column(String(255), nullable=True)
    trang_thai: Mapped[TrangThaiSinhVien] = mapped_column(
        SAEnum(TrangThaiSinhVien, native_enum=True),
        nullable=False,
        default=TrangThaiSinhVien.DANG_HOC,
    )

    nguoi_dung: Mapped["NguoiDung | None"] = relationship()  # noqa: F821
    lop: Mapped["LopHoc | None"] = relationship(back_populates="danh_sach_sinh_vien")  # noqa: F821
    khoa: Mapped["Khoa | None"] = relationship()  # noqa: F821
    danh_sach_khuon_mat: Mapped[list["KhuonMat"]] = relationship(  # noqa: F821
        back_populates="sinh_vien", cascade="all, delete-orphan"
    )
    danh_sach_diem_danh: Mapped[list["DiemDanh"]] = relationship(  # noqa: F821
        back_populates="sinh_vien"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SinhVien id={self.id} ma_sinh_vien={self.ma_sinh_vien!r}>"
