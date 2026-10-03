"""Model LopMonHoc: lop hoc phan — mot mon hoc duoc mo trong mot hoc ky, do mot giang vien phu trach."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.co_so_du_lieu.mo_hinh import Base, ThoiGianMixin


class LopMonHoc(ThoiGianMixin, Base):
    """Bang lop_mon_hoc."""

    __tablename__ = "lop_mon_hoc"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ma_lop_mon: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    mon_hoc_id: Mapped[int] = mapped_column(ForeignKey("mon_hoc.id", ondelete="RESTRICT"), nullable=False)
    giang_vien_id: Mapped[int | None] = mapped_column(ForeignKey("giang_vien.id", ondelete="SET NULL"), nullable=True)
    hoc_ky: Mapped[str] = mapped_column(String(20), nullable=False)
    nam_hoc: Mapped[str] = mapped_column(String(20), nullable=False)

    mon_hoc: Mapped["MonHoc"] = relationship(back_populates="danh_sach_lop_mon_hoc")  # noqa: F821
    giang_vien: Mapped["GiangVien | None"] = relationship(  # noqa: F821
        back_populates="danh_sach_lop_mon_hoc"
    )
    danh_sach_sinh_vien_dang_ky: Mapped[list["SinhVienLop"]] = relationship(  # noqa: F821
        back_populates="lop_mon_hoc", cascade="all, delete-orphan"
    )
    danh_sach_buoi_hoc: Mapped[list["BuoiHoc"]] = relationship(  # noqa: F821
        back_populates="lop_mon_hoc", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<LopMonHoc id={self.id} ma_lop_mon={self.ma_lop_mon!r}>"
