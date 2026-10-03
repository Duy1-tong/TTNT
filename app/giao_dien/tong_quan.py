"""Man hinh Tong Quan (Dashboard): thong ke nhanh va bieu do diem danh hom nay."""

from __future__ import annotations

import datetime as _datetime

import matplotlib

matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.co_so_du_lieu.ket_noi import mo_phien_lam_viec
from app.dich_vu.xac_thuc import PhienDangNhap
from app.mo_hinh.buoi_hoc import BuoiHoc
from app.mo_hinh.diem_danh import DiemDanh, TrangThaiDiemDanh
from app.mo_hinh.giang_vien import GiangVien
from app.mo_hinh.lop_hoc import LopHoc
from app.mo_hinh.lop_mon_hoc import LopMonHoc
from app.mo_hinh.sinh_vien import SinhVien, TrangThaiSinhVien
from app.tien_ich.hieu_ung_giao_dien import ap_dung_do_bong

# Bang mau "xanh pastel sang trong" dung rieng cho dashboard: cac sac do
# deu nam trong ho xanh duong - xanh ngoc - xanh chi de giu su hai hoa,
# chi khac nhau ve do dam nhat, thay vi cac mau tuong phan manh (do/vang/luc).
_MAU_THONG_KE = ["#5B9BD5", "#4FA6A0", "#6E8FCB", "#3E76AA"]
_BIEU_TUONG_THONG_KE = ["🧑‍🎓", "🏫", "📚", "📅"]


class TheThongKe(QFrame):
    """Mot the (card) hien thi mot con so thong ke don le, phong cach the noi mem mai."""

    def __init__(self, tieu_de: str, gia_tri: str, mau_nhan: str, bieu_tuong: str) -> None:
        super().__init__()
        self.setObjectName("theThongKe")
        self.setMinimumHeight(108)
        self.setStyleSheet(
            f"#theThongKe {{ background-color: #FFFFFF; border-radius: 16px; "
            f"border: 1px solid #E4EEF7; border-left: 4px solid {mau_nhan}; }}"
        )
        ap_dung_do_bong(self, do_mo=22, do_lech_y=5)

        bo_cuc = QHBoxLayout(self)
        bo_cuc.setContentsMargins(18, 16, 20, 16)
        bo_cuc.setSpacing(14)

        khung_bieu_tuong = QFrame()
        khung_bieu_tuong.setObjectName("khungBieuTuongThongKe")
        khung_bieu_tuong.setFixedSize(48, 48)
        khung_bieu_tuong.setStyleSheet(
            f"#khungBieuTuongThongKe {{ background-color: {_pha_nhat(mau_nhan)}; "
            f"border-radius: 12px; }}"
        )
        bo_cuc_icon = QVBoxLayout(khung_bieu_tuong)
        bo_cuc_icon.setContentsMargins(0, 0, 0, 0)
        nhan_icon = QLabel(bieu_tuong)
        nhan_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nhan_icon.setStyleSheet("font-size: 20px; background: transparent;")
        bo_cuc_icon.addWidget(nhan_icon)
        bo_cuc.addWidget(khung_bieu_tuong)

        khung_van_ban = QVBoxLayout()
        khung_van_ban.setSpacing(2)
        nhan_gia_tri = QLabel(gia_tri)
        nhan_gia_tri.setObjectName("nhanGiaTriThongKe")
        nhan_tieu_de = QLabel(tieu_de)
        nhan_tieu_de.setObjectName("nhanTieuDeThongKe")
        khung_van_ban.addWidget(nhan_gia_tri)
        khung_van_ban.addWidget(nhan_tieu_de)
        bo_cuc.addLayout(khung_van_ban, stretch=1)


def _pha_nhat(ma_mau_hex: str) -> str:
    """Pha mot mau hex dam thanh phien ban pastel nhat hon (dung lam nen icon)."""
    ma_mau_hex = ma_mau_hex.lstrip("#")
    do_do, do_xanh_la, do_xanh_duong = (int(ma_mau_hex[i : i + 2], 16) for i in (0, 2, 4))
    he_so = 0.82
    do_do = int(do_do + (255 - do_do) * he_so)
    do_xanh_la = int(do_xanh_la + (255 - do_xanh_la) * he_so)
    do_xanh_duong = int(do_xanh_duong + (255 - do_xanh_duong) * he_so)
    return f"#{do_do:02X}{do_xanh_la:02X}{do_xanh_duong:02X}"


