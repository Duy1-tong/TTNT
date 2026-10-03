"""Man hinh Quan Ly Giang Vien: danh sach, tim kiem, them/sua/xoa giang vien."""

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
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.dich_vu import danh_muc, giang_vien as dv_giang_vien
from app.dich_vu.xac_thuc import PhienDangNhap


class HopThoaiGiangVien(QDialog):
    """Hop thoai them moi / chinh sua thong tin mot giang vien."""

    def __init__(
        self,
        parent: QWidget | None,
        danh_sach_khoa: list[danh_muc.ThongTinKhoa],
        thong_tin_hien_co: dv_giang_vien.ThongTinGiangVien | None = None,
    ) -> None:
        super().__init__(parent)
        self._thong_tin_hien_co = thong_tin_hien_co
        self._danh_sach_khoa = danh_sach_khoa
        self.setWindowTitle(
            "Chỉnh Sửa Giảng Viên" if thong_tin_hien_co else "Thêm Giảng Viên Mới"
        )
        self.setMinimumWidth(420)
        self._xay_dung_giao_dien()
        if thong_tin_hien_co:
            self._nap_du_lieu_hien_co(thong_tin_hien_co)

    def _xay_dung_giao_dien(self) -> None:
        bo_cuc = QFormLayout(self)

        self._o_ma_giang_vien = QLineEdit()
        self._o_ma_giang_vien.setEnabled(self._thong_tin_hien_co is None)
        bo_cuc.addRow("Mã giảng viên (*):", self._o_ma_giang_vien)

        self._o_ho_ten = QLineEdit()
        bo_cuc.addRow("Họ tên (*):", self._o_ho_ten)

        self._o_hoc_vi = QLineEdit()
        bo_cuc.addRow("Học vị:", self._o_hoc_vi)

        self._o_email = QLineEdit()
        bo_cuc.addRow("Email:", self._o_email)

        self._o_so_dien_thoai = QLineEdit()
        bo_cuc.addRow("Số điện thoại:", self._o_so_dien_thoai)

        self._o_khoa = QComboBox()
        self._o_khoa.addItem("(Chưa xếp khoa)", None)
        for khoa in self._danh_sach_khoa:
            self._o_khoa.addItem(f"{khoa.ma_khoa} - {khoa.ten_khoa}", khoa.id)
        bo_cuc.addRow("Khoa:", self._o_khoa)

        nut = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        nut.accepted.connect(self.accept)
        nut.rejected.connect(self.reject)
        bo_cuc.addRow(nut)

    def _nap_du_lieu_hien_co(self, thong_tin: dv_giang_vien.ThongTinGiangVien) -> None:
        self._o_ma_giang_vien.setText(thong_tin.ma_giang_vien)
        self._o_ho_ten.setText(thong_tin.ho_ten)
        self._o_hoc_vi.setText(thong_tin.hoc_vi or "")
        self._o_email.setText(thong_tin.email or "")
        self._o_so_dien_thoai.setText(thong_tin.so_dien_thoai or "")
        if thong_tin.khoa_id:
            chi_so = self._o_khoa.findData(thong_tin.khoa_id)
            if chi_so >= 0:
                self._o_khoa.setCurrentIndex(chi_so)

    def lay_du_lieu_nhap(self) -> dict:
        return {
            "ma_giang_vien": self._o_ma_giang_vien.text().strip(),
            "ho_ten": self._o_ho_ten.text().strip(),
            "hoc_vi": self._o_hoc_vi.text().strip() or None,
            "email": self._o_email.text().strip() or None,
            "so_dien_thoai": self._o_so_dien_thoai.text().strip() or None,
            "khoa_id": self._o_khoa.currentData(),
        }


