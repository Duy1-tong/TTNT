"""Man hinh Cai Dat: doi mat khau (moi vai tro), cau hinh he thong va quan ly tai khoan (ADMIN)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.dich_vu import cau_hinh_he_thong as dv_cau_hinh
from app.dich_vu import tai_khoan as dv_tai_khoan
from app.dich_vu.phan_quyen import QuyenHeThong, co_quyen
from app.dich_vu.xac_thuc import LoiXacThuc, PhienDangNhap, doi_mat_khau
from app.mo_hinh.nguoi_dung import VaiTro


class HopThoaiTaoTaiKhoan(QDialog):
    """Hop thoai tao mot tai khoan dang nhap moi (chi ADMIN)."""

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Tạo Tài Khoản Mới")
        self.setMinimumWidth(380)
        bo_cuc = QFormLayout(self)

        self._o_ten_dang_nhap = QLineEdit()
        self._o_mat_khau = QLineEdit()
        self._o_mat_khau.setEchoMode(QLineEdit.EchoMode.Password)
        self._o_ho_ten = QLineEdit()
        self._o_email = QLineEdit()
        self._o_vai_tro = QComboBox()
        self._o_vai_tro.addItem("Quản trị viên", VaiTro.ADMIN)
        self._o_vai_tro.addItem("Giảng viên", VaiTro.GIANG_VIEN)
        self._o_vai_tro.addItem("Sinh viên", VaiTro.SINH_VIEN)

        bo_cuc.addRow("Tên đăng nhập (*):", self._o_ten_dang_nhap)
        bo_cuc.addRow("Mật khẩu ban đầu (*):", self._o_mat_khau)
        bo_cuc.addRow("Họ tên (*):", self._o_ho_ten)
        bo_cuc.addRow("Email:", self._o_email)
        bo_cuc.addRow("Vai trò:", self._o_vai_tro)

        nut = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        nut.accepted.connect(self.accept)
        nut.rejected.connect(self.reject)
        bo_cuc.addRow(nut)

    def lay_du_lieu_nhap(self) -> dict:
        return {
            "ten_dang_nhap": self._o_ten_dang_nhap.text().strip(),
            "mat_khau_ban_dau": self._o_mat_khau.text(),
            "ho_ten": self._o_ho_ten.text().strip(),
            "email": self._o_email.text().strip() or None,
            "vai_tro_moi": self._o_vai_tro.currentData(),
        }


class TrangCaiDat(QWidget):
    """Trang cai dat he thong."""

    def __init__(self, phien_dang_nhap: PhienDangNhap) -> None:
        super().__init__()
        self.phien_dang_nhap = phien_dang_nhap
        self._xay_dung_giao_dien()

    def _xay_dung_giao_dien(self) -> None:
        bo_cuc_ngoai = QVBoxLayout(self)
        bo_cuc_ngoai.setContentsMargins(28, 24, 28, 24)
        bo_cuc_ngoai.setSpacing(14)

        nhan_tieu_de = QLabel("Cài Đặt")
        nhan_tieu_de.setObjectName("nhanTieuDeTrang")
        bo_cuc_ngoai.addWidget(nhan_tieu_de)

        tab = QTabWidget()
        tab.addTab(self._tao_tab_doi_mat_khau(), "Đổi Mật Khẩu")

        if co_quyen(self.phien_dang_nhap.vai_tro, QuyenHeThong.THAY_DOI_CAU_HINH_HE_THONG):
            tab.addTab(self._tao_tab_cau_hinh_he_thong(), "Cấu Hình Hệ Thống")

        if co_quyen(self.phien_dang_nhap.vai_tro, QuyenHeThong.QUAN_LY_TAI_KHOAN):
            tab.addTab(self._tao_tab_quan_ly_tai_khoan(), "Quản Lý Tài Khoản")

        bo_cuc_ngoai.addWidget(tab, stretch=1)

    # ------------------------------------------------------------------
    # DOI MAT KHAU
    # ------------------------------------------------------------------
    def _tao_tab_doi_mat_khau(self) -> QWidget:
        trang = QWidget()
        bo_cuc = QVBoxLayout(trang)
        bo_cuc.setAlignment(Qt.AlignmentFlag.AlignTop)

        khung = QFrame()
        khung.setMaximumWidth(420)
        bo_cuc_form = QFormLayout(khung)

        self._o_mat_khau_cu = QLineEdit()
        self._o_mat_khau_cu.setEchoMode(QLineEdit.EchoMode.Password)
        self._o_mat_khau_moi = QLineEdit()
        self._o_mat_khau_moi.setEchoMode(QLineEdit.EchoMode.Password)
        self._o_xac_nhan_mat_khau_moi = QLineEdit()
        self._o_xac_nhan_mat_khau_moi.setEchoMode(QLineEdit.EchoMode.Password)

        bo_cuc_form.addRow("Mật khẩu hiện tại:", self._o_mat_khau_cu)
        bo_cuc_form.addRow("Mật khẩu mới:", self._o_mat_khau_moi)
        bo_cuc_form.addRow("Xác nhận mật khẩu mới:", self._o_xac_nhan_mat_khau_moi)

        nut_doi = QPushButton("Đổi Mật Khẩu")
        nut_doi.setObjectName("nutChinh")
        nut_doi.clicked.connect(self._xu_ly_doi_mat_khau)
        bo_cuc_form.addRow(nut_doi)

        bo_cuc.addWidget(khung)
        return trang

    def _xu_ly_doi_mat_khau(self) -> None:
        mat_khau_moi = self._o_mat_khau_moi.text()
        if mat_khau_moi != self._o_xac_nhan_mat_khau_moi.text():
            QMessageBox.warning(self, "Không khớp", "Mật khẩu mới và xác nhận không khớp nhau.")
            return
        try:
            doi_mat_khau(
                self.phien_dang_nhap.nguoi_dung_id, self._o_mat_khau_cu.text(), mat_khau_moi
            )
        except LoiXacThuc as loi:
            QMessageBox.warning(self, "Không thể đổi mật khẩu", str(loi))
            return
        QMessageBox.information(self, "Thành công", "Đổi mật khẩu thành công.")
        self._o_mat_khau_cu.clear()
        self._o_mat_khau_moi.clear()
        self._o_xac_nhan_mat_khau_moi.clear()

    # ------------------------------------------------------------------
    # CAU HINH HE THONG (ADMIN)
    # ------------------------------------------------------------------
    def _tao_tab_cau_hinh_he_thong(self) -> QWidget:
        trang = QWidget()
        cuon = QScrollArea()
        cuon.setWidgetResizable(True)
        noi_dung = QWidget()
        bo_cuc = QVBoxLayout(noi_dung)
        bo_cuc.setAlignment(Qt.AlignmentFlag.AlignTop)
        bo_cuc.setSpacing(10)

        nhan_ghi_chu = QLabel(
            "Các giá trị dưới đây được lưu trong bảng cau_hinh và áp dụng ngay cho lần "
            "điểm danh/đăng nhập tiếp theo mà không cần khởi động lại chương trình."
        )
        nhan_ghi_chu.setWordWrap(True)
        bo_cuc.addWidget(nhan_ghi_chu)

        self._o_cau_hinh: dict[str, QLineEdit] = {}
        khung_form = QFrame()
        bo_cuc_form = QFormLayout(khung_form)

        cac_khoa_can_hien_thi = [
            ("NGUONG_DO_TUONG_DONG", "Ngưỡng độ tương đồng khuôn mặt (0.0 - 1.0)"),
            ("SO_LAN_DANG_NHAP_SAI_TOI_DA", "Số lần đăng nhập sai tối đa"),
            ("THOI_GIAN_KHOA_TAI_KHOAN_PHUT", "Thời gian khóa tài khoản (phút)"),
            ("PHUT_TINH_DI_MUON", "Số phút được tính là đi muộn"),
        ]
        danh_sach_hien_co = {c.khoa_cau_hinh: c.gia_tri for c in dv_cau_hinh.lay_danh_sach_cau_hinh()}
        for khoa, nhan in cac_khoa_can_hien_thi:
            o_nhap = QLineEdit(danh_sach_hien_co.get(khoa, ""))
            self._o_cau_hinh[khoa] = o_nhap
            bo_cuc_form.addRow(f"{nhan}:", o_nhap)

        nut_luu = QPushButton("Lưu Cấu Hình")
        nut_luu.setObjectName("nutChinh")
        nut_luu.clicked.connect(self._xu_ly_luu_cau_hinh)
        bo_cuc_form.addRow(nut_luu)

        bo_cuc.addWidget(khung_form)
        cuon.setWidget(noi_dung)
        bo_cuc_trang = QVBoxLayout(trang)
        bo_cuc_trang.addWidget(cuon)
        return trang

    def _xu_ly_luu_cau_hinh(self) -> None:
        try:
            for khoa, o_nhap in self._o_cau_hinh.items():
                gia_tri = o_nhap.text().strip()
                if gia_tri:
                    dv_cau_hinh.cap_nhat_cau_hinh(
                        self.phien_dang_nhap.vai_tro,
                        khoa,
                        gia_tri,
                        nguoi_thuc_hien_id=self.phien_dang_nhap.nguoi_dung_id,
                    )
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể lưu cấu hình", str(loi))
            return
        QMessageBox.information(self, "Thành công", "Đã lưu cấu hình hệ thống.")

    # ------------------------------------------------------------------
    # QUAN LY TAI KHOAN (ADMIN)
    # ------------------------------------------------------------------
    def _tao_tab_quan_ly_tai_khoan(self) -> QWidget:
        trang = QWidget()
        bo_cuc = QVBoxLayout(trang)

        hang_cong_cu = QHBoxLayout()
        hang_cong_cu.addStretch(1)
        nut_tao = QPushButton("+ Tạo Tài Khoản")
        nut_tao.setObjectName("nutChinh")
        nut_tao.clicked.connect(self._xu_ly_tao_tai_khoan)
        hang_cong_cu.addWidget(nut_tao)
        bo_cuc.addLayout(hang_cong_cu)

        self._bang_tai_khoan = QTableWidget(0, 5)
        self._bang_tai_khoan.setHorizontalHeaderLabels(
            ["Tên đăng nhập", "Họ tên", "Vai trò", "Trạng thái", "Đăng nhập cuối"]
        )
        self._bang_tai_khoan.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self._bang_tai_khoan.horizontalHeader().setStretchLastSection(False)
        self._bang_tai_khoan.horizontalHeader().setMinimumSectionSize(88)
        self._bang_tai_khoan.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._bang_tai_khoan.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        bo_cuc.addWidget(self._bang_tai_khoan, stretch=1)

        hang_nut = QHBoxLayout()
        nut_khoa = QPushButton("Khóa Tài Khoản")
        nut_khoa.clicked.connect(lambda: self._xu_ly_khoa_mo_khoa(True))
        nut_mo_khoa = QPushButton("Mở Khóa Tài Khoản")
        nut_mo_khoa.clicked.connect(lambda: self._xu_ly_khoa_mo_khoa(False))
        nut_dat_lai_mk = QPushButton("Đặt Lại Mật Khẩu")
        nut_dat_lai_mk.clicked.connect(self._xu_ly_dat_lai_mat_khau)
        hang_nut.addWidget(nut_khoa)
        hang_nut.addWidget(nut_mo_khoa)
        hang_nut.addWidget(nut_dat_lai_mk)
        hang_nut.addStretch(1)
        bo_cuc.addLayout(hang_nut)

        self._nap_lai_danh_sach_tai_khoan()
        return trang

    def _nap_lai_danh_sach_tai_khoan(self) -> None:
        bang_vai_tro = {"ADMIN": "Quản trị viên", "GIANG_VIEN": "Giảng viên", "SINH_VIEN": "Sinh viên"}
        bang_trang_thai = {
            "HOAT_DONG": "Đang hoạt động", "KHOA": "Đang bị khóa", "NGUNG_HOAT_DONG": "Ngừng hoạt động",
        }
        danh_sach = dv_tai_khoan.lay_danh_sach_tai_khoan()
        self._bang_tai_khoan.setRowCount(len(danh_sach))
        for hang, tk in enumerate(danh_sach):
            lan_cuoi = tk.lan_dang_nhap_cuoi.strftime("%d/%m/%Y %H:%M") if tk.lan_dang_nhap_cuoi else "-"
            gia_tri_cac_cot = [
                tk.ten_dang_nhap, tk.ho_ten, bang_vai_tro.get(tk.vai_tro, tk.vai_tro),
                bang_trang_thai.get(tk.trang_thai, tk.trang_thai), lan_cuoi,
            ]
            for cot, gia_tri in enumerate(gia_tri_cac_cot):
                muc = QTableWidgetItem(gia_tri)
                muc.setData(Qt.ItemDataRole.UserRole, tk.id)
                self._bang_tai_khoan.setItem(hang, cot, muc)

    def _lay_id_tai_khoan_dang_chon(self) -> int | None:
        hang = self._bang_tai_khoan.currentRow()
        if hang < 0:
            return None
        muc = self._bang_tai_khoan.item(hang, 0)
        return muc.data(Qt.ItemDataRole.UserRole) if muc else None

    def _xu_ly_tao_tai_khoan(self) -> None:
        hop_thoai = HopThoaiTaoTaiKhoan(self)
        if hop_thoai.exec() != QDialog.DialogCode.Accepted:
            return
        du_lieu = hop_thoai.lay_du_lieu_nhap()
        if not du_lieu["ten_dang_nhap"] or not du_lieu["ho_ten"] or not du_lieu["mat_khau_ban_dau"]:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng điền đầy đủ các trường bắt buộc.")
            return
        try:
            dv_tai_khoan.tao_tai_khoan(
                self.phien_dang_nhap.vai_tro,
                nguoi_thuc_hien_id=self.phien_dang_nhap.nguoi_dung_id,
                **du_lieu,
            )
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể tạo tài khoản", str(loi))
            return
        self._nap_lai_danh_sach_tai_khoan()

    def _xu_ly_khoa_mo_khoa(self, khoa: bool) -> None:
        tai_khoan_id = self._lay_id_tai_khoan_dang_chon()
        if tai_khoan_id is None:
            QMessageBox.information(self, "Chưa chọn", "Vui lòng chọn một tài khoản.")
            return
        try:
            dv_tai_khoan.khoa_hoac_mo_khoa_tai_khoan(
                self.phien_dang_nhap.vai_tro,
                tai_khoan_id,
                khoa,
                nguoi_thuc_hien_id=self.phien_dang_nhap.nguoi_dung_id,
            )
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể thực hiện", str(loi))
            return
        self._nap_lai_danh_sach_tai_khoan()

    def _xu_ly_dat_lai_mat_khau(self) -> None:
        tai_khoan_id = self._lay_id_tai_khoan_dang_chon()
        if tai_khoan_id is None:
            QMessageBox.information(self, "Chưa chọn", "Vui lòng chọn một tài khoản.")
            return
        from PySide6.QtWidgets import QInputDialog

        mat_khau_moi, ok = QInputDialog.getText(
            self, "Đặt Lại Mật Khẩu", "Nhập mật khẩu mới cho tài khoản này:",
            QLineEdit.EchoMode.Password,
        )
        if not ok or not mat_khau_moi:
            return
        try:
            dv_tai_khoan.dat_lai_mat_khau(
                self.phien_dang_nhap.vai_tro,
                tai_khoan_id,
                mat_khau_moi,
                nguoi_thuc_hien_id=self.phien_dang_nhap.nguoi_dung_id,
            )
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể đặt lại mật khẩu", str(loi))
            return
        QMessageBox.information(self, "Thành công", "Đã đặt lại mật khẩu cho tài khoản.")
