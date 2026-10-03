"""
Dinh nghia lop Base cho toan bo model SQLAlchemy va cac mixin dung chung
(vi du: cot ngay_tao / ngay_cap_nhat tu dong).
"""

from __future__ import annotations

import datetime as _datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Lop co so (declarative base) cho tat ca cac model ORM cua he thong."""


class ThoiGianMixin:
    """Mixin cung cap hai cot ngay_tao / ngay_cap_nhat tu dong cap nhat."""

    ngay_tao: Mapped[_datetime.datetime] = mapped_column(
        DateTime, default=_datetime.datetime.utcnow, nullable=False
    )
    ngay_cap_nhat: Mapped[_datetime.datetime] = mapped_column(
        DateTime,
        default=_datetime.datetime.utcnow,
        onupdate=_datetime.datetime.utcnow,
        nullable=False,
    )
