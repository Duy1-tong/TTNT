"""Man hinh Quan Ly Khoa - Lop: quan ly danh muc Khoa va Lop hanh chinh."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.dich_vu import danh_muc
from app.dich_vu.xac_thuc import PhienDangNhap


class HopThoaiKhoa(QDialog):
    """Hop thoai them moi mot Khoa."""

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Thêm Khoa Mới")
        self.setMinimumWidth(360)
        bo_cuc = QFormLayout(self)
        self._o_ma_khoa = QLineEdit()
        self._o_ten_khoa = QLineEdit()
        self._o_mo_ta = QLineEdit()
        bo_cuc.addRow("Mã khoa (*):", self._o_ma_khoa)
        bo_cuc.addRow("Tên khoa (*):", self._o_ten_khoa)
        bo_cuc.addRow("Mô tả:", self._o_mo_ta)
        nut = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        nut.accepted.connect(self.accept)
        nut.rejected.connect(self.reject)
        bo_cuc.addRow(nut)

    def lay_du_lieu_nhap(self) -> dict:
        return {
            "ma_khoa": self._o_ma_khoa.text().strip(),
            "ten_khoa": self._o_ten_khoa.text().strip(),
            "mo_ta": self._o_mo_ta.text().strip() or None,
        }


class HopThoaiLopHoc(QDialog):
    """Hop thoai them moi mot Lop hanh chinh."""

    def __init__(self, parent: QWidget | None, danh_sach_khoa: list[danh_muc.ThongTinKhoa]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Thêm Lớp Hành Chính Mới")
        self.setMinimumWidth(380)
        bo_cuc = QFormLayout(self)
        self._o_ma_lop = QLineEdit()
        self._o_ten_lop = QLineEdit()
        self._o_khoa_hoc = QLineEdit()
        self._o_khoa_hoc.setPlaceholderText("Ví dụ: 2021-2025")
        self._o_khoa = QComboBox()
        for khoa in danh_sach_khoa:
            self._o_khoa.addItem(f"{khoa.ma_khoa} - {khoa.ten_khoa}", khoa.id)
        bo_cuc.addRow("Mã lớp (*):", self._o_ma_lop)
        bo_cuc.addRow("Tên lớp (*):", self._o_ten_lop)
        bo_cuc.addRow("Khóa học:", self._o_khoa_hoc)
        bo_cuc.addRow("Khoa (*):", self._o_khoa)
        nut = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        nut.accepted.connect(self.accept)
        nut.rejected.connect(self.reject)
        bo_cuc.addRow(nut)

    def lay_du_lieu_nhap(self) -> dict:
        return {
            "ma_lop": self._o_ma_lop.text().strip(),
            "ten_lop": self._o_ten_lop.text().strip(),
            "khoa_hoc": self._o_khoa_hoc.text().strip() or None,
            "khoa_id": self._o_khoa.currentData(),
        }


class TrangQuanLyLop(QWidget):
    """Trang quan ly Khoa va Lop hanh chinh, chia lam 2 tab."""

    def __init__(self, phien_dang_nhap: PhienDangNhap) -> None:
        super().__init__()
        self.phien_dang_nhap = phien_dang_nhap
        self._xay_dung_giao_dien()
        self._nap_lai_tat_ca()

    def _xay_dung_giao_dien(self) -> None:
        bo_cuc = QVBoxLayout(self)
        bo_cuc.setContentsMargins(28, 24, 28, 24)
        bo_cuc.setSpacing(14)

        nhan_tieu_de = QLabel("Quản Lý Khoa - Lớp Hành Chính")
        nhan_tieu_de.setObjectName("nhanTieuDeTrang")
        bo_cuc.addWidget(nhan_tieu_de)

        tab = QTabWidget()

        # ----- Tab Khoa -----
        trang_khoa = QWidget()
        bo_cuc_khoa = QVBoxLayout(trang_khoa)
        hang_khoa = QHBoxLayout()
        hang_khoa.addStretch(1)
        nut_them_khoa = QPushButton("+ Thêm Khoa")
        nut_them_khoa.setObjectName("nutChinh")
        nut_them_khoa.clicked.connect(self._xu_ly_them_khoa)
        hang_khoa.addWidget(nut_them_khoa)
        bo_cuc_khoa.addLayout(hang_khoa)

        self._bang_khoa = QTableWidget(0, 3)
        self._bang_khoa.setHorizontalHeaderLabels(["Mã khoa", "Tên khoa", "Mô tả"])
        self._bang_khoa.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._bang_khoa.horizontalHeader().setStretchLastSection(False)
        self._bang_khoa.horizontalHeader().setMinimumSectionSize(88)
        self._bang_khoa.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        bo_cuc_khoa.addWidget(self._bang_khoa)
        tab.addTab(trang_khoa, "Khoa")

        # ----- Tab Lop hanh chinh -----
        trang_lop = QWidget()
        bo_cuc_lop = QVBoxLayout(trang_lop)
        hang_lop = QHBoxLayout()
        hang_lop.addStretch(1)
        nut_them_lop = QPushButton("+ Thêm Lớp Hành Chính")
        nut_them_lop.setObjectName("nutChinh")
        nut_them_lop.clicked.connect(self._xu_ly_them_lop)
        hang_lop.addWidget(nut_them_lop)
        bo_cuc_lop.addLayout(hang_lop)

        self._bang_lop = QTableWidget(0, 5)
        self._bang_lop.setHorizontalHeaderLabels(
            ["Mã lớp", "Tên lớp", "Khoa", "Khóa học", "Sĩ số"]
        )
        self._bang_lop.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._bang_lop.horizontalHeader().setStretchLastSection(False)
        self._bang_lop.horizontalHeader().setMinimumSectionSize(88)
        self._bang_lop.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        bo_cuc_lop.addWidget(self._bang_lop)
        tab.addTab(trang_lop, "Lớp Hành Chính")

        bo_cuc.addWidget(tab, stretch=1)

    def _nap_lai_tat_ca(self) -> None:
        self._danh_sach_khoa = danh_muc.lay_danh_sach_khoa()
        self._bang_khoa.setRowCount(len(self._danh_sach_khoa))
        for hang, khoa in enumerate(self._danh_sach_khoa):
            for cot, gia_tri in enumerate([khoa.ma_khoa, khoa.ten_khoa, khoa.mo_ta or "-"]):
                self._bang_khoa.setItem(hang, cot, QTableWidgetItem(gia_tri))

        danh_sach_lop = danh_muc.lay_danh_sach_lop_hoc()
        self._bang_lop.setRowCount(len(danh_sach_lop))
        for hang, lop in enumerate(danh_sach_lop):
            gia_tri_cac_cot = [
                lop.ma_lop, lop.ten_lop, lop.ten_khoa or "-", lop.khoa_hoc or "-", str(lop.si_so)
            ]
            for cot, gia_tri in enumerate(gia_tri_cac_cot):
                self._bang_lop.setItem(hang, cot, QTableWidgetItem(gia_tri))

    def _xu_ly_them_khoa(self) -> None:
        hop_thoai = HopThoaiKhoa(self)
        if hop_thoai.exec() != QDialog.DialogCode.Accepted:
            return
        du_lieu = hop_thoai.lay_du_lieu_nhap()
        if not du_lieu["ma_khoa"] or not du_lieu["ten_khoa"]:
            QMessageBox.warning(self, "Thiếu thông tin", "Mã khoa và tên khoa là bắt buộc.")
            return
        try:
            danh_muc.them_khoa(self.phien_dang_nhap.vai_tro, **du_lieu)
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể thêm khoa", str(loi))
            return
        self._nap_lai_tat_ca()

    def _xu_ly_them_lop(self) -> None:
        if not self._danh_sach_khoa:
            QMessageBox.information(
                self, "Chưa có khoa", "Vui lòng thêm ít nhất một Khoa trước khi tạo lớp."
            )
            return
        hop_thoai = HopThoaiLopHoc(self, self._danh_sach_khoa)
        if hop_thoai.exec() != QDialog.DialogCode.Accepted:
            return
        du_lieu = hop_thoai.lay_du_lieu_nhap()
        if not du_lieu["ma_lop"] or not du_lieu["ten_lop"]:
            QMessageBox.warning(self, "Thiếu thông tin", "Mã lớp và tên lớp là bắt buộc.")
            return
        try:
            danh_muc.them_lop_hoc(self.phien_dang_nhap.vai_tro, **du_lieu)
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể thêm lớp", str(loi))
            return
        self._nap_lai_tat_ca()
