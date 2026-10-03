"""Model CauHinh: cau hinh he thong dang khoa-gia tri, co the thay doi tu giao dien Admin."""

from __future__ import annotations

import datetime as _datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.co_so_du_lieu.mo_hinh import Base


class CauHinh(Base):
    """Bang cau_hinh."""

    __tablename__ = "cau_hinh"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    khoa_cau_hinh: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    gia_tri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    mo_ta: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ngay_cap_nhat: Mapped[_datetime.datetime] = mapped_column(
        DateTime,
        default=_datetime.datetime.utcnow,
        onupdate=_datetime.datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CauHinh khoa_cau_hinh={self.khoa_cau_hinh!r} gia_tri={self.gia_tri!r}>"
