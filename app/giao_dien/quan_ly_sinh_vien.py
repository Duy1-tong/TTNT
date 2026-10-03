"""Man hinh Quan Ly Sinh Vien: danh sach, tim kiem, them/sua/doi trang thai/xoa."""

from __future__ import annotations

import datetime as _datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
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

from app.dich_vu import danh_muc, sinh_vien as dv_sinh_vien
from app.dich_vu.xac_thuc import PhienDangNhap
from app.mo_hinh.sinh_vien import GioiTinh, TrangThaiSinhVien


class HopThoaiSinhVien(QDialog):
    """Hop thoai them moi / chinh sua thong tin mot sinh vien."""

    def __init__(
        self,
        parent: QWidget | None,
        danh_sach_lop: list[danh_muc.ThongTinLopHoc],
        thong_tin_hien_co: dv_sinh_vien.ThongTinSinhVien | None = None,
    ) -> None:
        super().__init__(parent)
        self._thong_tin_hien_co = thong_tin_hien_co
        self._danh_sach_lop = danh_sach_lop
        self.setWindowTitle(
            "Chỉnh Sửa Sinh Viên" if thong_tin_hien_co else "Thêm Sinh Viên Mới"
        )
        self.setMinimumWidth(420)
        self._xay_dung_giao_dien()
        if thong_tin_hien_co:
            self._nap_du_lieu_hien_co(thong_tin_hien_co)

    def _xay_dung_giao_dien(self) -> None:
        bo_cuc = QFormLayout(self)

        self._o_ma_sinh_vien = QLineEdit()
        self._o_ma_sinh_vien.setEnabled(self._thong_tin_hien_co is None)
        bo_cuc.addRow("Mã sinh viên (*):", self._o_ma_sinh_vien)

        self._o_ho_ten = QLineEdit()
        bo_cuc.addRow("Họ tên (*):", self._o_ho_ten)

        self._o_ngay_sinh = QDateEdit()
        self._o_ngay_sinh.setCalendarPopup(True)
        self._o_ngay_sinh.setDate(_datetime.date(2003, 1, 1))
        bo_cuc.addRow("Ngày sinh:", self._o_ngay_sinh)

        self._o_gioi_tinh = QComboBox()
        self._o_gioi_tinh.addItems(["Nam", "Nữ", "Khác"])
        bo_cuc.addRow("Giới tính:", self._o_gioi_tinh)

        self._o_email = QLineEdit()
        bo_cuc.addRow("Email:", self._o_email)

        self._o_so_dien_thoai = QLineEdit()
        bo_cuc.addRow("Số điện thoại:", self._o_so_dien_thoai)

        self._o_dia_chi = QLineEdit()
        bo_cuc.addRow("Địa chỉ:", self._o_dia_chi)

        self._o_lop = QComboBox()
        self._o_lop.addItem("(Chưa xếp lớp)", None)
        for lop in self._danh_sach_lop:
            self._o_lop.addItem(f"{lop.ma_lop} - {lop.ten_lop}", (lop.id, lop.khoa_id))
        bo_cuc.addRow("Lớp hành chính:", self._o_lop)

        nut = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        nut.accepted.connect(self.accept)
        nut.rejected.connect(self.reject)
        bo_cuc.addRow(nut)

    def _nap_du_lieu_hien_co(self, thong_tin: dv_sinh_vien.ThongTinSinhVien) -> None:
        self._o_ma_sinh_vien.setText(thong_tin.ma_sinh_vien)
        self._o_ho_ten.setText(thong_tin.ho_ten)
        if thong_tin.ngay_sinh:
            self._o_ngay_sinh.setDate(thong_tin.ngay_sinh)
        if thong_tin.gioi_tinh:
            bang_gioi_tinh = {"NAM": 0, "NU": 1, "KHAC": 2}
            self._o_gioi_tinh.setCurrentIndex(bang_gioi_tinh.get(thong_tin.gioi_tinh, 2))
        self._o_email.setText(thong_tin.email or "")
        self._o_so_dien_thoai.setText(thong_tin.so_dien_thoai or "")
        self._o_dia_chi.setText(thong_tin.dia_chi or "")
        if thong_tin.lop_id:
            for chi_so in range(self._o_lop.count()):
                du_lieu = self._o_lop.itemData(chi_so)
                if du_lieu and du_lieu[0] == thong_tin.lop_id:
                    self._o_lop.setCurrentIndex(chi_so)
                    break

    def lay_du_lieu_nhap(self) -> dict:
        du_lieu_lop = self._o_lop.currentData()
        bang_gioi_tinh = [GioiTinh.NAM, GioiTinh.NU, GioiTinh.KHAC]
        return {
            "ma_sinh_vien": self._o_ma_sinh_vien.text().strip(),
            "ho_ten": self._o_ho_ten.text().strip(),
            "ngay_sinh": self._o_ngay_sinh.date().toPython(),
            "gioi_tinh": bang_gioi_tinh[self._o_gioi_tinh.currentIndex()],
            "email": self._o_email.text().strip() or None,
            "so_dien_thoai": self._o_so_dien_thoai.text().strip() or None,
            "dia_chi": self._o_dia_chi.text().strip() or None,
            "lop_id": du_lieu_lop[0] if du_lieu_lop else None,
            "khoa_id": du_lieu_lop[1] if du_lieu_lop else None,
        }


