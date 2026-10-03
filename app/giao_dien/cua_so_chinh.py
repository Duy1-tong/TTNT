"""Man hinh Cua So Chinh: sidebar dieu huong + vung noi dung (QStackedWidget)."""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.dich_vu.phan_quyen import QuyenHeThong, co_quyen
from app.dich_vu.xac_thuc import PhienDangNhap, dang_xuat

_bo_ghi_log = logging.getLogger(__name__)

# Giu tham chieu toi cac cua so chinh duoc tao lai sau moi lan dang xuat/dang
# nhap tai khoan khac, tranh bi Python tu dong don rac (garbage collected)
# ngay sau khi hien thi - neu khong, cua so moi se bien mat lang le.
_cac_cua_so_dang_mo: list["CuaSoChinh"] = []


class CuaSoChinh(QMainWindow):
    """Cua so chinh cua ung dung sau khi dang nhap thanh cong."""

    def __init__(self, phien_dang_nhap: PhienDangNhap) -> None:
        super().__init__()
        self.phien_dang_nhap = phien_dang_nhap
        self.setWindowTitle("He Thong Diem Danh Sinh Vien Bang Khuon Mat")
        self.resize(1280, 800)

        self._cac_trang: dict[str, QWidget] = {}
        self._xay_dung_giao_dien()
        self._nap_danh_sach_menu()

    # ------------------------------------------------------------------
    def _xay_dung_giao_dien(self) -> None:
        widget_trung_tam = QWidget()
        bo_cuc_chinh = QHBoxLayout(widget_trung_tam)
        bo_cuc_chinh.setContentsMargins(0, 0, 0, 0)
        bo_cuc_chinh.setSpacing(0)

        # ----- Sidebar -----
        khung_sidebar = QFrame()
        khung_sidebar.setObjectName("sidebar")
        khung_sidebar.setFixedWidth(260)
        bo_cuc_sidebar = QVBoxLayout(khung_sidebar)
        bo_cuc_sidebar.setContentsMargins(0, 0, 0, 0)
        bo_cuc_sidebar.setSpacing(0)

        khung_thuong_hieu = QFrame()
        khung_thuong_hieu.setObjectName("khungThuongHieu")
        bo_cuc_thuong_hieu = QHBoxLayout(khung_thuong_hieu)
        bo_cuc_thuong_hieu.setContentsMargins(20, 18, 20, 18)
        bo_cuc_thuong_hieu.setSpacing(10)
        nhan_bieu_tuong_nho = QLabel("🎓")
        nhan_bieu_tuong_nho.setObjectName("nhanBieuTuongNho")
        nhan_bieu_tuong_nho.setFixedSize(36, 36)
        nhan_bieu_tuong_nho.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bo_cuc_thuong_hieu.addWidget(nhan_bieu_tuong_nho)
        khung_ten_ung_dung = QVBoxLayout()
        khung_ten_ung_dung.setSpacing(0)
        nhan_ten_ung_dung = QLabel("Điểm Danh")
        nhan_ten_ung_dung.setObjectName("nhanTenUngDung")
        nhan_khau_hieu = QLabel("Nhận diện khuôn mặt")
        nhan_khau_hieu.setObjectName("nhanKhauHieu")
        khung_ten_ung_dung.addWidget(nhan_ten_ung_dung)
        khung_ten_ung_dung.addWidget(nhan_khau_hieu)
        bo_cuc_thuong_hieu.addLayout(khung_ten_ung_dung)
        bo_cuc_thuong_hieu.addStretch(1)
        bo_cuc_sidebar.addWidget(khung_thuong_hieu)

        khung_thong_tin_user = QFrame()
        khung_thong_tin_user.setObjectName("khungThongTinUser")
        bo_cuc_user = QHBoxLayout(khung_thong_tin_user)
        bo_cuc_user.setContentsMargins(20, 16, 20, 16)
        bo_cuc_user.setSpacing(12)
        nhan_chu_cai_dau = QLabel(_lay_chu_cai_dau(self.phien_dang_nhap.ho_ten))
        nhan_chu_cai_dau.setObjectName("nhanChuCaiDauTen")
        nhan_chu_cai_dau.setFixedSize(40, 40)
        nhan_chu_cai_dau.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bo_cuc_user.addWidget(nhan_chu_cai_dau)
        khung_ten_vai_tro = QVBoxLayout()
        khung_ten_vai_tro.setSpacing(2)
        nhan_ho_ten = QLabel(self.phien_dang_nhap.ho_ten)
        nhan_ho_ten.setObjectName("nhanHoTen")
        nhan_vai_tro = QLabel(_ten_hien_thi_vai_tro(self.phien_dang_nhap.vai_tro))
        nhan_vai_tro.setObjectName("nhanVaiTro")
        khung_ten_vai_tro.addWidget(nhan_ho_ten)
        khung_ten_vai_tro.addWidget(nhan_vai_tro)
        bo_cuc_user.addLayout(khung_ten_vai_tro, stretch=1)
        bo_cuc_sidebar.addWidget(khung_thong_tin_user)

        self._danh_sach_menu = QListWidget()
        self._danh_sach_menu.setObjectName("danhSachMenu")
        self._danh_sach_menu.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._danh_sach_menu.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._danh_sach_menu.setFrameShape(QFrame.Shape.NoFrame)
        self._danh_sach_menu.currentRowChanged.connect(self._chuyen_trang)
        bo_cuc_sidebar.addWidget(self._danh_sach_menu, stretch=1)

        nut_dang_xuat = QPushButton("Đăng Xuất")
        nut_dang_xuat.setObjectName("nutDangXuat")
        nut_dang_xuat.clicked.connect(self._xu_ly_dang_xuat)
        bo_cuc_sidebar.addWidget(nut_dang_xuat)

        bo_cuc_chinh.addWidget(khung_sidebar)

        # ----- Vung noi dung -----
        self._vung_noi_dung = QStackedWidget()
        bo_cuc_chinh.addWidget(self._vung_noi_dung, stretch=1)

        self.setCentralWidget(widget_trung_tam)

    def _nap_danh_sach_menu(self) -> None:
        """Xay dung danh sach menu theo vai tro (chi de UX; quyen thuc su
        van luon duoc kiem tra o tang Service, khong phu thuoc vao viec an nut)."""
        vai_tro = self.phien_dang_nhap.vai_tro
        cac_muc_menu: list[tuple[str, str, QuyenHeThong | None]] = [
            ("tong_quan", "📊  Tổng Quan", None),
            ("quan_ly_sinh_vien", "🧑‍🎓  Quản Lý Sinh Viên", QuyenHeThong.QUAN_LY_SINH_VIEN),
            ("quan_ly_giang_vien", "👨‍🏫  Quản Lý Giảng Viên", QuyenHeThong.QUAN_LY_GIANG_VIEN),
            ("quan_ly_lop", "🏫  Quản Lý Khoa - Lớp", QuyenHeThong.QUAN_LY_LOP),
            ("quan_ly_mon", "📚  Quản Lý Môn - Lớp Học Phần", QuyenHeThong.QUAN_LY_MON_HOC),
            ("dang_ky_khuon_mat", "🪪  Đăng Ký Khuôn Mặt", QuyenHeThong.DANG_KY_KHUON_MAT),
            ("diem_danh", "📷  Điểm Danh", QuyenHeThong.THUC_HIEN_DIEM_DANH),
            ("bao_cao", "📈  Báo Cáo", None),
            ("nhat_ky", "🗒️  Nhật Ký Hệ Thống", QuyenHeThong.XEM_NHAT_KY_HE_THONG),
            ("cai_dat", "⚙️  Cài Đặt", None),
        ]

        for khoa_trang, nhan_hien_thi, quyen_can in cac_muc_menu:
            if quyen_can is not None and not co_quyen(vai_tro, quyen_can):
                # Truong hop rieng: sinh vien van duoc xem "Bao cao" (lich su ca nhan)
                # va "Dang ky khuon mat" chi hien thi neu duoc phep dang ky ho so ban than.
                if khoa_trang == "bao_cao" and co_quyen(
                    vai_tro, QuyenHeThong.XEM_LICH_SU_DIEM_DANH_CA_NHAN
                ):
                    pass
                else:
                    continue
            self._danh_sach_menu.addItem(QListWidgetItem(nhan_hien_thi))
            self._cac_trang[khoa_trang] = None  # type: ignore[assignment]

        if self._danh_sach_menu.count() > 0:
            self._danh_sach_menu.setCurrentRow(0)

    def _chuyen_trang(self, chi_so_dong: int) -> None:
        if chi_so_dong < 0:
            return
        cac_khoa_trang = list(self._cac_trang.keys())
        if chi_so_dong >= len(cac_khoa_trang):
            return
        khoa_trang = cac_khoa_trang[chi_so_dong]
        trang = self._cac_trang.get(khoa_trang)
        if trang is None:
            trang = self._tao_trang(khoa_trang)
            self._cac_trang[khoa_trang] = trang
            self._vung_noi_dung.addWidget(trang)
        self._vung_noi_dung.setCurrentWidget(trang)

    def _tao_trang(self, khoa_trang: str) -> QWidget:
        """Tao (lazy-load) widget cho tung trang, tranh khoi tao camera/model AI
        khi nguoi dung chua thuc su mo den trang do."""
        try:
            if khoa_trang == "tong_quan":
                from app.giao_dien.tong_quan import TrangTongQuan

                return TrangTongQuan(self.phien_dang_nhap)
            if khoa_trang == "quan_ly_sinh_vien":
                from app.giao_dien.quan_ly_sinh_vien import TrangQuanLySinhVien

                return TrangQuanLySinhVien(self.phien_dang_nhap)
            if khoa_trang == "quan_ly_giang_vien":
                from app.giao_dien.quan_ly_giang_vien import TrangQuanLyGiangVien

                return TrangQuanLyGiangVien(self.phien_dang_nhap)
            if khoa_trang == "quan_ly_lop":
                from app.giao_dien.quan_ly_lop import TrangQuanLyLop

                return TrangQuanLyLop(self.phien_dang_nhap)
            if khoa_trang == "quan_ly_mon":
                from app.giao_dien.quan_ly_mon import TrangQuanLyMon

                return TrangQuanLyMon(self.phien_dang_nhap)
            if khoa_trang == "dang_ky_khuon_mat":
                from app.giao_dien.dang_ky_khuon_mat import TrangDangKyKhuonMat

                return TrangDangKyKhuonMat(self.phien_dang_nhap)
            if khoa_trang == "diem_danh":
                from app.giao_dien.diem_danh import TrangDiemDanh

                return TrangDiemDanh(self.phien_dang_nhap)
            if khoa_trang == "bao_cao":
                from app.giao_dien.bao_cao import TrangBaoCao

                return TrangBaoCao(self.phien_dang_nhap)
            if khoa_trang == "nhat_ky":
                from app.giao_dien.nhat_ky import TrangNhatKy

                return TrangNhatKy(self.phien_dang_nhap)
            if khoa_trang == "cai_dat":
                from app.giao_dien.cai_dat import TrangCaiDat

                return TrangCaiDat(self.phien_dang_nhap)
        except Exception as loi:  # noqa: BLE001
            _bo_ghi_log.exception("Loi khi tao trang '%s'", khoa_trang)
            trang_loi = QWidget()
            bo_cuc = QVBoxLayout(trang_loi)
            nhan = QLabel(f"Khong the tai trang nay.\n\nChi tiet loi: {loi}")
            nhan.setWordWrap(True)
            nhan.setAlignment(Qt.AlignmentFlag.AlignCenter)
            bo_cuc.addWidget(nhan)
            return trang_loi
        return QWidget()

    def _xu_ly_dang_xuat(self) -> None:
        xac_nhan = QMessageBox.question(
            self, "Xac nhan dang xuat", "Ban co chac muon dang xuat khoi he thong?"
        )
        if xac_nhan != QMessageBox.StandardButton.Yes:
            return
        dang_xuat(self.phien_dang_nhap.nguoi_dung_id)
        # QUAN TRONG: phai MO man hinh dang nhap moi TRUOC roi moi DONG cua so
        # hien tai. Neu dong truoc, se co mot khoanh khac KHONG CON cua so nao
        # hien thi, khien Qt tu dong thoat toan bo ung dung (quitOnLastWindowClosed)
        # ma khong bao loi gi ra terminal.
        self._mo_lai_man_hinh_dang_nhap()
        self.close()

    def _mo_lai_man_hinh_dang_nhap(self) -> None:
        from app.giao_dien.dang_nhap import ManHinhDangNhap

        self._man_hinh_dang_nhap_moi = ManHinhDangNhap()

        def _khi_dang_nhap_lai(phien_moi: PhienDangNhap) -> None:
            cua_so_moi = CuaSoChinh(phien_moi)
            cua_so_moi.show()
            _cac_cua_so_dang_mo.append(cua_so_moi)
            self._man_hinh_dang_nhap_moi.close()

        self._man_hinh_dang_nhap_moi.dang_nhap_thanh_cong.connect(_khi_dang_nhap_lai)
        self._man_hinh_dang_nhap_moi.show()

    def closeEvent(self, event) -> None:  # noqa: N802 - override Qt method
        """Dam bao dung camera dang chay (neu co) truoc khi dong ung dung."""
        for trang in self._cac_trang.values():
            if trang is not None and hasattr(trang, "don_dep_truoc_khi_dong"):
                try:
                    trang.don_dep_truoc_khi_dong()
                except Exception:  # noqa: BLE001
                    pass
        super().closeEvent(event)


def _ten_hien_thi_vai_tro(vai_tro: str) -> str:
    """Chuyen ma vai tro sang ten tieng Viet co dau de hien thi."""
    bang_ten = {
        "ADMIN": "Quản Trị Viên",
        "GIANG_VIEN": "Giảng Viên",
        "SINH_VIEN": "Sinh Viên",
    }
    return bang_ten.get(vai_tro, vai_tro)


def _lay_chu_cai_dau(ho_ten: str) -> str:
    """Lay chu cai dau cua tu cuoi cung trong ho ten (thuong la ten goi) de lam avatar."""
    cac_tu = ho_ten.strip().split()
    if not cac_tu:
        return "?"
    return cac_tu[-1][0].upper()
