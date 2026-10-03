"""
Tien ich Hieu Ung Giao Dien: cung cap do bong (drop shadow) mem cho cac
khoi giao dien (the thong ke, hop dang nhap, sidebar...) de tao cam giac
"noi" nhe nhang, sang trong thay vi phang mot mau.

Qt Style Sheet (QSS) khong ho tro thuoc tinh box-shadow nhu CSS, nen ta
dung QGraphicsDropShadowEffect (mot hieu ung do Qt cung cap san) ap dung
truc tiep len tung QWidget can lam noi bat.
"""

from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget

# Mau bong mac dinh: xanh dam nhat, mo, phu hop voi tong mau xanh pastel chu dao.
_MAU_BONG_MAC_DINH = QColor(30, 54, 84, 45)


def ap_dung_do_bong(
    widget: QWidget,
    do_mo: int = 24,
    do_lech_x: float = 0,
    do_lech_y: float = 6,
    mau_bong: QColor | None = None,
) -> QGraphicsDropShadowEffect:
    """Ap dung hieu ung do bong mem cho mot widget, tra ve hieu ung de co the
    tuy chinh them neu can. Goi ham nay SAU khi widget da duoc xay dung xong
    (Qt khong cho phep hai widget dung chung mot QGraphicsEffect)."""
    hieu_ung = QGraphicsDropShadowEffect(widget)
    hieu_ung.setBlurRadius(do_mo)
    hieu_ung.setOffset(do_lech_x, do_lech_y)
    hieu_ung.setColor(mau_bong if mau_bong is not None else _MAU_BONG_MAC_DINH)
    widget.setGraphicsEffect(hieu_ung)
    return hieu_ung
