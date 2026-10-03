"""
Kiem thu ket noi va cac tinh nang co ban cua co so du lieu MySQL/MariaDB.

Bao gom: ket noi, database ton tai, bang ton tai, CRUD, transaction/rollback,
khoa ngoai (foreign key), rang buoc duy nhat (unique constraint).
"""

from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError

from app.co_so_du_lieu.ket_noi import (
    kiem_tra_cac_bang_can_thiet,
    kiem_tra_database_ton_tai,
    kiem_tra_ket_noi_mysql,
    mo_phien_lam_viec,
)
from app.mo_hinh.khoa import Khoa
from app.mo_hinh.lop_hoc import LopHoc


def test_ket_noi_mysql_thanh_cong() -> None:
    thanh_cong, thong_bao = kiem_tra_ket_noi_mysql()
    assert thanh_cong is True
    assert "thanh cong" in thong_bao.lower()


def test_database_da_ton_tai() -> None:
    thanh_cong, _ = kiem_tra_database_ton_tai()
    assert thanh_cong is True


def test_du_toan_bo_bang_can_thiet() -> None:
    thanh_cong, thong_bao, cac_bang_thieu = kiem_tra_cac_bang_can_thiet()
    assert thanh_cong is True, thong_bao
    assert cac_bang_thieu == []


def test_crud_tao_doc_sua_xoa_ban_ghi() -> None:
    """Kiem tra chu ky CRUD day du tren mot ban ghi Khoa tam thoi."""
    with mo_phien_lam_viec() as phien:
        # CREATE
        khoa_moi = Khoa(ma_khoa="TEST_CRUD", ten_khoa="Khoa Kiem Thu CRUD")
        phien.add(khoa_moi)
        phien.commit()
        khoa_id = khoa_moi.id
        assert khoa_id is not None

        # READ
        khoa_doc_lai = phien.get(Khoa, khoa_id)
        assert khoa_doc_lai is not None
        assert khoa_doc_lai.ten_khoa == "Khoa Kiem Thu CRUD"

        # UPDATE
        khoa_doc_lai.ten_khoa = "Khoa Kiem Thu Da Sua"
        phien.commit()
        khoa_sau_sua = phien.get(Khoa, khoa_id)
        assert khoa_sau_sua.ten_khoa == "Khoa Kiem Thu Da Sua"

        # DELETE
        phien.delete(khoa_sau_sua)
        phien.commit()
        khoa_sau_xoa = phien.get(Khoa, khoa_id)
        assert khoa_sau_xoa is None


def test_transaction_rollback_khoi_phuc_du_lieu() -> None:
    """Khi rollback, thay doi chua commit phai bi huy bo hoan toan."""
    with mo_phien_lam_viec() as phien:
        khoa_moi = Khoa(ma_khoa="TEST_ROLLBACK", ten_khoa="Khoa Se Bi Rollback")
        phien.add(khoa_moi)
        phien.flush()  # Gui SQL xuong CSDL nhung CHUA commit
        khoa_id = khoa_moi.id
        phien.rollback()

    with mo_phien_lam_viec() as phien_moi:
        ket_qua = phien_moi.query(Khoa).filter_by(ma_khoa="TEST_ROLLBACK").first()
        assert ket_qua is None, "Ban ghi khong duoc ton tai sau khi rollback."


def test_khoa_ngoai_chan_du_lieu_khong_hop_le() -> None:
    """Them LopHoc voi khoa_id khong ton tai phai bi CSDL tu choi (foreign key)."""
    with mo_phien_lam_viec() as phien:
        lop_khong_hop_le = LopHoc(ma_lop="TEST_FK_LOP", ten_lop="Lop Test FK", khoa_id=999999)
        phien.add(lop_khong_hop_le)
        with pytest.raises(IntegrityError):
            phien.commit()
        phien.rollback()


def test_rang_buoc_duy_nhat_chan_trung_ma_khoa() -> None:
    """Them hai Khoa cung ma_khoa phai bi tu choi boi UNIQUE constraint."""
    with mo_phien_lam_viec() as phien:
        khoa_1 = Khoa(ma_khoa="TEST_UNIQUE", ten_khoa="Khoa Thu Nhat")
        phien.add(khoa_1)
        phien.commit()

    try:
        with mo_phien_lam_viec() as phien:
            khoa_2 = Khoa(ma_khoa="TEST_UNIQUE", ten_khoa="Khoa Trung Ma")
            phien.add(khoa_2)
            with pytest.raises(IntegrityError):
                phien.commit()
            phien.rollback()
    finally:
        with mo_phien_lam_viec() as phien_don_dep:
            ban_ghi = phien_don_dep.query(Khoa).filter_by(ma_khoa="TEST_UNIQUE").first()
            if ban_ghi is not None:
                phien_don_dep.delete(ban_ghi)
                phien_don_dep.commit()
