"""Kiem thu tri tue nhan tao nhan dien khuon mat va dich vu dang ky khuon mat."""

from __future__ import annotations

import numpy as np
import pytest

from app.dich_vu import sinh_vien as dv_sinh_vien
from app.dich_vu.khuon_mat import LoiDangKyKhuonMat, dang_ky_khuon_mat_tu_anh, xoa_khuon_mat
from app.tri_tue_nhan_tao.phat_hien_khuon_mat import BoPhatHienKhuonMat
from app.tri_tue_nhan_tao.so_sanh_khuon_mat import (
    tim_sinh_vien_phu_hop_nhat,
    tinh_do_tuong_dong_cosine,
)
from app.tri_tue_nhan_tao.tao_embedding import BoTaoEmbedding

MA_SINH_VIEN_TEST = "SV_TEST_KM01"


def test_phat_hien_khuon_mat_tra_ve_danh_sach_rong_tren_anh_nhieu() -> None:
    bo_phat_hien = BoPhatHienKhuonMat()
    anh_nhieu = (np.random.rand(240, 320, 3) * 255).astype(np.uint8)
    ket_qua = bo_phat_hien.phat_hien(anh_nhieu)
    assert isinstance(ket_qua, list)
    assert len(ket_qua) == 0


def test_tao_embedding_cho_ra_vector_chuan_hoa() -> None:
    bo_embedding = BoTaoEmbedding()
    anh_gia = (np.random.rand(160, 160, 3) * 255).astype(np.uint8)
    vector = bo_embedding.tao_embedding(anh_gia)
    assert isinstance(vector, np.ndarray)
    assert vector.ndim == 1
    # Vector phai duoc chuan hoa L2 (norm xap xi 1.0) de cosine similarity hoat dong dung.
    assert abs(float(np.linalg.norm(vector)) - 1.0) < 1e-3


def test_cung_mot_anh_cho_do_tuong_dong_cao_nhat() -> None:
    bo_embedding = BoTaoEmbedding()
    anh_a = (np.random.rand(160, 160, 3) * 255).astype(np.uint8)
    anh_b = (np.random.rand(160, 160, 3) * 255).astype(np.uint8)

    vector_a1 = bo_embedding.tao_embedding(anh_a)
    vector_a2 = bo_embedding.tao_embedding(anh_a)
    vector_b = bo_embedding.tao_embedding(anh_b)

    do_tuong_dong_cung_anh = tinh_do_tuong_dong_cosine(vector_a1, vector_a2)
    do_tuong_dong_khac_anh = tinh_do_tuong_dong_cosine(vector_a1, vector_b)

    assert do_tuong_dong_cung_anh > do_tuong_dong_khac_anh
    assert do_tuong_dong_cung_anh > 0.99


def test_tim_sinh_vien_phu_hop_nhat_chon_dung_ung_vien_gan_nhat() -> None:
    bo_embedding = BoTaoEmbedding()
    vector_muc_tieu = bo_embedding.tao_embedding(
        (np.random.rand(160, 160, 3) * 255).astype(np.uint8)
    )
    vector_giong = vector_muc_tieu.copy()
    vector_khac = bo_embedding.tao_embedding((np.random.rand(160, 160, 3) * 255).astype(np.uint8))

    ket_qua = tim_sinh_vien_phu_hop_nhat(
        vector_muc_tieu,
        [(101, vector_khac), (202, vector_giong)],
        nguong_do_tuong_dong=0.9,
    )
    assert ket_qua is not None
    assert ket_qua.sinh_vien_id == 202


def test_tim_sinh_vien_phu_hop_nhat_tra_ve_none_khi_duoi_nguong() -> None:
    bo_embedding = BoTaoEmbedding()
    vector_muc_tieu = bo_embedding.tao_embedding(
        (np.random.rand(160, 160, 3) * 255).astype(np.uint8)
    )
    vector_khac_hoan_toan = bo_embedding.tao_embedding(
        (np.random.rand(160, 160, 3) * 255).astype(np.uint8)
    )
    ket_qua = tim_sinh_vien_phu_hop_nhat(
        vector_muc_tieu, [(999, vector_khac_hoan_toan)], nguong_do_tuong_dong=0.999999
    )
    assert ket_qua is None


@pytest.fixture()
def sinh_vien_tam_de_dang_ky_khuon_mat():
    sinh_vien_id = dv_sinh_vien.them_sinh_vien(
        "ADMIN", ma_sinh_vien=MA_SINH_VIEN_TEST, ho_ten="Sinh Vien Kiem Thu Khuon Mat",
        nguoi_thuc_hien_id=1,
    )
    yield sinh_vien_id
    from app.co_so_du_lieu.ket_noi import mo_phien_lam_viec
    from app.mo_hinh.khuon_mat import KhuonMat
    from app.mo_hinh.sinh_vien import SinhVien

    with mo_phien_lam_viec() as phien:
        phien.query(KhuonMat).filter_by(sinh_vien_id=sinh_vien_id).delete()
        ban_ghi = phien.get(SinhVien, sinh_vien_id)
        if ban_ghi is not None:
            phien.delete(ban_ghi)
        phien.commit()


def test_dang_ky_khuon_mat_that_bai_khi_khong_phat_hien_duoc_khuon_mat(
    sinh_vien_tam_de_dang_ky_khuon_mat,
) -> None:
    """Anh nhieu ngau nhien khong chua khuon mat thuc su nen phai bi tu choi dang ky."""
    anh_khong_co_khuon_mat = (np.random.rand(240, 320, 3) * 255).astype(np.uint8)
    with pytest.raises(LoiDangKyKhuonMat):
        dang_ky_khuon_mat_tu_anh(
            "ADMIN",
            sinh_vien_tam_de_dang_ky_khuon_mat,
            anh_khong_co_khuon_mat,
            nguoi_thuc_hien_id=1,
        )


def test_xoa_khuon_mat_khong_ton_tai_phat_sinh_loi() -> None:
    with pytest.raises(LoiDangKyKhuonMat):
        xoa_khuon_mat("ADMIN", khuon_mat_id=999999999, nguoi_thuc_hien_id=1)