class TrangQuanLySinhVien(QWidget):
    """Trang quan ly danh sach sinh vien."""

    def __init__(self, phien_dang_nhap: PhienDangNhap) -> None:
        super().__init__()
        self.phien_dang_nhap = phien_dang_nhap
        self._danh_sach_lop: list[danh_muc.ThongTinLopHoc] = []
        self._xay_dung_giao_dien()
        self._nap_danh_sach_lop()
        self._nap_lai_danh_sach()

    def _xay_dung_giao_dien(self) -> None:
        bo_cuc = QVBoxLayout(self)
        bo_cuc.setContentsMargins(28, 24, 28, 24)
        bo_cuc.setSpacing(14)

        nhan_tieu_de = QLabel("Quản Lý Sinh Viên")
        nhan_tieu_de.setObjectName("nhanTieuDeTrang")
        bo_cuc.addWidget(nhan_tieu_de)

        hang_cong_cu = QHBoxLayout()
        self._o_tim_kiem = QLineEdit()
        self._o_tim_kiem.setPlaceholderText("Tìm theo mã hoặc họ tên sinh viên...")
        self._o_tim_kiem.textChanged.connect(lambda _: self._nap_lai_danh_sach())
        hang_cong_cu.addWidget(self._o_tim_kiem, stretch=2)

        self._o_loc_lop = QComboBox()
        self._o_loc_lop.currentIndexChanged.connect(lambda _: self._nap_lai_danh_sach())
        hang_cong_cu.addWidget(self._o_loc_lop, stretch=1)

        nut_them = QPushButton("+ Thêm Sinh Viên")
        nut_them.setObjectName("nutChinh")
        nut_them.clicked.connect(self._xu_ly_them_sinh_vien)
        hang_cong_cu.addWidget(nut_them)
        bo_cuc.addLayout(hang_cong_cu)

        self._bang = QTableWidget(0, 8)
        self._bang.setHorizontalHeaderLabels(
            ["Mã SV", "Họ tên", "Lớp", "Giới tính", "Email", "SĐT", "Trạng thái", "Số khuôn mặt"]
        )
        self._bang.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._bang.horizontalHeader().setStretchLastSection(False)
        self._bang.horizontalHeader().setMinimumSectionSize(88)
        self._bang.setColumnWidth(0, 90)
        self._bang.setColumnWidth(2, 100)
        self._bang.setColumnWidth(3, 100)
        self._bang.setColumnWidth(4, 150)
        self._bang.setColumnWidth(5, 110)
        self._bang.setColumnWidth(6, 110)
        self._bang.setColumnWidth(7, 135)
        self._bang.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._bang.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        bo_cuc.addWidget(self._bang, stretch=1)

        hang_nut_thao_tac = QHBoxLayout()
        nut_sua = QPushButton("Sửa")
        nut_sua.clicked.connect(self._xu_ly_sua_sinh_vien)
        nut_doi_trang_thai = QPushButton("Đổi Trạng Thái")
        nut_doi_trang_thai.clicked.connect(self._xu_ly_doi_trang_thai)
        nut_xoa = QPushButton("Xóa")
        nut_xoa.setObjectName("nutNguyHiem")
        nut_xoa.clicked.connect(self._xu_ly_xoa_sinh_vien)
        hang_nut_thao_tac.addWidget(nut_sua)
        hang_nut_thao_tac.addWidget(nut_doi_trang_thai)
        hang_nut_thao_tac.addWidget(nut_xoa)
        hang_nut_thao_tac.addStretch(1)
        bo_cuc.addLayout(hang_nut_thao_tac)

    def _nap_danh_sach_lop(self) -> None:
        self._danh_sach_lop = danh_muc.lay_danh_sach_lop_hoc()
        self._o_loc_lop.blockSignals(True)
        self._o_loc_lop.clear()
        self._o_loc_lop.addItem("Tất cả các lớp", None)
        for lop in self._danh_sach_lop:
            self._o_loc_lop.addItem(f"{lop.ma_lop} - {lop.ten_lop}", lop.id)
        self._o_loc_lop.blockSignals(False)

    def _nap_lai_danh_sach(self) -> None:
        tu_khoa = self._o_tim_kiem.text().strip() or None
        lop_id = self._o_loc_lop.currentData()
        danh_sach = dv_sinh_vien.lay_danh_sach_sinh_vien(
            tu_khoa_tim_kiem=tu_khoa, lop_id=lop_id
        )
        self._bang.setRowCount(len(danh_sach))
        for hang, sv in enumerate(danh_sach):
            bang_gioi_tinh_hien_thi = {"NAM": "Nam", "NU": "Nữ", "KHAC": "Khác", None: "-"}
            gia_tri_cac_cot = [
                sv.ma_sinh_vien,
                sv.ho_ten,
                sv.ten_lop or "-",
                bang_gioi_tinh_hien_thi.get(sv.gioi_tinh, "-"),
                sv.email or "-",
                sv.so_dien_thoai or "-",
                _ten_hien_thi_trang_thai(sv.trang_thai),
                str(sv.so_khuon_mat_da_dang_ky),
            ]
            for cot, gia_tri in enumerate(gia_tri_cac_cot):
                muc = QTableWidgetItem(gia_tri)
                muc.setData(Qt.ItemDataRole.UserRole, sv.id)
                self._bang.setItem(hang, cot, muc)

    def _lay_id_sinh_vien_dang_chon(self) -> int | None:
        hang = self._bang.currentRow()
        if hang < 0:
            return None
        muc = self._bang.item(hang, 0)
        return muc.data(Qt.ItemDataRole.UserRole) if muc else None

    def _xu_ly_them_sinh_vien(self) -> None:
        hop_thoai = HopThoaiSinhVien(self, self._danh_sach_lop)
        if hop_thoai.exec() != QDialog.DialogCode.Accepted:
            return
        du_lieu = hop_thoai.lay_du_lieu_nhap()
        if not du_lieu["ma_sinh_vien"] or not du_lieu["ho_ten"]:
            QMessageBox.warning(self, "Thiếu thông tin", "Mã sinh viên và họ tên là bắt buộc.")
            return
        try:
            dv_sinh_vien.them_sinh_vien(
                self.phien_dang_nhap.vai_tro,
                nguoi_thuc_hien_id=self.phien_dang_nhap.nguoi_dung_id,
                **du_lieu,
            )
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể thêm sinh viên", str(loi))
            return
        self._nap_lai_danh_sach()

    def _xu_ly_sua_sinh_vien(self) -> None:
        sinh_vien_id = self._lay_id_sinh_vien_dang_chon()
        if sinh_vien_id is None:
            QMessageBox.information(self, "Chưa chọn", "Vui lòng chọn một sinh viên để sửa.")
            return
        thong_tin = dv_sinh_vien.lay_sinh_vien_theo_id(sinh_vien_id)
        if thong_tin is None:
            return
        hop_thoai = HopThoaiSinhVien(self, self._danh_sach_lop, thong_tin_hien_co=thong_tin)
        if hop_thoai.exec() != QDialog.DialogCode.Accepted:
            return
        du_lieu = hop_thoai.lay_du_lieu_nhap()
        du_lieu.pop("ma_sinh_vien", None)
        try:
            dv_sinh_vien.cap_nhat_sinh_vien(
                self.phien_dang_nhap.vai_tro,
                sinh_vien_id=sinh_vien_id,
                nguoi_thuc_hien_id=self.phien_dang_nhap.nguoi_dung_id,
                **du_lieu,
            )
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể cập nhật", str(loi))
            return
        self._nap_lai_danh_sach()

    def _xu_ly_doi_trang_thai(self) -> None:
        sinh_vien_id = self._lay_id_sinh_vien_dang_chon()
        if sinh_vien_id is None:
            QMessageBox.information(self, "Chưa chọn", "Vui lòng chọn một sinh viên.")
            return
        cac_trang_thai = list(TrangThaiSinhVien)
        ten_hien_thi = [_ten_hien_thi_trang_thai(t.value) for t in cac_trang_thai]
        from PySide6.QtWidgets import QInputDialog

        lua_chon, ok = QInputDialog.getItem(
            self, "Đổi Trạng Thái Sinh Viên", "Chọn trạng thái mới:", ten_hien_thi, 0, False
        )
        if not ok:
            return
        trang_thai_moi = cac_trang_thai[ten_hien_thi.index(lua_chon)]
        try:
            dv_sinh_vien.doi_trang_thai_sinh_vien(
                self.phien_dang_nhap.vai_tro,
                sinh_vien_id,
                trang_thai_moi,
                nguoi_thuc_hien_id=self.phien_dang_nhap.nguoi_dung_id,
            )
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể đổi trạng thái", str(loi))
            return
        self._nap_lai_danh_sach()

    def _xu_ly_xoa_sinh_vien(self) -> None:
        sinh_vien_id = self._lay_id_sinh_vien_dang_chon()
        if sinh_vien_id is None:
            QMessageBox.information(self, "Chưa chọn", "Vui lòng chọn một sinh viên để xóa.")
            return
        xac_nhan = QMessageBox.question(
            self,
            "Xác nhận xóa",
            "Sinh viên đã có lịch sử điểm danh sẽ KHÔNG thể xóa (chỉ đổi được trạng thái).\n"
            "Bạn có chắc muốn xóa sinh viên này?",
        )
        if xac_nhan != QMessageBox.StandardButton.Yes:
            return
        try:
            dv_sinh_vien.xoa_sinh_vien(
                self.phien_dang_nhap.vai_tro,
                sinh_vien_id,
                nguoi_thuc_hien_id=self.phien_dang_nhap.nguoi_dung_id,
            )
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể xóa", str(loi))
            return
        self._nap_lai_danh_sach()


def _ten_hien_thi_trang_thai(trang_thai: str) -> str:
    bang = {
        "DANG_HOC": "Đang học",
        "NGHI_HOC": "Nghỉ học",
        "BAO_LUU": "Bảo lưu",
        "TOT_NGHIEP": "Tốt nghiệp",
    }
    return bang.get(trang_thai, trang_thai)
