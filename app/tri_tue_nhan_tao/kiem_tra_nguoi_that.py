"""
Module kiem tra nguoi that (Liveness Detection / Anti-Spoofing).

Muc tieu: han che truong hop diem danh ho bang anh chup, video quay lai
mot khuon mat tren man hinh dien thoai/may tinh.

Ap dung hai phuong phap nhe (khong can model AI rieng, chay realtime tren
CPU) va ket hop diem so:

1. Phan tich do net tan so cao (Laplacian variance): anh chup lai tu man
   hinh/anh in thuong bi mat chi tiet tan so cao, giam do net cuc bo.
2. Phan tich chuyen dong tu nhien giua nhieu khung hinh lien tiep: nguoi
   that luon co chuyen dong nho (rung mi mat, rung co mat...), trong khi
   anh tinh hoac video phat lai tren man hinh phang thuong cho chuyen
   dong dong nhat hoac hoan toan khong doi trong vung khuon mat.

Day la giai phap can bang giua chi phi trien khai va hieu qua thuc te cho
do an sinh vien, khong thay the hoan toan cac giai phap liveness detection
thuong mai dua tren tia hong ngoai/3D.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


NGUONG_DO_NET_TOI_THIEU = 20.0
NGUONG_CHUYEN_DONG_TOI_THIEU = 0.2
NGUONG_CHUYEN_DONG_TOI_DA = 40.0


@dataclass
class KetQuaKiemTraNguoiThat:
    """Ket qua kiem tra liveness cho mot chuoi khung hinh khuon mat."""

    la_nguoi_that: bool
    diem_do_net: float
    diem_chuyen_dong: float
    ghi_chu: str


class BoKiemTraNguoiThat:
    """Kiem tra nguoi that dua tren do net anh va chuyen dong tu nhien giua cac khung hinh."""

    def kiem_tra(
        self, danh_sach_khung_hinh_khuon_mat: list[np.ndarray]
    ) -> KetQuaKiemTraNguoiThat:
        """Nhan vao danh sach it nhat 2 anh khuon mat da cat lien tiep tu camera."""

        if not danh_sach_khung_hinh_khuon_mat:
            return KetQuaKiemTraNguoiThat(
                la_nguoi_that=False,
                diem_do_net=0.0,
                diem_chuyen_dong=0.0,
                ghi_chu="Khong co du lieu khung hinh de kiem tra.",
            )

        diem_do_net = self._tinh_diem_do_net(
            danh_sach_khung_hinh_khuon_mat
        )

        if len(danh_sach_khung_hinh_khuon_mat) >= 2:
            diem_chuyen_dong = self._tinh_diem_chuyen_dong(
                danh_sach_khung_hinh_khuon_mat
            )
        else:
            diem_chuyen_dong = None

        net_dat_yeu_cau = (
            diem_do_net >= NGUONG_DO_NET_TOI_THIEU
        )

        chuyen_dong_dat_yeu_cau = (
            diem_chuyen_dong is None
            or NGUONG_CHUYEN_DONG_TOI_THIEU
            <= diem_chuyen_dong
            <= NGUONG_CHUYEN_DONG_TOI_DA
        )

        la_nguoi_that = (
            net_dat_yeu_cau
            and chuyen_dong_dat_yeu_cau
        )

        ghi_chu = self._tao_ghi_chu(
            net_dat_yeu_cau,
            chuyen_dong_dat_yeu_cau,
            diem_do_net,
            diem_chuyen_dong,
        )

        return KetQuaKiemTraNguoiThat(
            la_nguoi_that=la_nguoi_that,
            diem_do_net=diem_do_net,
            diem_chuyen_dong=(
                diem_chuyen_dong
                if diem_chuyen_dong is not None
                else -1.0
            ),
            ghi_chu=ghi_chu,
        )

    @staticmethod
    def _tinh_diem_do_net(
        danh_sach_khung_hinh: list[np.ndarray],
    ) -> float:
        """Tinh phuong sai Laplacian trung binh — chi so danh gia do net/chi tiet anh."""

        cac_gia_tri_do_net = []

        for khung_hinh in danh_sach_khung_hinh:
            if khung_hinh is None or khung_hinh.size == 0:
                continue

            anh_xam = cv2.cvtColor(
                khung_hinh,
                cv2.COLOR_BGR2GRAY,
            )

            cac_gia_tri_do_net.append(
                cv2.Laplacian(
                    anh_xam,
                    cv2.CV_64F,
                ).var()
            )

        return (
            float(np.mean(cac_gia_tri_do_net))
            if cac_gia_tri_do_net
            else 0.0
        )

    @staticmethod
    def _tinh_diem_chuyen_dong(
        danh_sach_khung_hinh: list[np.ndarray],
    ) -> float:
        """Tinh muc do thay doi giua cac khung hinh khuon mat."""

        kich_thuoc_chuan = (96, 96)
        cac_anh_xam = []

        for khung_hinh in danh_sach_khung_hinh:
            if khung_hinh is None or khung_hinh.size == 0:
                continue

            anh_xam = cv2.cvtColor(
                khung_hinh,
                cv2.COLOR_BGR2GRAY,
            )

            anh_xam = cv2.resize(
                anh_xam,
                kich_thuoc_chuan,
            )

            # Lam mo nhe de giam nhieu do camera
            anh_xam = cv2.GaussianBlur(
                anh_xam,
                (5, 5),
                0,
            )

            cac_anh_xam.append(
                anh_xam.astype(np.float32)
            )

        if len(cac_anh_xam) < 2:
            return 0.0

        cac_chenh_lech = []

        for i in range(1, len(cac_anh_xam)):
            chenh_lech = np.mean(
                np.abs(
                    cac_anh_xam[i]
                    - cac_anh_xam[i - 1]
                )
            )

            cac_chenh_lech.append(
                chenh_lech
            )

        return float(
            np.mean(cac_chenh_lech)
        )

    @staticmethod
    def _tao_ghi_chu(
        net_dat_yeu_cau: bool,
        chuyen_dong_dat_yeu_cau: bool,
        diem_do_net: float,
        diem_chuyen_dong: float | None,
    ) -> str:
        """Tao ghi chu ket qua kiem tra nguoi that."""

        if (
            net_dat_yeu_cau
            and chuyen_dong_dat_yeu_cau
        ):
            return "Dat yeu cau kiem tra nguoi that."

        if not net_dat_yeu_cau:
            return (
                f"Do net qua thap "
                f"(diem={diem_do_net:.2f}, "
                f"nguong={NGUONG_DO_NET_TOI_THIEU:.2f}) — "
                "vui long dua khuon mat gan camera hon."
            )

        if (
            diem_chuyen_dong is not None
            and diem_chuyen_dong
            < NGUONG_CHUYEN_DONG_TOI_THIEU
        ):
            return (
                "Khong phat hien chuyen dong tu nhien "
                "giua cac khung hinh — nghi ngo la "
                "anh tinh hoac video dung hinh. "
                "Vui long giu yen va nhin thang "
                "vao camera."
            )

        return (
            "Phat hien chuyen dong bat thuong "
            "(qua nhieu) — vui long giu on dinh "
            "khuon mat truoc camera trong qua "
            "trinh kiem tra."
        )