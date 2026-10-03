"""Model Khoa: don vi khoa/vien dao tao trong truong."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.co_so_du_lieu.mo_hinh import Base, ThoiGianMixin


class Khoa(ThoiGianMixin, Base):
    """Bang khoa: danh sach cac khoa/vien trong truong."""

    __tablename__ = "khoa"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ma_khoa: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    ten_khoa: Mapped[str] = mapped_column(String(150), nullable=False)
    mo_ta: Mapped[str | None] = mapped_column(String(500), nullable=True)

    danh_sach_lop: Mapped[list["LopHoc"]] = relationship(  # noqa: F821
        back_populates="khoa", cascade="save-update"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Khoa id={self.id} ma_khoa={self.ma_khoa!r}>"
