"""
Cau hinh dung chung cho toan bo bo kiem thu (pytest).

Cac test trong thu muc nay can ket noi toi MySQL/MariaDB (XAMPP) dang
chay voi database `diem_danh_khuon_mat` da duoc khoi tao (chay truoc
`python cai_dat.py`). Neu khong ket noi duoc, toan bo cac test can CSDL
se tu dong bi SKIP thay vi bao loi, de khong lam gian doan CI/moi truong
chua co MySQL.

Luu y: de an toan, nen chay bo kiem thu tren mot database THU NGHIEM
rieng (vi du sua DB_NAME trong .env thanh `diem_danh_khuon_mat_test`)
thay vi database du lieu that dang su dung.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

THU_MUC_GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(THU_MUC_GOC))

from app.co_so_du_lieu.ket_noi import kiem_tra_ket_noi_mysql  # noqa: E402


def _mysql_kha_dung() -> bool:
    thanh_cong, _ = kiem_tra_ket_noi_mysql()
    return thanh_cong


@pytest.fixture(scope="session", autouse=True)
def yeu_cau_mysql() -> None:
    """Tu dong bo qua toan bo test can CSDL neu MySQL/MariaDB chua san sang."""
    if not _mysql_kha_dung():
        pytest.skip(
            "Khong the ket noi MySQL/MariaDB (XAMPP). Vui long mo XAMPP, "
            "Start MySQL, roi chay 'python cai_dat.py' truoc khi kiem thu."
        )
