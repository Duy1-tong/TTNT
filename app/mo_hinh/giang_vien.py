"""Model GiangVien: ho so giang vien, co the lien ket toi mot tai khoan dang nhap."""

from __future__ import annotations

import enum

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.co_so_du_lieu.mo_hinh import Base, ThoiGianMixin


class TrangThaiGiangVien(str, enum.Enum):
    """Trang thai cong tac cua giang vien."""

    DANG_CONG_TAC = "DANG_CONG_TAC"
    NGHI_VIEC = "NGHI_VIEC"


class GiangVien(ThoiGianMixin, Base):
    """Bang giang_vien."""

    __tablename__ = "giang_vien"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nguoi_dung_id: Mapped[int | None] = mapped_column(
        ForeignKey("nguoi_dung.id", ondelete="SET NULL"), unique=True, nullable=True
    )
    ma_giang_vien: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    ho_ten: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    so_dien_thoai: Mapped[str | None] = mapped_column(String(20), nullable=True)
    khoa_id: Mapped[int | None] = mapped_column(ForeignKey("khoa.id", ondelete="SET NULL"), nullable=True)
    hoc_vi: Mapped[str | None] = mapped_column(String(50), nullable=True)
    trang_thai: Mapped[TrangThaiGiangVien] = mapped_column(
        SAEnum(TrangThaiGiangVien, native_enum=True),
        nullable=False,
        default=TrangThaiGiangVien.DANG_CONG_TAC,
    )

    nguoi_dung: Mapped["NguoiDung | None"] = relationship()  # noqa: F821
    khoa: Mapped["Khoa | None"] = relationship()  # noqa: F821
    danh_sach_lop_mon_hoc: Mapped[list["LopMonHoc"]] = relationship(  # noqa: F821
        back_populates="giang_vien"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<GiangVien id={self.id} ma_giang_vien={self.ma_giang_vien!r}>"