class TrangQuanLyGiangVien(QWidget):
    """Trang quan ly danh sach giang vien."""

    def __init__(self, phien_dang_nhap: PhienDangNhap) -> None:
        super().__init__()
        self.phien_dang_nhap = phien_dang_nhap
        self._danh_sach_khoa: list[danh_muc.ThongTinKhoa] = []
        self._xay_dung_giao_dien()
        self._danh_sach_khoa = danh_muc.lay_danh_sach_khoa()
        self._nap_lai_danh_sach()

    def _xay_dung_giao_dien(self) -> None:
        bo_cuc = QVBoxLayout(self)
        bo_cuc.setContentsMargins(28, 24, 28, 24)
        bo_cuc.setSpacing(14)

        nhan_tieu_de = QLabel("Quản Lý Giảng Viên")
        nhan_tieu_de.setObjectName("nhanTieuDeTrang")
        bo_cuc.addWidget(nhan_tieu_de)

        hang_cong_cu = QHBoxLayout()
        self._o_tim_kiem = QLineEdit()
        self._o_tim_kiem.setPlaceholderText("Tìm theo mã hoặc họ tên giảng viên...")
        self._o_tim_kiem.textChanged.connect(lambda _: self._nap_lai_danh_sach())
        hang_cong_cu.addWidget(self._o_tim_kiem, stretch=1)

        nut_them = QPushButton("+ Thêm Giảng Viên")
        nut_them.setObjectName("nutChinh")
        nut_them.clicked.connect(self._xu_ly_them)
        hang_cong_cu.addWidget(nut_them)
        bo_cuc.addLayout(hang_cong_cu)

        self._bang = QTableWidget(0, 7)
        self._bang.setHorizontalHeaderLabels(
            ["Mã GV", "Họ tên", "Học vị", "Email", "SĐT", "Trạng thái", "Số lớp phụ trách"]
        )
        self._bang.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._bang.horizontalHeader().setStretchLastSection(False)
        self._bang.horizontalHeader().setMinimumSectionSize(88)
        self._bang.setColumnWidth(0, 90)
        self._bang.setColumnWidth(2, 95)
        self._bang.setColumnWidth(3, 150)
        self._bang.setColumnWidth(4, 110)
        self._bang.setColumnWidth(5, 100)
        self._bang.setColumnWidth(6, 150)
        self._bang.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._bang.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        bo_cuc.addWidget(self._bang, stretch=1)

        hang_nut = QHBoxLayout()
        nut_sua = QPushButton("Sửa")
        nut_sua.clicked.connect(self._xu_ly_sua)
        nut_xoa = QPushButton("Xóa")
        nut_xoa.setObjectName("nutNguyHiem")
        nut_xoa.clicked.connect(self._xu_ly_xoa)
        hang_nut.addWidget(nut_sua)
        hang_nut.addWidget(nut_xoa)
        hang_nut.addStretch(1)
        bo_cuc.addLayout(hang_nut)

    def _nap_lai_danh_sach(self) -> None:
        tu_khoa = self._o_tim_kiem.text().strip() or None
        danh_sach = dv_giang_vien.lay_danh_sach_giang_vien(tu_khoa_tim_kiem=tu_khoa)
        bang_trang_thai = {"DANG_CONG_TAC": "Đang công tác", "NGHI_VIEC": "Nghỉ việc"}
        self._bang.setRowCount(len(danh_sach))
        for hang, gv in enumerate(danh_sach):
            gia_tri_cac_cot = [
                gv.ma_giang_vien,
                gv.ho_ten,
                gv.hoc_vi or "-",
                gv.email or "-",
                gv.so_dien_thoai or "-",
                bang_trang_thai.get(gv.trang_thai, gv.trang_thai),
                str(gv.so_lop_mon_hoc_phu_trach),
            ]
            for cot, gia_tri in enumerate(gia_tri_cac_cot):
                muc = QTableWidgetItem(gia_tri)
                muc.setData(Qt.ItemDataRole.UserRole, gv.id)
                self._bang.setItem(hang, cot, muc)

    def _lay_id_dang_chon(self) -> int | None:
        hang = self._bang.currentRow()
        if hang < 0:
            return None
        muc = self._bang.item(hang, 0)
        return muc.data(Qt.ItemDataRole.UserRole) if muc else None

    def _xu_ly_them(self) -> None:
        hop_thoai = HopThoaiGiangVien(self, self._danh_sach_khoa)
        if hop_thoai.exec() != QDialog.DialogCode.Accepted:
            return
        du_lieu = hop_thoai.lay_du_lieu_nhap()
        if not du_lieu["ma_giang_vien"] or not du_lieu["ho_ten"]:
            QMessageBox.warning(self, "Thiếu thông tin", "Mã giảng viên và họ tên là bắt buộc.")
            return
        try:
            dv_giang_vien.them_giang_vien(
                self.phien_dang_nhap.vai_tro,
                nguoi_thuc_hien_id=self.phien_dang_nhap.nguoi_dung_id,
                **du_lieu,
            )
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể thêm giảng viên", str(loi))
            return
        self._nap_lai_danh_sach()

    def _xu_ly_sua(self) -> None:
        giang_vien_id = self._lay_id_dang_chon()
        if giang_vien_id is None:
            QMessageBox.information(self, "Chưa chọn", "Vui lòng chọn một giảng viên để sửa.")
            return
        danh_sach_hien_tai = dv_giang_vien.lay_danh_sach_giang_vien()
        thong_tin = next((gv for gv in danh_sach_hien_tai if gv.id == giang_vien_id), None)
        if thong_tin is None:
            return
        hop_thoai = HopThoaiGiangVien(self, self._danh_sach_khoa, thong_tin_hien_co=thong_tin)
        if hop_thoai.exec() != QDialog.DialogCode.Accepted:
            return
        du_lieu = hop_thoai.lay_du_lieu_nhap()
        du_lieu.pop("ma_giang_vien", None)
        try:
            dv_giang_vien.cap_nhat_giang_vien(
                self.phien_dang_nhap.vai_tro,
                giang_vien_id=giang_vien_id,
                nguoi_thuc_hien_id=self.phien_dang_nhap.nguoi_dung_id,
                **du_lieu,
            )
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể cập nhật", str(loi))
            return
        self._nap_lai_danh_sach()

    def _xu_ly_xoa(self) -> None:
        giang_vien_id = self._lay_id_dang_chon()
        if giang_vien_id is None:
            QMessageBox.information(self, "Chưa chọn", "Vui lòng chọn một giảng viên để xóa.")
            return
        xac_nhan = QMessageBox.question(
            self, "Xác nhận xóa", "Bạn có chắc muốn xóa giảng viên này?"
        )
        if xac_nhan != QMessageBox.StandardButton.Yes:
            return
        try:
            dv_giang_vien.xoa_giang_vien(
                self.phien_dang_nhap.vai_tro,
                giang_vien_id,
                nguoi_thuc_hien_id=self.phien_dang_nhap.nguoi_dung_id,
            )
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể xóa", str(loi))
            return
        self._nap_lai_danh_sach()
