"""Man hinh Bao Cao: thong ke diem danh theo lop hoc phan / ca nhan, xuat Excel & PDF."""

from __future__ import annotations

import datetime as _datetime

from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.dich_vu import bao_cao as dv_bao_cao
from app.dich_vu import danh_muc
from app.dich_vu import sinh_vien as dv_sinh_vien
from app.dich_vu.phan_quyen import QuyenHeThong, co_quyen
from app.dich_vu.xac_thuc import PhienDangNhap


class TrangBaoCao(QWidget):
    """Trang bao cao: Admin/Giang vien xem thong ke lop hoc phan, Sinh vien xem lich su ca nhan."""

    def __init__(self, phien_dang_nhap: PhienDangNhap) -> None:
        super().__init__()
        self.phien_dang_nhap = phien_dang_nhap
        self._du_lieu_bao_cao_hien_tai: list[dv_bao_cao.DongBaoCaoSinhVien] = []

        if co_quyen(phien_dang_nhap.vai_tro, QuyenHeThong.XUAT_BAO_CAO):
            self._xay_dung_giao_dien_bao_cao_lop()
        else:
            self._xay_dung_giao_dien_ca_nhan()

    # ------------------------------------------------------------------
    # BAO CAO THEO LOP HOC PHAN (ADMIN / GIANG_VIEN)
    # ------------------------------------------------------------------
    def _xay_dung_giao_dien_bao_cao_lop(self) -> None:
        bo_cuc = QVBoxLayout(self)
        bo_cuc.setContentsMargins(28, 24, 28, 24)
        bo_cuc.setSpacing(14)

        nhan_tieu_de = QLabel("Báo Cáo Điểm Danh")
        nhan_tieu_de.setObjectName("nhanTieuDeTrang")
        bo_cuc.addWidget(nhan_tieu_de)

        hang_bo_loc = QHBoxLayout()
        hang_bo_loc.addWidget(QLabel("Lớp học phần:"))
        self._o_lop_mon = QComboBox()
        for lop_mon in danh_muc.lay_danh_sach_lop_mon_hoc():
            self._o_lop_mon.addItem(f"{lop_mon.ma_lop_mon} - {lop_mon.ten_mon}", lop_mon.id)
        hang_bo_loc.addWidget(self._o_lop_mon, stretch=1)

        hang_bo_loc.addWidget(QLabel("Từ ngày:"))
        self._o_tu_ngay = QDateEdit()
        self._o_tu_ngay.setCalendarPopup(True)
        self._o_tu_ngay.setDate(_datetime.date.today().replace(day=1))
        hang_bo_loc.addWidget(self._o_tu_ngay)

        hang_bo_loc.addWidget(QLabel("Đến ngày:"))
        self._o_den_ngay = QDateEdit()
        self._o_den_ngay.setCalendarPopup(True)
        self._o_den_ngay.setDate(_datetime.date.today())
        hang_bo_loc.addWidget(self._o_den_ngay)

        nut_thong_ke = QPushButton("Thống Kê")
        nut_thong_ke.setObjectName("nutChinh")
        nut_thong_ke.clicked.connect(self._xu_ly_thong_ke)
        hang_bo_loc.addWidget(nut_thong_ke)
        bo_cuc.addLayout(hang_bo_loc)

        self._bang = QTableWidget(0, 8)
        self._bang.setHorizontalHeaderLabels(
            [
                "Mã SV", "Họ tên", "Có mặt", "Đi muộn", "Vắng", "Có phép",
                "Tổng số buổi", "Tỷ lệ có mặt (%)",
            ]
        )
        self._bang.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._bang.horizontalHeader().setStretchLastSection(False)
        self._bang.horizontalHeader().setMinimumSectionSize(88)
        self._bang.setColumnWidth(0, 90)
        self._bang.setColumnWidth(2, 90)
        self._bang.setColumnWidth(3, 90)
        self._bang.setColumnWidth(4, 80)
        self._bang.setColumnWidth(5, 90)
        self._bang.setColumnWidth(6, 130)
        self._bang.setColumnWidth(7, 165)
        self._bang.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        bo_cuc.addWidget(self._bang, stretch=1)

        hang_xuat = QHBoxLayout()
        nut_xuat_excel = QPushButton("📊  Xuất Excel")
        nut_xuat_excel.clicked.connect(self._xu_ly_xuat_excel)
        nut_xuat_pdf = QPushButton("📄  Xuất PDF")
        nut_xuat_pdf.clicked.connect(self._xu_ly_xuat_pdf)
        hang_xuat.addWidget(nut_xuat_excel)
        hang_xuat.addWidget(nut_xuat_pdf)
        hang_xuat.addStretch(1)
        bo_cuc.addLayout(hang_xuat)

    def _xu_ly_thong_ke(self) -> None:
        lop_mon_hoc_id = self._o_lop_mon.currentData()
        if lop_mon_hoc_id is None:
            QMessageBox.information(self, "Chưa có lớp", "Hệ thống chưa có lớp học phần nào.")
            return
        try:
            self._du_lieu_bao_cao_hien_tai = dv_bao_cao.bao_cao_theo_lop_mon_hoc(
                self.phien_dang_nhap.vai_tro,
                lop_mon_hoc_id,
                tu_ngay=self._o_tu_ngay.date().toPython(),
                den_ngay=self._o_den_ngay.date().toPython(),
            )
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể tạo báo cáo", str(loi))
            return

        self._bang.setRowCount(len(self._du_lieu_bao_cao_hien_tai))
        for hang, dong in enumerate(self._du_lieu_bao_cao_hien_tai):
            gia_tri_cac_cot = [
                dong.ma_sinh_vien, dong.ho_ten, str(dong.so_buoi_co_mat),
                str(dong.so_buoi_di_muon), str(dong.so_buoi_vang), str(dong.so_buoi_co_phep),
                str(dong.tong_so_buoi), f"{dong.ty_le_co_mat_phan_tram:.1f}",
            ]
            for cot, gia_tri in enumerate(gia_tri_cac_cot):
                self._bang.setItem(hang, cot, QTableWidgetItem(gia_tri))

    def _xu_ly_xuat_excel(self) -> None:
        if not self._du_lieu_bao_cao_hien_tai:
            QMessageBox.information(self, "Chưa có dữ liệu", "Vui lòng bấm Thống Kê trước.")
            return
        ten_file = f"bao_cao_diem_danh_{_datetime.date.today().isoformat()}.xlsx"
        try:
            duong_dan = dv_bao_cao.xuat_bao_cao_lop_ra_excel(
                self._du_lieu_bao_cao_hien_tai,
                "Báo Cáo Điểm Danh",
                ten_file,
                nguoi_thuc_hien_id=self.phien_dang_nhap.nguoi_dung_id,
            )
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể xuất Excel", str(loi))
            return
        QMessageBox.information(self, "Thành công", f"Đã xuất báo cáo Excel tại:\n{duong_dan}")

    def _xu_ly_xuat_pdf(self) -> None:
        if not self._du_lieu_bao_cao_hien_tai:
            QMessageBox.information(self, "Chưa có dữ liệu", "Vui lòng bấm Thống Kê trước.")
            return
        ten_file = f"bao_cao_diem_danh_{_datetime.date.today().isoformat()}.pdf"
        try:
            duong_dan = dv_bao_cao.xuat_bao_cao_lop_ra_pdf(
                self._du_lieu_bao_cao_hien_tai,
                "Báo Cáo Điểm Danh",
                ten_file,
                nguoi_thuc_hien_id=self.phien_dang_nhap.nguoi_dung_id,
            )
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể xuất PDF", str(loi))
            return
        QMessageBox.information(self, "Thành công", f"Đã xuất báo cáo PDF tại:\n{duong_dan}")

    # ------------------------------------------------------------------
    # LICH SU CA NHAN (SINH_VIEN)
    # ------------------------------------------------------------------
    def _xay_dung_giao_dien_ca_nhan(self) -> None:
        bo_cuc = QVBoxLayout(self)
        bo_cuc.setContentsMargins(28, 24, 28, 24)
        bo_cuc.setSpacing(14)

        nhan_tieu_de = QLabel("Lịch Sử Điểm Danh Của Tôi")
        nhan_tieu_de.setObjectName("nhanTieuDeTrang")
        bo_cuc.addWidget(nhan_tieu_de)

        thong_tin_sinh_vien = dv_sinh_vien.lay_sinh_vien_theo_nguoi_dung_id(
            self.phien_dang_nhap.nguoi_dung_id
        )
        if thong_tin_sinh_vien is None:
            bo_cuc.addWidget(QLabel("Tài khoản này chưa được liên kết với hồ sơ sinh viên nào."))
            return

        bang = QTableWidget(0, 5)
        bang.setHorizontalHeaderLabels(
            ["Ngày học", "Môn học", "Lớp học phần", "Trạng thái", "Phương thức"]
        )
        bang.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        bang.horizontalHeader().setStretchLastSection(False)
        bang.horizontalHeader().setMinimumSectionSize(88)
        bang.setColumnWidth(0, 100)
        bang.setColumnWidth(2, 140)
        bang.setColumnWidth(3, 100)
        bang.setColumnWidth(4, 110)
        bang.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        danh_sach = _lay_lich_su_diem_danh_ca_nhan(thong_tin_sinh_vien.id)

        bang.setRowCount(len(danh_sach))
        bang_trang_thai = {
            "CO_MAT": "Có mặt", "DI_MUON": "Đi muộn", "VANG": "Vắng", "CO_PHEP": "Có phép",
        }
        bang_phuong_thuc = {"KHUON_MAT": "Khuôn mặt", "THU_CONG": "Thủ công"}
        for hang, dong in enumerate(danh_sach):
            gia_tri_cac_cot = [
                str(dong["ngay_hoc"]),
                dong["ten_mon"],
                dong["ma_lop_mon"],
                bang_trang_thai.get(dong["trang_thai"], dong["trang_thai"]),
                bang_phuong_thuc.get(dong["phuong_thuc"], dong["phuong_thuc"]),
            ]
            for cot, gia_tri in enumerate(gia_tri_cac_cot):
                bang.setItem(hang, cot, QTableWidgetItem(gia_tri))

        bo_cuc.addWidget(bang, stretch=1)


