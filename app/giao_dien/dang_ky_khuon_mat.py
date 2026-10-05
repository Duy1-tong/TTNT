"""Man hinh Dang Ky Khuon Mat: chon sinh vien, bat camera, chup va luu embedding."""

from __future__ import annotations

import logging

import cv2
import numpy as np
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.cau_hinh.cai_dat import lay_cau_hinh
from app.dich_vu import khuon_mat as dv_khuon_mat, sinh_vien as dv_sinh_vien
from app.dich_vu.khuon_mat import LoiDangKyKhuonMat
from app.dich_vu.xac_thuc import PhienDangNhap

_bo_ghi_log = logging.getLogger(__name__)


class TrangDangKyKhuonMat(QWidget):
    """Trang dang ky khuon mat cho sinh vien, dung camera de chup truc tiep."""

    def __init__(self, phien_dang_nhap: PhienDangNhap) -> None:
        super().__init__()
        self.phien_dang_nhap = phien_dang_nhap
        self._camera: cv2.VideoCapture | None = None
        self._bo_dinh_thoi = QTimer(self)
        self._bo_dinh_thoi.timeout.connect(self._cap_nhat_khung_hinh)
        self._khung_hinh_hien_tai: np.ndarray | None = None

        self._xay_dung_giao_dien()
        self._nap_danh_sach_sinh_vien()

    def _xay_dung_giao_dien(self) -> None:
        bo_cuc = QVBoxLayout(self)
        bo_cuc.setContentsMargins(28, 24, 28, 24)
        bo_cuc.setSpacing(14)

        nhan_tieu_de = QLabel("Đăng Ký Khuôn Mặt Sinh Viên")
        nhan_tieu_de.setObjectName("nhanTieuDeTrang")
        bo_cuc.addWidget(nhan_tieu_de)

        bo_cuc_ngang = QHBoxLayout()
        bo_cuc_ngang.setSpacing(20)

        # ----- Cot trai: chon sinh vien + danh sach da dang ky -----
        khung_trai = QFrame()
        bo_cuc_trai = QVBoxLayout(khung_trai)
        bo_cuc_trai.addWidget(QLabel("Chọn sinh viên:"))
        self._o_sinh_vien = QComboBox()
        self._o_sinh_vien.currentIndexChanged.connect(lambda _: self._nap_danh_sach_khuon_mat())
        bo_cuc_trai.addWidget(self._o_sinh_vien)

        bo_cuc_trai.addWidget(QLabel("Khuôn mặt đã đăng ký:"))
        self._danh_sach_khuon_mat = QListWidget()
        bo_cuc_trai.addWidget(self._danh_sach_khuon_mat, stretch=1)

        nut_xoa_khuon_mat = QPushButton("Xóa Khuôn Mặt Đã Chọn")
        nut_xoa_khuon_mat.setObjectName("nutNguyHiem")
        nut_xoa_khuon_mat.clicked.connect(self._xu_ly_xoa_khuon_mat)
        bo_cuc_trai.addWidget(nut_xoa_khuon_mat)

        bo_cuc_ngang.addWidget(khung_trai, stretch=1)

        # ----- Cot phai: camera -----
        khung_phai = QFrame()
        bo_cuc_phai = QVBoxLayout(khung_phai)

        self._nhan_camera = QLabel("Camera chưa được bật.")
        self._nhan_camera.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._nhan_camera.setMinimumSize(480, 360)
        self._nhan_camera.setObjectName("khungCamera")
        bo_cuc_phai.addWidget(self._nhan_camera)

        hang_nut_camera = QHBoxLayout()
        self._nut_bat_camera = QPushButton("Bật Camera")
        self._nut_bat_camera.clicked.connect(self._xu_ly_bat_tat_camera)
        hang_nut_camera.addWidget(self._nut_bat_camera)

        nut_chup_dang_ky = QPushButton("📸  Chụp & Đăng Ký Khuôn Mặt")
        nut_chup_dang_ky.setObjectName("nutChinh")
        nut_chup_dang_ky.clicked.connect(self._xu_ly_chup_va_dang_ky)
        hang_nut_camera.addWidget(nut_chup_dang_ky)
        bo_cuc_phai.addLayout(hang_nut_camera)

        bo_cuc_ngang.addWidget(khung_phai, stretch=1)
        bo_cuc.addLayout(bo_cuc_ngang, stretch=1)

    def _nap_danh_sach_sinh_vien(self) -> None:
        self._o_sinh_vien.blockSignals(True)
        self._o_sinh_vien.clear()
        for sv in dv_sinh_vien.lay_danh_sach_sinh_vien():
            self._o_sinh_vien.addItem(f"{sv.ma_sinh_vien} - {sv.ho_ten}", sv.id)
        self._o_sinh_vien.blockSignals(False)
        self._nap_danh_sach_khuon_mat()

    def _nap_danh_sach_khuon_mat(self) -> None:
        self._danh_sach_khuon_mat.clear()
        sinh_vien_id = self._o_sinh_vien.currentData()
        if sinh_vien_id is None:
            return
        for ban_ghi in dv_khuon_mat.lay_danh_sach_khuon_mat_cua_sinh_vien(sinh_vien_id):
            muc = QListWidgetItem(f"Mã #{ban_ghi.id} — mô hình: {ban_ghi.mo_hinh}")
            muc.setData(Qt.ItemDataRole.UserRole, ban_ghi.id)
            self._danh_sach_khuon_mat.addItem(muc)

    # ------------------------------------------------------------------
    # CAMERA
    # ------------------------------------------------------------------
    def _xu_ly_bat_tat_camera(self) -> None:
        if self._camera is not None:
            self._tat_camera()
            return

        chi_so_camera = lay_cau_hinh().ai.chi_so_camera_mac_dinh
        camera = cv2.VideoCapture(chi_so_camera)
        if not camera.isOpened():
            QMessageBox.warning(
                self,
                "Không thể mở camera",
                f"Không thể mở camera tại chỉ số {chi_so_camera}.\n"
                "Vui lòng kiểm tra webcam đã được kết nối, hoặc thay đổi "
                "CHI_SO_CAMERA_MAC_DINH trong file .env.",
            )
            camera.release()
            return

        self._camera = camera
        self._bo_dinh_thoi.start(33)  # ~30 khung hinh/giay
        self._nut_bat_camera.setText("Tắt Camera")

    def _tat_camera(self) -> None:
        self._bo_dinh_thoi.stop()
        if self._camera is not None:
            self._camera.release()
            self._camera = None
        self._nhan_camera.setText("Camera chưa được bật.")
        self._nhan_camera.setPixmap(QPixmap())
        self._nut_bat_camera.setText("Bật Camera")

    def _cap_nhat_khung_hinh(self) -> None:
        if self._camera is None:
            return
        doc_thanh_cong, khung_hinh = self._camera.read()
        if not doc_thanh_cong:
            return
        self._khung_hinh_hien_tai = khung_hinh
        self._hien_thi_khung_hinh(khung_hinh)

    def _hien_thi_khung_hinh(self, khung_hinh_bgr: np.ndarray) -> None:
        # Lật ngang hình ảnh hiển thị để camera giống như gương
        khung_hinh_hien_thi = cv2.flip(khung_hinh_bgr, 1)

        khung_hinh_rgb = cv2.cvtColor(
            khung_hinh_hien_thi,
            cv2.COLOR_BGR2RGB
        )

        cao, rong, kenh = khung_hinh_rgb.shape

        anh_qt = QImage(
            khung_hinh_rgb.data,
            rong,
            cao,
            kenh * rong,
            QImage.Format.Format_RGB888
        )

        self._nhan_camera.setPixmap(
            QPixmap.fromImage(anh_qt).scaled(
                self._nhan_camera.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def _xu_ly_chup_va_dang_ky(self) -> None:
        sinh_vien_id = self._o_sinh_vien.currentData()
        if sinh_vien_id is None:
            QMessageBox.information(self, "Chưa chọn", "Vui lòng chọn một sinh viên trước.")
            return
        if self._khung_hinh_hien_tai is None:
            QMessageBox.information(
                self, "Chưa có hình ảnh", "Vui lòng bật camera và chờ hình ảnh hiển thị."
            )
            return

        try:
            ket_qua = dv_khuon_mat.dang_ky_khuon_mat_tu_anh(
                self.phien_dang_nhap.vai_tro,
                sinh_vien_id,
                self._khung_hinh_hien_tai.copy(),
                nguoi_thuc_hien_id=self.phien_dang_nhap.nguoi_dung_id,
            )
        except LoiDangKyKhuonMat as loi:
            QMessageBox.warning(self, "Không thể đăng ký khuôn mặt", str(loi))
            return
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Lỗi hệ thống", str(loi))
            return

        QMessageBox.information(
            self,
            "Thành công",
            f"Đã đăng ký khuôn mặt thành công (mô hình: {ket_qua.mo_hinh}).",
        )
        self._nap_danh_sach_khuon_mat()

    def _xu_ly_xoa_khuon_mat(self) -> None:
        muc = self._danh_sach_khuon_mat.currentItem()
        if muc is None:
            QMessageBox.information(self, "Chưa chọn", "Vui lòng chọn một khuôn mặt để xóa.")
            return
        khuon_mat_id = muc.data(Qt.ItemDataRole.UserRole)
        xac_nhan = QMessageBox.question(
            self, "Xác nhận xóa", "Bạn có chắc muốn xóa dữ liệu khuôn mặt này?"
        )
        if xac_nhan != QMessageBox.StandardButton.Yes:
            return
        try:
            dv_khuon_mat.xoa_khuon_mat(
                self.phien_dang_nhap.vai_tro,
                khuon_mat_id,
                nguoi_thuc_hien_id=self.phien_dang_nhap.nguoi_dung_id,
            )
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể xóa", str(loi))
            return
        self._nap_danh_sach_khuon_mat()

    def don_dep_truoc_khi_dong(self) -> None:
        """Duoc CuaSoChinh goi truoc khi dong ung dung, dam bao giai phong camera."""
        self._tat_camera()
