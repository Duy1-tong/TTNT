"""
Module dieu phoi toan bo pipeline nhan dien khuon mat:

    OpenCV (doc khung hinh)
        -> BoPhatHienKhuonMat (YOLO / DNN / Haar Cascade)
        -> Can chinh & cat khuon mat (Face Alignment don gian)
        -> BoTaoEmbedding (InsightFace / ArcFace hoac du phong OpenCV)
        -> BoKiemTraNguoiThat (Liveness Detection)
        -> so_sanh_khuon_mat (Cosine Similarity)
        -> Ket qua nhan dien sinh vien

Day la lop duy nhat ma tang Service (app/dich_vu) nen goi truc tiep khi
can thuc hien nhan dien khuon mat; cac module con ben trong (phat hien,
embedding, so sanh, liveness) khong nen duoc goi rai rac tu giao dien.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

from app.tri_tue_nhan_tao.kiem_tra_nguoi_that import (
    BoKiemTraNguoiThat,
    KetQuaKiemTraNguoiThat,
)
from app.tri_tue_nhan_tao.phat_hien_khuon_mat import (
    BoPhatHienKhuonMat,
    HopGioiHanKhuonMat,
)
from app.tri_tue_nhan_tao.so_sanh_khuon_mat import (
    KetQuaSoSanh,
    tim_sinh_vien_phu_hop_nhat,
)
from app.tri_tue_nhan_tao.tao_embedding import (
    BoTaoEmbedding,
)


_bo_ghi_log = logging.getLogger(__name__)


@dataclass
class KetQuaNhanDien:
    """Ket qua tong hop cua mot lan chay pipeline nhan dien khuon mat."""

    tim_thay_khuon_mat: bool
    hop_gioi_han: HopGioiHanKhuonMat | None
    embedding: np.ndarray | None
    ket_qua_so_sanh: KetQuaSoSanh | None
    ket_qua_nguoi_that: KetQuaKiemTraNguoiThat | None
    thong_bao: str


class BoNhanDienKhuonMat:
    """Dieu phoi toan bo pipeline: phat hien -> embedding -> lien nguoi that -> so sanh."""

    def __init__(self) -> None:
        self.bo_phat_hien = BoPhatHienKhuonMat()
        self.bo_tao_embedding = BoTaoEmbedding()
        self.bo_kiem_tra_nguoi_that = BoKiemTraNguoiThat()

        _bo_ghi_log.info(
            "Khoi tao pipeline nhan dien: phat hien=%s, embedding=%s",
            self.bo_phat_hien.ten_phuong_phap_dang_dung,
            self.bo_tao_embedding.ten_mo_hinh,
        )

    @staticmethod
    def _kiem_tra_so_luong_khuon_mat(
        cac_hop: list[HopGioiHanKhuonMat],
    ) -> tuple[bool, str]:

        if not cac_hop:
            return (
                False,
                "Khong phat hien duoc khuon mat.",
            )

        if len(cac_hop) > 1:
            return (
                False,
                f"Phat hien {len(cac_hop)} khuon mat. "
                "Vui long chi co mot sinh vien truoc camera.",
            )

        return (
            True,
            "Chi co mot khuon mat.",
        )

    def trich_xuat_embedding_tu_anh(
        self,
        anh_bgr: np.ndarray,
    ) -> KetQuaNhanDien:
        """Phat hien khuon mat lon nhat trong anh va tra ve embedding tuong ung.

        Dung khi DANG KY khuon mat moi cho sinh vien
        (khong can kiem tra nguoi that).
        """

        cac_hop = self.bo_phat_hien.phat_hien(
            anh_bgr
        )

        if not cac_hop:
            return KetQuaNhanDien(
                tim_thay_khuon_mat=False,
                hop_gioi_han=None,
                embedding=None,
                ket_qua_so_sanh=None,
                ket_qua_nguoi_that=None,
                thong_bao=(
                    "Khong phat hien duoc khuon mat nao "
                    "trong anh. Vui long thu lai."
                ),
            )

        hop_lon_nhat = max(
            cac_hop,
            key=lambda hop: hop.rong * hop.cao,
        )

        anh_khuon_mat = hop_lon_nhat.cat_anh(
            anh_bgr
        )

        embedding = self.bo_tao_embedding.tao_embedding(
            anh_khuon_mat
        )

        if embedding is None:
            return KetQuaNhanDien(
                tim_thay_khuon_mat=True,
                hop_gioi_han=hop_lon_nhat,
                embedding=None,
                ket_qua_so_sanh=None,
                ket_qua_nguoi_that=None,
                thong_bao=(
                    "Phat hien duoc khuon mat "
                    "nhung khong the trich xuat "
                    "dac trung."
                ),
            )

        return KetQuaNhanDien(
            tim_thay_khuon_mat=True,
            hop_gioi_han=hop_lon_nhat,
            embedding=embedding,
            ket_qua_so_sanh=None,
            ket_qua_nguoi_that=None,
            thong_bao=(
                "Trich xuat embedding thanh cong."
            ),
        )

    def nhan_dien_de_diem_danh(
        self,
        danh_sach_khung_hinh_gan_nhat: list[np.ndarray],
        danh_sach_embedding_da_dang_ky: list[
            tuple[int, np.ndarray]
        ],
        nguong_do_tuong_dong: float,
        yeu_cau_kiem_tra_nguoi_that: bool = True,
    ) -> KetQuaNhanDien:
        """Chay toan bo pipeline tren khung hinh moi nhat de phuc vu diem danh.

        `danh_sach_khung_hinh_gan_nhat` la vai khung hinh camera gan nhat (BGR)
        dung de: (1) phat hien + embedding tren khung hinh cuoi, (2) kiem tra
        nguoi that dua tren su chenh lech giua cac khung hinh.
        """

        if not danh_sach_khung_hinh_gan_nhat:
            return KetQuaNhanDien(
                tim_thay_khuon_mat=False,
                hop_gioi_han=None,
                embedding=None,
                ket_qua_so_sanh=None,
                ket_qua_nguoi_that=None,
                thong_bao="Khong co du lieu tu camera.",
            )

        khung_hinh_hien_tai = (
            danh_sach_khung_hinh_gan_nhat[-1]
        )

        cac_hop = self.bo_phat_hien.phat_hien(
            khung_hinh_hien_tai
        )

        if not cac_hop:
            return KetQuaNhanDien(
                tim_thay_khuon_mat=False,
                hop_gioi_han=None,
                embedding=None,
                ket_qua_so_sanh=None,
                ket_qua_nguoi_that=None,
                thong_bao=(
                    "Khong phat hien duoc khuon mat "
                    "trong khung hinh camera."
                ),
            )

        hop_lon_nhat = max(
            cac_hop,
            key=lambda hop: hop.rong * hop.cao,
        )

        ket_qua_nguoi_that: (
            KetQuaKiemTraNguoiThat | None
        ) = None

        if yeu_cau_kiem_tra_nguoi_that:
            cac_anh_khuon_mat = []

            for khung_hinh in (
                danh_sach_khung_hinh_gan_nhat
            ):
                cac_hop_tung_khung = (
                    self.bo_phat_hien.phat_hien(
                        khung_hinh
                    )
                )

                if not cac_hop_tung_khung:
                    continue

                hop_tung_khung = max(
                    cac_hop_tung_khung,
                    key=lambda hop: (
                        hop.rong * hop.cao
                    ),
                )

                anh_khuon_mat = (
                    hop_tung_khung.cat_anh(
                        khung_hinh
                    )
                )

                if (
                    anh_khuon_mat is not None
                    and anh_khuon_mat.size > 0
                ):
                    cac_anh_khuon_mat.append(
                        anh_khuon_mat
                    )

            ket_qua_nguoi_that = (
                self.bo_kiem_tra_nguoi_that.kiem_tra(
                    cac_anh_khuon_mat
                )
            )

            if not ket_qua_nguoi_that.la_nguoi_that:
                return KetQuaNhanDien(
                    tim_thay_khuon_mat=True,
                    hop_gioi_han=hop_lon_nhat,
                    embedding=None,
                    ket_qua_so_sanh=None,
                    ket_qua_nguoi_that=(
                        ket_qua_nguoi_that
                    ),
                    thong_bao=(
                        "Khong vuot qua kiem tra "
                        "nguoi that: "
                        f"{ket_qua_nguoi_that.ghi_chu}"
                    ),
                )

        anh_khuon_mat = hop_lon_nhat.cat_anh(
            khung_hinh_hien_tai
        )

        embedding = self.bo_tao_embedding.tao_embedding(
            anh_khuon_mat
        )

        if embedding is None:
            return KetQuaNhanDien(
                tim_thay_khuon_mat=True,
                hop_gioi_han=hop_lon_nhat,
                embedding=None,
                ket_qua_so_sanh=None,
                ket_qua_nguoi_that=ket_qua_nguoi_that,
                thong_bao=(
                    "Khong the trich xuat "
                    "dac trung khuon mat."
                ),
            )

        ket_qua_so_sanh = (
            tim_sinh_vien_phu_hop_nhat(
                embedding,
                danh_sach_embedding_da_dang_ky,
                nguong_do_tuong_dong,
            )
        )

        if ket_qua_so_sanh is None:
            return KetQuaNhanDien(
                tim_thay_khuon_mat=True,
                hop_gioi_han=hop_lon_nhat,
                embedding=embedding,
                ket_qua_so_sanh=None,
                ket_qua_nguoi_that=ket_qua_nguoi_that,
                thong_bao=(
                    "Khong tim thay sinh vien nao "
                    "khop voi khuon mat nay trong "
                    "he thong."
                ),
            )

        return KetQuaNhanDien(
            tim_thay_khuon_mat=True,
            hop_gioi_han=hop_lon_nhat,
            embedding=embedding,
            ket_qua_so_sanh=ket_qua_so_sanh,
            ket_qua_nguoi_that=ket_qua_nguoi_that,
            thong_bao="Nhan dien thanh cong.",
        )