def _lay_lich_su_diem_danh_ca_nhan(sinh_vien_id: int) -> list[dict]:
    """Truy van lich su diem danh chi tiet cho mot sinh vien (dung cho man hinh ca nhan,
    khong yeu cau quyen XUAT_BAO_CAO — sinh vien chi duoc xem du lieu cua chinh minh)."""
    from app.co_so_du_lieu.ket_noi import mo_phien_lam_viec
    from app.mo_hinh.buoi_hoc import BuoiHoc
    from app.mo_hinh.diem_danh import DiemDanh
    from app.mo_hinh.lop_mon_hoc import LopMonHoc
    from app.mo_hinh.mon_hoc import MonHoc

    with mo_phien_lam_viec() as phien:
        truy_van = (
            phien.query(DiemDanh, BuoiHoc, LopMonHoc, MonHoc)
            .join(BuoiHoc, DiemDanh.buoi_hoc_id == BuoiHoc.id)
            .join(LopMonHoc, BuoiHoc.lop_mon_hoc_id == LopMonHoc.id)
            .join(MonHoc, LopMonHoc.mon_hoc_id == MonHoc.id)
            .filter(DiemDanh.sinh_vien_id == sinh_vien_id)
            .order_by(BuoiHoc.ngay_hoc.desc())
        )
        return [
            {
                "ngay_hoc": buoi.ngay_hoc,
                "ten_mon": mon.ten_mon,
                "ma_lop_mon": lop_mon.ma_lop_mon,
                "trang_thai": diem_danh.trang_thai.value,
                "phuong_thuc": diem_danh.phuong_thuc.value,
            }
            for diem_danh, buoi, lop_mon, mon in truy_van.all()
        ]
