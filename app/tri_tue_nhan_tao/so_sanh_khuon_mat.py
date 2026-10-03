"""Module so sanh embedding khuon mat bang do tuong dong cosine (cosine similarity)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class KetQuaSoSanh:
    """Ket qua so sanh mot embedding voi mot sinh vien da dang ky."""

    sinh_vien_id: int
    do_tuong_dong: float


def tinh_do_tuong_dong_cosine(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """Tinh cosine similarity giua hai vector, tra ve gia tri trong [-1, 1]."""
    if vector_a is None or vector_b is None:
        return -1.0
    if vector_a.shape != vector_b.shape:
        return -1.0
    chuan_a = np.linalg.norm(vector_a)
    chuan_b = np.linalg.norm(vector_b)
    if chuan_a == 0 or chuan_b == 0:
        return -1.0
    return float(np.dot(vector_a, vector_b) / (chuan_a * chuan_b))


def tim_sinh_vien_phu_hop_nhat(
    embedding_can_kiem_tra: np.ndarray,
    danh_sach_embedding_da_dang_ky: list[tuple[int, np.ndarray]],
    nguong_do_tuong_dong: float,
) -> KetQuaSoSanh | None:
    """So sanh embedding can kiem tra voi toan bo embedding da dang ky trong CSDL.

    `danh_sach_embedding_da_dang_ky` la danh sach (sinh_vien_id, vector_embedding).
    Tra ve KetQuaSoSanh cua sinh vien co do tuong dong cao nhat NEU do tuong
    dong do >= nguong_do_tuong_dong, nguoc lai tra ve None (khong nhan dien duoc).
    """
    ket_qua_tot_nhat: KetQuaSoSanh | None = None
    for sinh_vien_id, vector_da_dang_ky in danh_sach_embedding_da_dang_ky:
        do_tuong_dong = tinh_do_tuong_dong_cosine(embedding_can_kiem_tra, vector_da_dang_ky)
        if ket_qua_tot_nhat is None or do_tuong_dong > ket_qua_tot_nhat.do_tuong_dong:
            ket_qua_tot_nhat = KetQuaSoSanh(sinh_vien_id=sinh_vien_id, do_tuong_dong=do_tuong_dong)

    if ket_qua_tot_nhat is None or ket_qua_tot_nhat.do_tuong_dong < nguong_do_tuong_dong:
        return None
    return ket_qua_tot_nhat
