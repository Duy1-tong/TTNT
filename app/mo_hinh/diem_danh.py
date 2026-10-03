"""Model DiemDanh: ban ghi diem danh cua sinh vien trong mot buoi hoc."""

from __future__ import annotations

import datetime as _datetime
import enum

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.co_so_du_lieu.mo_hinh import Base, ThoiGianMixin


class TrangThaiDiemDanh(str, enum.Enum):
    """Trang thai diem danh cua sinh vien trong buoi hoc."""

    CO_MAT = "CO_MAT"
    DI_MUON = "DI_MUON"
    VANG = "VANG"
    CO_PHEP = "CO_PHEP"


class PhuongThucDiemDanh(str, enum.Enum):
    """Phuong thuc thuc hien diem danh."""

    KHUON_MAT = "KHUON_MAT"
    THU_CONG = "THU_CONG"


class DiemDanh(ThoiGianMixin, Base):
    """Bang diem_danh. Co UNIQUE(buoi_hoc_id, sinh_vien_id) de chong diem danh trung."""

    __tablename__ = "diem_danh"
    __table_args__ = (
        UniqueConstraint("buoi_hoc_id", "sinh_vien_id", name="uk_diem_danh_buoi_sinh_vien"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    buoi_hoc_id: Mapped[int] = mapped_column(ForeignKey("buoi_hoc.id", ondelete="CASCADE"), nullable=False)
    sinh_vien_id: Mapped[int] = mapped_column(ForeignKey("sinh_vien.id", ondelete="CASCADE"), nullable=False)
    thoi_gian_diem_danh: Mapped[_datetime.datetime] = mapped_column(
        default=_datetime.datetime.utcnow, nullable=False
    )
    trang_thai: Mapped[TrangThaiDiemDanh] = mapped_column(
        SAEnum(TrangThaiDiemDanh, native_enum=True),
        nullable=False,
        default=TrangThaiDiemDanh.CO_MAT,
    )
    phuong_thuc: Mapped[PhuongThucDiemDanh] = mapped_column(
        SAEnum(PhuongThucDiemDanh, native_enum=True),
        nullable=False,
        default=PhuongThucDiemDanh.KHUON_MAT,
    )
    do_tuong_dong: Mapped[float | None] = mapped_column(Float, nullable=True)
    ghi_chu: Mapped[str | None] = mapped_column(String(500), nullable=True)
    nguoi_thuc_hien_id: Mapped[int | None] = mapped_column(
        ForeignKey("nguoi_dung.id", ondelete="SET NULL"), nullable=True
    )

    buoi_hoc: Mapped["BuoiHoc"] = relationship(back_populates="danh_sach_diem_danh")  # noqa: F821
    sinh_vien: Mapped["SinhVien"] = relationship(back_populates="danh_sach_diem_danh")  # noqa: F821
    nguoi_thuc_hien: Mapped["NguoiDung | None"] = relationship()  # noqa: F821

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<DiemDanh buoi_hoc_id={self.buoi_hoc_id} sinh_vien_id={self.sinh_vien_id} "
            f"trang_thai={self.trang_thai}>"
        )
