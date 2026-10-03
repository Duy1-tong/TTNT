"""Model MonHoc: danh muc mon hoc."""

from __future__ import annotations

from sqlalchemy import ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.co_so_du_lieu.mo_hinh import Base, ThoiGianMixin


class MonHoc(ThoiGianMixin, Base):
    """Bang mon_hoc."""

    __tablename__ = "mon_hoc"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ma_mon: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    ten_mon: Mapped[str] = mapped_column(String(150), nullable=False)
    so_tin_chi: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    khoa_id: Mapped[int | None] = mapped_column(ForeignKey("khoa.id", ondelete="SET NULL"), nullable=True)

    khoa: Mapped["Khoa | None"] = relationship()  # noqa: F821
    danh_sach_lop_mon_hoc: Mapped[list["LopMonHoc"]] = relationship(  # noqa: F821
        back_populates="mon_hoc"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<MonHoc id={self.id} ma_mon={self.ma_mon!r}>"
