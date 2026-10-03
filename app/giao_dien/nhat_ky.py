"""Man hinh Nhat Ky He Thong: xem audit log, loc theo hanh dong."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.dich_vu import nhat_ky as dv_nhat_ky
from app.dich_vu.xac_thuc import PhienDangNhap

_CAC_HANH_DONG_THUONG_GAP = [
    ("Tất cả hành động", None),
    ("Đăng nhập / thất bại", "DANG_NHAP"),
    ("Đăng xuất", "DANG_XUAT"),
    ("Đổi mật khẩu", "DOI_MAT_KHAU"),
    ("Đặt lại mật khẩu", "DAT_LAI_MAT_KHAU"),
    ("Tạo tài khoản", "TAO_TAI_KHOAN"),
    ("Khóa / mở khóa tài khoản", "KHOA_TAI_KHOAN"),
    ("Đăng ký khuôn mặt", "DANG_KY_KHUON_MAT"),
    ("Xóa khuôn mặt", "XOA_KHUON_MAT"),
    ("Tạo buổi học", "TAO_BUOI_HOC"),
    ("Mở điểm danh", "MO_DIEM_DANH"),
    ("Đóng điểm danh", "DONG_DIEM_DANH"),
    ("Điểm danh", "DIEM_DANH"),
    ("Sửa điểm danh", "SUA_DIEM_DANH"),
    ("Thêm sinh viên", "THEM_SINH_VIEN"),
    ("Cập nhật sinh viên", "CAP_NHAT_SINH_VIEN"),
    ("Xóa sinh viên", "XOA_SINH_VIEN"),
    ("Đổi trạng thái sinh viên", "DOI_TRANG_THAI_SINH_VIEN"),
    ("Thêm giảng viên", "THEM_GIANG_VIEN"),
    ("Cập nhật giảng viên", "CAP_NHAT_GIANG_VIEN"),
    ("Xóa giảng viên", "XOA_GIANG_VIEN"),
    ("Thay đổi cấu hình", "THAY_DOI_CAU_HINH"),
    ("Xuất báo cáo Excel", "XUAT_BAO_CAO_EXCEL"),
    ("Xuất báo cáo PDF", "XUAT_BAO_CAO_PDF"),
]


class TrangNhatKy(QWidget):
    """Trang xem nhat ky he thong (audit log). Chi ADMIN duoc phep truy cap trang nay."""

    def __init__(self, phien_dang_nhap: PhienDangNhap) -> None:
        super().__init__()
        self.phien_dang_nhap = phien_dang_nhap
        self._xay_dung_giao_dien()
        self._nap_lai_danh_sach()

    def _xay_dung_giao_dien(self) -> None:
        bo_cuc = QVBoxLayout(self)
        bo_cuc.setContentsMargins(28, 24, 28, 24)
        bo_cuc.setSpacing(14)

        nhan_tieu_de = QLabel("Nhật Ký Hệ Thống")
        nhan_tieu_de.setObjectName("nhanTieuDeTrang")
        bo_cuc.addWidget(nhan_tieu_de)

        hang_bo_loc = QHBoxLayout()
        hang_bo_loc.addWidget(QLabel("Lọc theo hành động:"))
        self._o_hanh_dong = QComboBox()
        for nhan, gia_tri in _CAC_HANH_DONG_THUONG_GAP:
            self._o_hanh_dong.addItem(nhan, gia_tri)
        self._o_hanh_dong.currentIndexChanged.connect(lambda _: self._nap_lai_danh_sach())
        hang_bo_loc.addWidget(self._o_hanh_dong)

        nut_lam_moi = QPushButton("🔄  Làm Mới")
        nut_lam_moi.clicked.connect(self._nap_lai_danh_sach)
        hang_bo_loc.addWidget(nut_lam_moi)
        hang_bo_loc.addStretch(1)
        bo_cuc.addLayout(hang_bo_loc)

        self._bang = QTableWidget(0, 7)
        self._bang.setHorizontalHeaderLabels(
            ["Thời gian", "Người dùng", "Hành động", "Đối tượng", "Nội dung", "Địa chỉ IP", "Kết quả"]
        )
        self._bang.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self._bang.horizontalHeader().setStretchLastSection(False)
        self._bang.horizontalHeader().setMinimumSectionSize(88)
        self._bang.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        bo_cuc.addWidget(self._bang, stretch=1)

    def _nap_lai_danh_sach(self) -> None:
        hanh_dong_loc = self._o_hanh_dong.currentData()
        danh_sach = dv_nhat_ky.lay_danh_sach_nhat_ky(gioi_han=300, hanh_dong=hanh_dong_loc)
        bang_ket_qua = {"THANH_CONG": "Thành công", "THAT_BAI": "Thất bại"}
        self._bang.setRowCount(len(danh_sach))
        for hang, bg in enumerate(danh_sach):
            doi_tuong_hien_thi = (
                f"{bg.doi_tuong}#{bg.doi_tuong_id}" if bg.doi_tuong else "-"
            )
            gia_tri_cac_cot = [
                bg.thoi_gian.strftime("%d/%m/%Y %H:%M:%S"),
                bg.ten_dang_nhap,
                bg.hanh_dong,
                doi_tuong_hien_thi,
                bg.noi_dung or "-",
                bg.dia_chi_ip or "-",
                bang_ket_qua.get(bg.ket_qua, bg.ket_qua),
            ]
            for cot, gia_tri in enumerate(gia_tri_cac_cot):
                self._bang.setItem(hang, cot, QTableWidgetItem(gia_tri))
