"""Model KhuonMat: embedding khuon mat da dang ky cua tung sinh vien.

Du lieu sinh trac hoc (embedding) la du lieu nhay cam, chi luu vector dac
trung (khong luu anh khuon mat goc trong database) va co the duoc ma hoa
truoc khi ghi xuong CSDL (xem app/tien_ich/bao_mat.py).
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.co_so_du_lieu.mo_hinh import Base, ThoiGianMixin


class KhuonMat(ThoiGianMixin, Base):
    """Bang khuon_mat."""

    __tablename__ = "khuon_mat"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sinh_vien_id: Mapped[int] = mapped_column(ForeignKey("sinh_vien.id", ondelete="CASCADE"), nullable=False)
    embedding: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    mo_hinh: Mapped[str] = mapped_column(String(50), nullable=False)
    phien_ban_mo_hinh: Mapped[str] = mapped_column(String(20), nullable=False)

    sinh_vien: Mapped["SinhVien"] = relationship(back_populates="danh_sach_khuon_mat")  # noqa: F821

    def __repr__(self) -> str:  # pragma: no cover
        return f"<KhuonMat id={self.id} sinh_vien_id={self.sinh_vien_id} mo_hinh={self.mo_hinh!r}>"
