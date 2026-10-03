"""Module thiet lap he thong ghi log (Python `logging`) cho toan ung dung."""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

from app.cau_hinh.cai_dat import lay_cau_hinh

_DA_THIET_LAP = False


def thiet_lap_ghi_log() -> None:
    """Cau hinh logging goc cho toan ung dung: ghi ra file xoay vong + console.

    An toan khi goi nhieu lan (chi thiet lap mot lan duy nhat).
    """
    global _DA_THIET_LAP
    if _DA_THIET_LAP:
        return

    cau_hinh = lay_cau_hinh()
    thu_muc_nhat_ky = cau_hinh.duong_dan_tuyet_doi(cau_hinh.ung_dung.thu_muc_nhat_ky)
    thu_muc_nhat_ky.mkdir(parents=True, exist_ok=True)
    duong_dan_file_log = thu_muc_nhat_ky / "he_thong.log"

    dinh_dang = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    bo_xu_ly_file = logging.handlers.RotatingFileHandler(
        duong_dan_file_log, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    bo_xu_ly_file.setFormatter(dinh_dang)

    bo_xu_ly_console = logging.StreamHandler()
    bo_xu_ly_console.setFormatter(dinh_dang)

    logger_goc = logging.getLogger()
    muc_ghi_log = getattr(logging, cau_hinh.ung_dung.muc_ghi_log.upper(), logging.INFO)
    logger_goc.setLevel(muc_ghi_log)
    logger_goc.addHandler(bo_xu_ly_file)
    logger_goc.addHandler(bo_xu_ly_console)

    _DA_THIET_LAP = True
    logging.getLogger(__name__).info("Da thiet lap he thong ghi log. File: %s", duong_dan_file_log)
