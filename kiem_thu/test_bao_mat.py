"""Kiem thu module bao mat: bam mat khau, do manh mat khau, ma hoa embedding."""

from __future__ import annotations

import numpy as np

from app.tien_ich.bao_mat import (
    bam_mat_khau,
    giai_ma_du_lieu_nhi_phan,
    kiem_tra_do_manh_mat_khau,
    kiem_tra_mat_khau,
    ma_hoa_du_lieu_nhi_phan,
)


def test_bam_mat_khau_khong_luu_dang_van_ban_ro() -> None:
    mat_khau_goc = "MatKhauCuaToi@123"
    mat_khau_bam = bam_mat_khau(mat_khau_goc)
    assert mat_khau_bam != mat_khau_goc
    assert mat_khau_goc not in mat_khau_bam


def test_bam_mat_khau_hai_lan_cho_ra_hash_khac_nhau_do_salt() -> None:
    """bcrypt/Argon2 dung salt ngau nhien nen bam cung mot mat khau 2 lan phai cho hash khac nhau."""
    hash_1 = bam_mat_khau("MatKhauGiongNhau@1")
    hash_2 = bam_mat_khau("MatKhauGiongNhau@1")
    assert hash_1 != hash_2


def test_kiem_tra_mat_khau_dung_va_sai() -> None:
    mat_khau_bam = bam_mat_khau("MatKhauDung@123")
    assert kiem_tra_mat_khau("MatKhauDung@123", mat_khau_bam) is True
    assert kiem_tra_mat_khau("MatKhauSai@123", mat_khau_bam) is False


def test_kiem_tra_do_manh_mat_khau_tu_choi_mat_khau_yeu() -> None:
    hop_le, _ = kiem_tra_do_manh_mat_khau("123")
    assert hop_le is False

    hop_le, _ = kiem_tra_do_manh_mat_khau("abcdefgh")
    assert hop_le is False


def test_kiem_tra_do_manh_mat_khau_chap_nhan_mat_khau_manh() -> None:
    hop_le, _ = kiem_tra_do_manh_mat_khau("MatKhauManh@2024")
    assert hop_le is True


def test_ma_hoa_va_giai_ma_embedding_khong_lam_mat_du_lieu() -> None:
    vector_goc = np.random.rand(512).astype(np.float32)
    du_lieu_da_ma_hoa = ma_hoa_du_lieu_nhi_phan(vector_goc.tobytes())

    # Du lieu da ma hoa phai khac hoan toan du lieu goc (khong luu embedding tho).
    assert du_lieu_da_ma_hoa != vector_goc.tobytes()

    du_lieu_giai_ma = giai_ma_du_lieu_nhi_phan(du_lieu_da_ma_hoa)
    vector_khoi_phuc = np.frombuffer(du_lieu_giai_ma, dtype=np.float32)
    assert np.allclose(vector_goc, vector_khoi_phuc)
