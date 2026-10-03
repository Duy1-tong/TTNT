"""Man hinh Quan Ly Mon - Lop Hoc Phan: quan ly Mon hoc, Lop hoc phan va dang ky."""

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
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.dich_vu import danh_muc, giang_vien as dv_giang_vien, sinh_vien as dv_sinh_vien
from app.dich_vu.xac_thuc import PhienDangNhap


class HopThoaiMonHoc(QDialog):
    """Hop thoai them moi mot Mon hoc."""

    def __init__(self, parent: QWidget | None, danh_sach_khoa: list[danh_muc.ThongTinKhoa]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Thêm Môn Học Mới")
        self.setMinimumWidth(380)
        bo_cuc = QFormLayout(self)
        self._o_ma_mon = QLineEdit()
        self._o_ten_mon = QLineEdit()
        self._o_so_tin_chi = QSpinBox()
        self._o_so_tin_chi.setRange(1, 10)
        self._o_so_tin_chi.setValue(3)
        self._o_khoa = QComboBox()
        self._o_khoa.addItem("(Không thuộc khoa nào)", None)
        for khoa in danh_sach_khoa:
            self._o_khoa.addItem(f"{khoa.ma_khoa} - {khoa.ten_khoa}", khoa.id)
        bo_cuc.addRow("Mã môn (*):", self._o_ma_mon)
        bo_cuc.addRow("Tên môn (*):", self._o_ten_mon)
        bo_cuc.addRow("Số tín chỉ:", self._o_so_tin_chi)
        bo_cuc.addRow("Khoa:", self._o_khoa)
        nut = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        nut.accepted.connect(self.accept)
        nut.rejected.connect(self.reject)
        bo_cuc.addRow(nut)

    def lay_du_lieu_nhap(self) -> dict:
        return {
            "ma_mon": self._o_ma_mon.text().strip(),
            "ten_mon": self._o_ten_mon.text().strip(),
            "so_tin_chi": self._o_so_tin_chi.value(),
            "khoa_id": self._o_khoa.currentData(),
        }


class HopThoaiLopMonHoc(QDialog):
    """Hop thoai mo mot Lop hoc phan moi."""

    def __init__(
        self,
        parent: QWidget | None,
        danh_sach_mon: list[danh_muc.ThongTinMonHoc],
        danh_sach_giang_vien: list[dv_giang_vien.ThongTinGiangVien],
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Mở Lớp Học Phần Mới")
        self.setMinimumWidth(400)
        bo_cuc = QFormLayout(self)
        self._o_ma_lop_mon = QLineEdit()
        self._o_ma_lop_mon.setPlaceholderText("Ví dụ: IT101_HK2_2024")
        self._o_mon = QComboBox()
        for mon in danh_sach_mon:
            self._o_mon.addItem(f"{mon.ma_mon} - {mon.ten_mon}", mon.id)
        self._o_giang_vien = QComboBox()
        self._o_giang_vien.addItem("(Chưa phân công)", None)
        for gv in danh_sach_giang_vien:
            self._o_giang_vien.addItem(f"{gv.ma_giang_vien} - {gv.ho_ten}", gv.id)
        self._o_hoc_ky = QLineEdit()
        self._o_hoc_ky.setPlaceholderText("Ví dụ: HK1")
        self._o_nam_hoc = QLineEdit()
        self._o_nam_hoc.setPlaceholderText("Ví dụ: 2024-2025")
        bo_cuc.addRow("Mã lớp học phần (*):", self._o_ma_lop_mon)
        bo_cuc.addRow("Môn học (*):", self._o_mon)
        bo_cuc.addRow("Giảng viên phụ trách:", self._o_giang_vien)
        bo_cuc.addRow("Học kỳ (*):", self._o_hoc_ky)
        bo_cuc.addRow("Năm học (*):", self._o_nam_hoc)
        nut = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        nut.accepted.connect(self.accept)
        nut.rejected.connect(self.reject)
        bo_cuc.addRow(nut)

    def lay_du_lieu_nhap(self) -> dict:
        return {
            "ma_lop_mon": self._o_ma_lop_mon.text().strip(),
            "mon_hoc_id": self._o_mon.currentData(),
            "giang_vien_id": self._o_giang_vien.currentData(),
            "hoc_ky": self._o_hoc_ky.text().strip(),
            "nam_hoc": self._o_nam_hoc.text().strip(),
        }


class HopThoaiDangKySinhVien(QDialog):
    """Hop thoai chon mot sinh vien de dang ky vao lop hoc phan dang chon."""

    def __init__(self, parent: QWidget | None, danh_sach_sinh_vien: list) -> None:
        super().__init__(parent)
        self.setWindowTitle("Đăng Ký Sinh Viên Vào Lớp Học Phần")
        self.setMinimumWidth(380)
        bo_cuc = QFormLayout(self)
        self._o_sinh_vien = QComboBox()
        for sv in danh_sach_sinh_vien:
            self._o_sinh_vien.addItem(f"{sv.ma_sinh_vien} - {sv.ho_ten}", sv.id)
        bo_cuc.addRow("Chọn sinh viên:", self._o_sinh_vien)
        nut = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        nut.accepted.connect(self.accept)
        nut.rejected.connect(self.reject)
        bo_cuc.addRow(nut)

    def sinh_vien_id_da_chon(self) -> int | None:
        return self._o_sinh_vien.currentData()


class TrangQuanLyMon(QWidget):
    """Trang quan ly Mon hoc va Lop hoc phan."""

    def __init__(self, phien_dang_nhap: PhienDangNhap) -> None:
        super().__init__()
        self.phien_dang_nhap = phien_dang_nhap
        self._xay_dung_giao_dien()
        self._nap_lai_tat_ca()

    def _xay_dung_giao_dien(self) -> None:
        bo_cuc = QVBoxLayout(self)
        bo_cuc.setContentsMargins(28, 24, 28, 24)
        bo_cuc.setSpacing(14)

        nhan_tieu_de = QLabel("Quản Lý Môn Học - Lớp Học Phần")
        nhan_tieu_de.setObjectName("nhanTieuDeTrang")
        bo_cuc.addWidget(nhan_tieu_de)

        tab = QTabWidget()

        # ----- Tab Mon hoc -----
        trang_mon = QWidget()
        bo_cuc_mon = QVBoxLayout(trang_mon)
        hang_mon = QHBoxLayout()
        hang_mon.addStretch(1)
        nut_them_mon = QPushButton("+ Thêm Môn Học")
        nut_them_mon.setObjectName("nutChinh")
        nut_them_mon.clicked.connect(self._xu_ly_them_mon)
        hang_mon.addWidget(nut_them_mon)
        bo_cuc_mon.addLayout(hang_mon)

        self._bang_mon = QTableWidget(0, 3)
        self._bang_mon.setHorizontalHeaderLabels(["Mã môn", "Tên môn", "Số tín chỉ"])
        self._bang_mon.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._bang_mon.horizontalHeader().setStretchLastSection(False)
        self._bang_mon.horizontalHeader().setMinimumSectionSize(88)
        self._bang_mon.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        bo_cuc_mon.addWidget(self._bang_mon)
        tab.addTab(trang_mon, "Môn Học")

        # ----- Tab Lop hoc phan -----
        trang_lop_mon = QWidget()
        bo_cuc_lop_mon = QVBoxLayout(trang_lop_mon)
        hang_lop_mon = QHBoxLayout()
        hang_lop_mon.addStretch(1)
        nut_them_lop_mon = QPushButton("+ Mở Lớp Học Phần")
        nut_them_lop_mon.setObjectName("nutChinh")
        nut_them_lop_mon.clicked.connect(self._xu_ly_them_lop_mon)
        hang_lop_mon.addWidget(nut_them_lop_mon)
        bo_cuc_lop_mon.addLayout(hang_lop_mon)

        self._bang_lop_mon = QTableWidget(0, 6)
        self._bang_lop_mon.setHorizontalHeaderLabels(
            ["Mã lớp học phần", "Môn học", "Giảng viên", "Học kỳ", "Năm học", "Sĩ số"]
        )
        self._bang_lop_mon.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self._bang_lop_mon.horizontalHeader().setStretchLastSection(False)
        self._bang_lop_mon.horizontalHeader().setMinimumSectionSize(88)
        self._bang_lop_mon.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._bang_lop_mon.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        bo_cuc_lop_mon.addWidget(self._bang_lop_mon, stretch=1)

        hang_nut_dang_ky = QHBoxLayout()
        nut_dang_ky_sv = QPushButton("Đăng Ký Sinh Viên Vào Lớp Đang Chọn")
        nut_dang_ky_sv.clicked.connect(self._xu_ly_dang_ky_sinh_vien)
        hang_nut_dang_ky.addWidget(nut_dang_ky_sv)
        hang_nut_dang_ky.addStretch(1)
        bo_cuc_lop_mon.addLayout(hang_nut_dang_ky)

        tab.addTab(trang_lop_mon, "Lớp Học Phần")
        bo_cuc.addWidget(tab, stretch=1)

    def _nap_lai_tat_ca(self) -> None:
        self._danh_sach_khoa = danh_muc.lay_danh_sach_khoa()
        self._danh_sach_mon = danh_muc.lay_danh_sach_mon_hoc()
        self._danh_sach_giang_vien = dv_giang_vien.lay_danh_sach_giang_vien()

        self._bang_mon.setRowCount(len(self._danh_sach_mon))
        for hang, mon in enumerate(self._danh_sach_mon):
            for cot, gia_tri in enumerate([mon.ma_mon, mon.ten_mon, str(mon.so_tin_chi)]):
                self._bang_mon.setItem(hang, cot, QTableWidgetItem(gia_tri))

        self._danh_sach_lop_mon = danh_muc.lay_danh_sach_lop_mon_hoc()
        self._bang_lop_mon.setRowCount(len(self._danh_sach_lop_mon))
        for hang, lop_mon in enumerate(self._danh_sach_lop_mon):
            gia_tri_cac_cot = [
                lop_mon.ma_lop_mon,
                lop_mon.ten_mon or "-",
                lop_mon.ten_giang_vien or "(Chưa phân công)",
                lop_mon.hoc_ky,
                lop_mon.nam_hoc,
                str(lop_mon.si_so_dang_ky),
            ]
            for cot, gia_tri in enumerate(gia_tri_cac_cot):
                muc = QTableWidgetItem(gia_tri)
                muc.setData(Qt.ItemDataRole.UserRole, lop_mon.id)
                self._bang_lop_mon.setItem(hang, cot, muc)

    def _xu_ly_them_mon(self) -> None:
        hop_thoai = HopThoaiMonHoc(self, self._danh_sach_khoa)
        if hop_thoai.exec() != QDialog.DialogCode.Accepted:
            return
        du_lieu = hop_thoai.lay_du_lieu_nhap()
        if not du_lieu["ma_mon"] or not du_lieu["ten_mon"]:
            QMessageBox.warning(self, "Thiếu thông tin", "Mã môn và tên môn là bắt buộc.")
            return
        try:
            danh_muc.them_mon_hoc(self.phien_dang_nhap.vai_tro, **du_lieu)
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể thêm môn học", str(loi))
            return
        self._nap_lai_tat_ca()

    def _xu_ly_them_lop_mon(self) -> None:
        if not self._danh_sach_mon:
            QMessageBox.information(
                self, "Chưa có môn học", "Vui lòng thêm ít nhất một Môn học trước."
            )
            return
        hop_thoai = HopThoaiLopMonHoc(self, self._danh_sach_mon, self._danh_sach_giang_vien)
        if hop_thoai.exec() != QDialog.DialogCode.Accepted:
            return
        du_lieu = hop_thoai.lay_du_lieu_nhap()
        if not du_lieu["ma_lop_mon"] or not du_lieu["hoc_ky"] or not du_lieu["nam_hoc"]:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng điền đầy đủ các trường (*).")
            return
        try:
            danh_muc.them_lop_mon_hoc(self.phien_dang_nhap.vai_tro, **du_lieu)
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể mở lớp học phần", str(loi))
            return
        self._nap_lai_tat_ca()

    def _xu_ly_dang_ky_sinh_vien(self) -> None:
        hang = self._bang_lop_mon.currentRow()
        if hang < 0:
            QMessageBox.information(
                self, "Chưa chọn", "Vui lòng chọn một lớp học phần trong bảng."
            )
            return
        lop_mon_hoc_id = self._bang_lop_mon.item(hang, 0).data(Qt.ItemDataRole.UserRole)

        danh_sach_sinh_vien = dv_sinh_vien.lay_danh_sach_sinh_vien()
        if not danh_sach_sinh_vien:
            QMessageBox.information(self, "Chưa có sinh viên", "Hệ thống chưa có sinh viên nào.")
            return
        hop_thoai = HopThoaiDangKySinhVien(self, danh_sach_sinh_vien)
        if hop_thoai.exec() != QDialog.DialogCode.Accepted:
            return
        sinh_vien_id = hop_thoai.sinh_vien_id_da_chon()
        try:
            danh_muc.dang_ky_sinh_vien_vao_lop_mon_hoc(
                self.phien_dang_nhap.vai_tro, sinh_vien_id, lop_mon_hoc_id
            )
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể đăng ký", str(loi))
            return
        QMessageBox.information(self, "Thành công", "Đã đăng ký sinh viên vào lớp học phần.")
        self._nap_lai_tat_ca()
