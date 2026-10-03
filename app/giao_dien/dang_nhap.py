"""Man hinh Dang Nhap: giao dien dau tien nguoi dung thay khi mo ung dung."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.dich_vu.xac_thuc import LoiXacThuc, PhienDangNhap, dang_nhap
from app.tien_ich.hieu_ung_giao_dien import ap_dung_do_bong


class ManHinhDangNhap(QWidget):
    """Man hinh dang nhap he thong. Phat tin hieu `dang_nhap_thanh_cong` khi xac thuc OK."""

    dang_nhap_thanh_cong = Signal(object)  # object = PhienDangNhap

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("nenDangNhap")
        self.setWindowTitle("Đăng Nhập - Hệ Thống Điểm Danh Sinh Viên Bằng Khuôn Mặt")
        self.resize(1100, 700)
        self._xay_dung_giao_dien()

    def _xay_dung_giao_dien(self) -> None:
        bo_cuc_ngoai = QVBoxLayout(self)
        bo_cuc_ngoai.setContentsMargins(0, 0, 0, 0)
        bo_cuc_ngoai.setAlignment(Qt.AlignmentFlag.AlignCenter)

        khung = QFrame()
        khung.setObjectName("khungDangNhap")
        khung.setFixedWidth(400)
        bo_cuc = QVBoxLayout(khung)
        bo_cuc.setContentsMargins(44, 44, 44, 40)
        bo_cuc.setSpacing(6)
        bo_cuc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ap_dung_do_bong(khung, do_mo=48, do_lech_y=16)

        # ----- Bieu tuong (logo) hinh tron voi chu cai dau -----
        khung_bieu_tuong = QFrame()
        khung_bieu_tuong.setObjectName("khungBieuTuong")
        khung_bieu_tuong.setFixedSize(64, 64)
        bo_cuc_bieu_tuong = QVBoxLayout(khung_bieu_tuong)
        bo_cuc_bieu_tuong.setContentsMargins(0, 0, 0, 0)
        nhan_bieu_tuong = QLabel("🎓")
        nhan_bieu_tuong.setObjectName("nhanBieuTuong")
        nhan_bieu_tuong.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bo_cuc_bieu_tuong.addWidget(nhan_bieu_tuong)
        bo_cuc.addWidget(khung_bieu_tuong, alignment=Qt.AlignmentFlag.AlignHCenter)
        bo_cuc.addSpacing(18)

        nhan_tieu_de = QLabel("HỆ THỐNG ĐIỂM DANH\nSINH VIÊN BẰNG KHUÔN MẶT")
        nhan_tieu_de.setObjectName("nhanTieuDeDangNhap")
        nhan_tieu_de.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_tieu_de = QFont()
        font_tieu_de.setPointSize(15)
        font_tieu_de.setBold(True)
        nhan_tieu_de.setFont(font_tieu_de)
        bo_cuc.addWidget(nhan_tieu_de)

        nhan_phu = QLabel("Vui lòng đăng nhập để tiếp tục")
        nhan_phu.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nhan_phu.setObjectName("nhanPhu")
        bo_cuc.addWidget(nhan_phu)
        bo_cuc.addSpacing(22)

        self._o_ten_dang_nhap = QLineEdit()
        self._o_ten_dang_nhap.setPlaceholderText("Tên đăng nhập")
        self._o_ten_dang_nhap.setMinimumHeight(44)
        bo_cuc.addWidget(self._o_ten_dang_nhap)
        bo_cuc.addSpacing(10)

        self._o_mat_khau = QLineEdit()
        self._o_mat_khau.setPlaceholderText("Mật khẩu")
        self._o_mat_khau.setEchoMode(QLineEdit.EchoMode.Password)
        self._o_mat_khau.setMinimumHeight(44)
        self._o_mat_khau.returnPressed.connect(self._xu_ly_dang_nhap)
        bo_cuc.addWidget(self._o_mat_khau)

        self._nhan_loi = QLabel("")
        self._nhan_loi.setObjectName("nhanLoi")
        self._nhan_loi.setWordWrap(True)
        self._nhan_loi.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bo_cuc.addWidget(self._nhan_loi)
        bo_cuc.addSpacing(6)

        nut_dang_nhap = QPushButton("ĐĂNG NHẬP")
        nut_dang_nhap.setObjectName("nutChinh")
        nut_dang_nhap.setMinimumHeight(46)
        nut_dang_nhap.setCursor(Qt.CursorShape.PointingHandCursor)
        nut_dang_nhap.clicked.connect(self._xu_ly_dang_nhap)
        bo_cuc.addWidget(nut_dang_nhap)
        bo_cuc.addSpacing(20)

        nhan_ghi_chu = QLabel(
            "Tài khoản mẫu:\n"
            "admin / Admin@123\n"
            "giangvien01 / GiangVien@123\n"
            "sinhvien01 / SinhVien@123"
        )
        nhan_ghi_chu.setObjectName("nhanGhiChu")
        nhan_ghi_chu.setWordWrap(True)
        nhan_ghi_chu.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bo_cuc.addWidget(nhan_ghi_chu)

        bo_cuc_ngoai.addWidget(khung, alignment=Qt.AlignmentFlag.AlignCenter)
        self._o_ten_dang_nhap.setFocus()

    def _xu_ly_dang_nhap(self) -> None:
        ten_dang_nhap = self._o_ten_dang_nhap.text().strip()
        mat_khau = self._o_mat_khau.text()
        if not ten_dang_nhap or not mat_khau:
            self._nhan_loi.setText("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
            return
        try:
            phien: PhienDangNhap = dang_nhap(ten_dang_nhap, mat_khau)
        except LoiXacThuc as loi:
            self._nhan_loi.setText(str(loi))
            return
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(
                self,
                "Lỗi hệ thống",
                f"Đã xảy ra lỗi không mong muốn khi đăng nhập:\n{loi}\n\n"
                "Vui lòng kiểm tra kết nối MySQL/XAMPP.",
            )
            return

        self._nhan_loi.setText("")
        self._o_mat_khau.clear()
        self.dang_nhap_thanh_cong.emit(phien)
