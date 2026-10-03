"""Model SinhVienLop: bang trung gian the hien sinh vien dang ky hoc lop hoc phan nao."""

from __future__ import annotations

import datetime as _datetime
import enum

from sqlalchemy import Enum as SAEnum
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.co_so_du_lieu.mo_hinh import Base


class TrangThaiDangKy(str, enum.Enum):
    """Trang thai dang ky hoc phan cua sinh vien."""

    DANG_HOC = "DANG_HOC"
    DA_HUY = "DA_HUY"


class SinhVienLop(Base):
    """Bang sinh_vien_lop. Co UNIQUE(sinh_vien_id, lop_mon_hoc_id) de tranh dang ky trung."""

    __tablename__ = "sinh_vien_lop"
    __table_args__ = (
        UniqueConstraint("sinh_vien_id", "lop_mon_hoc_id", name="uk_sinh_vien_lop"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sinh_vien_id: Mapped[int] = mapped_column(ForeignKey("sinh_vien.id", ondelete="CASCADE"), nullable=False)
    lop_mon_hoc_id: Mapped[int] = mapped_column(ForeignKey("lop_mon_hoc.id", ondelete="CASCADE"), nullable=False)
    ngay_dang_ky: Mapped[_datetime.datetime] = mapped_column(
        DateTime, default=_datetime.datetime.utcnow, nullable=False
    )
    trang_thai: Mapped[TrangThaiDangKy] = mapped_column(
        SAEnum(TrangThaiDangKy, native_enum=True), nullable=False, default=TrangThaiDangKy.DANG_HOC
    )

    sinh_vien: Mapped["SinhVien"] = relationship()  # noqa: F821
    lop_mon_hoc: Mapped["LopMonHoc"] = relationship(  # noqa: F821
        back_populates="danh_sach_sinh_vien_dang_ky"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SinhVienLop sinh_vien_id={self.sinh_vien_id} lop_mon_hoc_id={self.lop_mon_hoc_id}>"