class TrangTongQuan(QWidget):
    """Trang tong quan he thong: hien thi ngay sau khi dang nhap."""

    def __init__(self, phien_dang_nhap: PhienDangNhap) -> None:
        super().__init__()
        self.phien_dang_nhap = phien_dang_nhap
        self._xay_dung_giao_dien()

    def _xay_dung_giao_dien(self) -> None:
        cuon = QScrollArea()
        cuon.setWidgetResizable(True)
        cuon.setFrameShape(QFrame.Shape.NoFrame)
        noi_dung = QWidget()
        bo_cuc = QVBoxLayout(noi_dung)
        bo_cuc.setContentsMargins(28, 24, 28, 24)
        bo_cuc.setSpacing(22)

        nhan_tieu_de = QLabel("Tổng Quan Hệ Thống")
        nhan_tieu_de.setObjectName("nhanTieuDeTrang")
        bo_cuc.addWidget(nhan_tieu_de)

        thong_ke = self._tinh_toan_thong_ke()

        luoi_the = QGridLayout()
        luoi_the.setSpacing(18)
        du_lieu_the = [
            ("Tổng số sinh viên", thong_ke["tong_sinh_vien"]),
            ("Lớp hành chính", thong_ke["tong_lop_hoc"]),
            ("Lớp học phần", thong_ke["tong_lop_mon_hoc"]),
            ("Buổi học hôm nay", thong_ke["so_buoi_hoc_hom_nay"]),
        ]
        for chi_so, (nhan, gia_tri) in enumerate(du_lieu_the):
            the = TheThongKe(
                nhan, str(gia_tri), _MAU_THONG_KE[chi_so], _BIEU_TUONG_THONG_KE[chi_so]
            )
            luoi_the.addWidget(the, 0, chi_so)
        bo_cuc.addLayout(luoi_the)

        nhan_bieu_do = QLabel("Thống Kê Điểm Danh Hôm Nay")
        nhan_bieu_do.setObjectName("nhanTieuDePhu")
        bo_cuc.addWidget(nhan_bieu_do)

        khung_bieu_do = QFrame()
        khung_bieu_do.setObjectName("theThongKe")
        khung_bieu_do.setStyleSheet(
            "#theThongKe { background-color: #FFFFFF; border-radius: 16px; "
            "border: 1px solid #E4EEF7; }"
        )
        ap_dung_do_bong(khung_bieu_do, do_mo=22, do_lech_y=5)
        bo_cuc_bieu_do = QVBoxLayout(khung_bieu_do)
        bo_cuc_bieu_do.setContentsMargins(16, 12, 16, 8)
        canvas = self._tao_bieu_do_diem_danh_hom_nay(thong_ke["thong_ke_diem_danh_hom_nay"])
        canvas.setMinimumHeight(300)
        bo_cuc_bieu_do.addWidget(canvas)
        bo_cuc.addWidget(khung_bieu_do)

        bo_cuc.addStretch(1)
        cuon.setWidget(noi_dung)

        bo_cuc_ngoai = QVBoxLayout(self)
        bo_cuc_ngoai.setContentsMargins(0, 0, 0, 0)
        bo_cuc_ngoai.addWidget(cuon)

    def _tinh_toan_thong_ke(self) -> dict:
        hom_nay = _datetime.date.today()
        with mo_phien_lam_viec() as phien:
            tong_sinh_vien = (
                phien.query(SinhVien)
                .filter(SinhVien.trang_thai == TrangThaiSinhVien.DANG_HOC)
                .count()
            )
            tong_lop_hoc = phien.query(LopHoc).count()
            tong_lop_mon_hoc = phien.query(LopMonHoc).count()
            cac_buoi_hom_nay = phien.query(BuoiHoc).filter(BuoiHoc.ngay_hoc == hom_nay).all()
            cac_buoi_hoc_id = [b.id for b in cac_buoi_hom_nay]

            thong_ke_diem_danh: dict[str, int] = {
                "CO_MAT": 0, "DI_MUON": 0, "VANG": 0, "CO_PHEP": 0
            }
            if cac_buoi_hoc_id:
                cac_ban_ghi = (
                    phien.query(DiemDanh).filter(DiemDanh.buoi_hoc_id.in_(cac_buoi_hoc_id)).all()
                )
                for bg in cac_ban_ghi:
                    thong_ke_diem_danh[bg.trang_thai.value] = (
                        thong_ke_diem_danh.get(bg.trang_thai.value, 0) + 1
                    )

        return {
            "tong_sinh_vien": tong_sinh_vien,
            "tong_lop_hoc": tong_lop_hoc,
            "tong_lop_mon_hoc": tong_lop_mon_hoc,
            "so_buoi_hoc_hom_nay": len(cac_buoi_hoc_id),
            "thong_ke_diem_danh_hom_nay": thong_ke_diem_danh,
        }

    @staticmethod
    def _tao_bieu_do_diem_danh_hom_nay(thong_ke: dict[str, int]) -> FigureCanvasQTAgg:
        nhan_cac_cot = ["Có mặt", "Đi muộn", "Vắng", "Có phép"]
        gia_tri_cac_cot = [
            thong_ke.get("CO_MAT", 0),
            thong_ke.get("DI_MUON", 0),
            thong_ke.get("VANG", 0),
            thong_ke.get("CO_PHEP", 0),
        ]
        # Bang mau pastel xanh dong bo voi giao dien: tu xanh duong nhat toi
        # xanh duong dam, giu tinh hai hoa "chu dao xanh pastel".
        mau_sac = ["#8FC1E3", "#6FADDA", "#5B9BD5", "#3E76AA"]

        figure = Figure(figsize=(6, 3.0))
        figure.patch.set_facecolor("#FFFFFF")
        truc = figure.add_subplot(111)
        truc.set_facecolor("#FFFFFF")
        thanh = truc.bar(nhan_cac_cot, gia_tri_cac_cot, color=mau_sac, width=0.55, zorder=3)
        truc.set_ylabel("Số lượt", color="#64798C", fontsize=10)
        truc.tick_params(colors="#64798C", labelsize=10)
        for vi_tri in ["top", "right", "left"]:
            truc.spines[vi_tri].set_visible(False)
        truc.spines["bottom"].set_color("#DCEAF5")
        truc.grid(axis="y", color="#EAF2FA", zorder=0)
        for thanh_don, gia_tri in zip(thanh, gia_tri_cac_cot):
            truc.text(
                thanh_don.get_x() + thanh_don.get_width() / 2, gia_tri, str(gia_tri),
                ha="center", va="bottom", color="#1F3A56", fontsize=10, fontweight="bold",
            )
        figure.tight_layout()
        return FigureCanvasQTAgg(figure)
