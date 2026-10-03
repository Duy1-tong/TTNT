"""Model NhatKyHeThong: nhat ky (audit log) ghi lai moi hanh dong quan trong."""

from __future__ import annotations

import datetime as _datetime
import enum

from sqlalchemy import BigInteger, DateTime, Enum as SAEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.co_so_du_lieu.mo_hinh import Base


class KetQuaHanhDong(str, enum.Enum):
    """Ket qua cua hanh dong duoc ghi log."""

    THANH_CONG = "THANH_CONG"
    THAT_BAI = "THAT_BAI"


class NhatKyHeThong(Base):
    """Bang nhat_ky_he_thong.

    Ghi log cho: dang nhap, dang xuat, dang ky khuon mat, xoa, sua, diem danh,
    sua diem danh, doi mat khau, thay doi cau hinh, dang nhap that bai.
    KHONG BAO GIO ghi mat khau (dang ro hay da bam) vao noi_dung.
    """

    __tablename__ = "nhat_ky_he_thong"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nguoi_dung_id: Mapped[int | None] = mapped_column(
        ForeignKey("nguoi_dung.id", ondelete="SET NULL"), nullable=True
    )
    hanh_dong: Mapped[str] = mapped_column(String(100), nullable=False)
    doi_tuong: Mapped[str | None] = mapped_column(String(100), nullable=True)
    doi_tuong_id: Mapped[int | None] = mapped_column(nullable=True)
    noi_dung: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    dia_chi_ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    thoi_gian: Mapped[_datetime.datetime] = mapped_column(
        DateTime, default=_datetime.datetime.utcnow, nullable=False
    )
    ket_qua: Mapped[KetQuaHanhDong] = mapped_column(
        SAEnum(KetQuaHanhDong, native_enum=True), nullable=False, default=KetQuaHanhDong.THANH_CONG
    )

    nguoi_dung: Mapped["NguoiDung | None"] = relationship()  # noqa: F821

    def __repr__(self) -> str:  # pragma: no cover
        return f"<NhatKyHeThong id={self.id} hanh_dong={self.hanh_dong!r} ket_qua={self.ket_qua}>"
