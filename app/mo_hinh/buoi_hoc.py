"""Model BuoiHoc: mot buoi hoc cu the cua mot lop hoc phan, la don vi de diem danh."""

from __future__ import annotations

import datetime as _datetime
import enum

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Date, DateTime, ForeignKey, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.co_so_du_lieu.mo_hinh import Base


class TrangThaiBuoiHoc(str, enum.Enum):
    """Trang thai cua mot buoi hoc."""

    CHUA_BAT_DAU = "CHUA_BAT_DAU"
    DANG_DIEM_DANH = "DANG_DIEM_DANH"
    DA_KET_THUC = "DA_KET_THUC"


class BuoiHoc(Base):
    """Bang buoi_hoc."""

    __tablename__ = "buoi_hoc"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lop_mon_hoc_id: Mapped[int] = mapped_column(ForeignKey("lop_mon_hoc.id", ondelete="CASCADE"), nullable=False)
    ngay_hoc: Mapped[_datetime.date] = mapped_column(Date, nullable=False)
    gio_bat_dau: Mapped[_datetime.time] = mapped_column(Time, nullable=False)
    gio_ket_thuc: Mapped[_datetime.time] = mapped_column(Time, nullable=False)
    gio_mo_diem_danh: Mapped[_datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    gio_dong_diem_danh: Mapped[_datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    phong_hoc: Mapped[str | None] = mapped_column(String(50), nullable=True)
    trang_thai: Mapped[TrangThaiBuoiHoc] = mapped_column(
        SAEnum(TrangThaiBuoiHoc, native_enum=True),
        nullable=False,
        default=TrangThaiBuoiHoc.CHUA_BAT_DAU,
    )
    nguoi_tao_id: Mapped[int | None] = mapped_column(ForeignKey("nguoi_dung.id", ondelete="SET NULL"), nullable=True)
    ngay_tao: Mapped[_datetime.datetime] = mapped_column(
        DateTime, default=_datetime.datetime.utcnow, nullable=False
    )

    lop_mon_hoc: Mapped["LopMonHoc"] = relationship(back_populates="danh_sach_buoi_hoc")  # noqa: F821
    nguoi_tao: Mapped["NguoiDung | None"] = relationship()  # noqa: F821
    danh_sach_diem_danh: Mapped[list["DiemDanh"]] = relationship(  # noqa: F821
        back_populates="buoi_hoc", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<BuoiHoc id={self.id} ngay_hoc={self.ngay_hoc} trang_thai={self.trang_thai}>"
