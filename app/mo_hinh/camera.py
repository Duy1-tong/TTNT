"""Model Camera: danh sach camera dung de diem danh bang khuon mat."""

from __future__ import annotations

import enum

from sqlalchemy import Enum as SAEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.co_so_du_lieu.mo_hinh import Base, ThoiGianMixin


class TrangThaiCamera(str, enum.Enum):
    """Trang thai su dung cua camera."""

    HOAT_DONG = "HOAT_DONG"
    NGUNG_SU_DUNG = "NGUNG_SU_DUNG"


class Camera(ThoiGianMixin, Base):
    """Bang camera.

    Truong `nguon` co the la chi so webcam (vi du "0") hoac duong dan/URL
    RTSP cua camera IP.
    """

    __tablename__ = "camera"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ten_camera: Mapped[str] = mapped_column(String(100), nullable=False)
    nguon: Mapped[str] = mapped_column(String(255), nullable=False)
    vi_tri: Mapped[str | None] = mapped_column(String(150), nullable=True)
    trang_thai: Mapped[TrangThaiCamera] = mapped_column(
        SAEnum(TrangThaiCamera, native_enum=True), nullable=False, default=TrangThaiCamera.HOAT_DONG
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Camera id={self.id} ten_camera={self.ten_camera!r}>"
