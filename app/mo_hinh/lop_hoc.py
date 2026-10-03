"""Model LopHoc: lop hanh chinh ma sinh vien truc thuoc."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.co_so_du_lieu.mo_hinh import Base, ThoiGianMixin


class LopHoc(ThoiGianMixin, Base):
    """Bang lop_hoc: lop hanh chinh (khong phai lop hoc phan)."""

    __tablename__ = "lop_hoc"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ma_lop: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    ten_lop: Mapped[str] = mapped_column(String(150), nullable=False)
    khoa_id: Mapped[int] = mapped_column(ForeignKey("khoa.id", ondelete="RESTRICT"), nullable=False)
    khoa_hoc: Mapped[str | None] = mapped_column(String(20), nullable=True)

    khoa: Mapped["Khoa"] = relationship(back_populates="danh_sach_lop")  # noqa: F821
    danh_sach_sinh_vien: Mapped[list["SinhVien"]] = relationship(  # noqa: F821
        back_populates="lop"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<LopHoc id={self.id} ma_lop={self.ma_lop!r}>"
