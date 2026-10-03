"""Man hinh Diem Danh: quan ly buoi hoc, diem danh bang khuon mat (camera truc tiep)
va diem danh/sua thu cong."""

from __future__ import annotations

import datetime as _datetime
import logging
from collections import deque

import cv2
import numpy as np
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
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
    QTableWidget,
    QTableWidgetItem,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from app.cau_hinh.cai_dat import lay_cau_hinh
from app.dich_vu import danh_muc
from app.dich_vu import diem_danh as dv_diem_danh
from app.dich_vu.diem_danh import LoiDiemDanh
from app.dich_vu.phan_quyen import QuyenHeThong, co_quyen
from app.dich_vu.xac_thuc import PhienDangNhap
from app.mo_hinh.diem_danh import TrangThaiDiemDanh

_bo_ghi_log = logging.getLogger(__name__)

SO_KHUNG_HINH_DEM_LIVENESS = 4
CHU_KY_NHAN_DIEN_MILI_GIAY = 1500


class HopThoaiTaoBuoiHoc(QDialog):
    """Hop thoai tao mot buoi hoc moi cho mot lop hoc phan."""

    def __init__(self, parent: QWidget | None, danh_sach_lop_mon: list) -> None:
        super().__init__(parent)
        self.setWindowTitle("Tạo Buổi Học Mới")
        self.setMinimumWidth(380)
        bo_cuc = QFormLayout(self)

        self._o_lop_mon = QComboBox()
        for lop_mon in danh_sach_lop_mon:
            self._o_lop_mon.addItem(f"{lop_mon.ma_lop_mon} - {lop_mon.ten_mon}", lop_mon.id)
        bo_cuc.addRow("Lớp học phần (*):", self._o_lop_mon)

        self._o_ngay_hoc = QDateEdit()
        self._o_ngay_hoc.setCalendarPopup(True)
        self._o_ngay_hoc.setDate(_datetime.date.today())
        bo_cuc.addRow("Ngày học:", self._o_ngay_hoc)

        self._o_gio_bat_dau = QTimeEdit()
        self._o_gio_bat_dau.setTime(_datetime.time(7, 0))
        bo_cuc.addRow("Giờ bắt đầu:", self._o_gio_bat_dau)

        self._o_gio_ket_thuc = QTimeEdit()
        self._o_gio_ket_thuc.setTime(_datetime.time(9, 30))
        bo_cuc.addRow("Giờ kết thúc:", self._o_gio_ket_thuc)

        self._o_phong_hoc = QLineEdit()
        bo_cuc.addRow("Phòng học:", self._o_phong_hoc)

        nut = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        nut.accepted.connect(self.accept)
        nut.rejected.connect(self.reject)
        bo_cuc.addRow(nut)

    def lay_du_lieu_nhap(self) -> dict:
        return {
            "lop_mon_hoc_id": self._o_lop_mon.currentData(),
            "ngay_hoc": self._o_ngay_hoc.date().toPython(),
            "gio_bat_dau": self._o_gio_bat_dau.time().toPython(),
            "gio_ket_thuc": self._o_gio_ket_thuc.time().toPython(),
            "phong_hoc": self._o_phong_hoc.text().strip() or None,
        }


class TrangDiemDanh(QWidget):
    """Trang thuc hien diem danh: chon buoi hoc, mo/dong diem danh, camera truc tiep."""

    def __init__(self, phien_dang_nhap: PhienDangNhap) -> None:
        super().__init__()
        self.phien_dang_nhap = phien_dang_nhap
        self._camera: cv2.VideoCapture | None = None
        self._bo_dinh_thoi_camera = QTimer(self)
        self._bo_dinh_thoi_camera.timeout.connect(self._cap_nhat_khung_hinh)
        self._bo_dem_khung_hinh: deque[np.ndarray] = deque(maxlen=SO_KHUNG_HINH_DEM_LIVENESS)
        self._bo_dinh_thoi_nhan_dien = QTimer(self)
        self._bo_dinh_thoi_nhan_dien.timeout.connect(self._thu_diem_danh_tu_dong)
        self._buoi_hoc_dang_chon_id: int | None = None
        self._danh_sach_lop_mon: list = []

        self._xay_dung_giao_dien()
        self._nap_danh_sach_lop_mon()

    # ------------------------------------------------------------------
    def _xay_dung_giao_dien(self) -> None:
        bo_cuc = QVBoxLayout(self)
        bo_cuc.setContentsMargins(28, 24, 28, 24)
        bo_cuc.setSpacing(14)

        nhan_tieu_de = QLabel("Điểm Danh")
        nhan_tieu_de.setObjectName("nhanTieuDeTrang")
        bo_cuc.addWidget(nhan_tieu_de)

        hang_chon_buoi = QHBoxLayout()
        hang_chon_buoi.addWidget(QLabel("Lớp học phần:"))
        self._o_lop_mon = QComboBox()
        self._o_lop_mon.currentIndexChanged.connect(lambda _: self._nap_danh_sach_buoi_hoc())
        hang_chon_buoi.addWidget(self._o_lop_mon, stretch=1)

        if co_quyen(self.phien_dang_nhap.vai_tro, QuyenHeThong.QUAN_LY_BUOI_HOC):
            nut_tao_buoi = QPushButton("+ Tạo Buổi Học")
            nut_tao_buoi.clicked.connect(self._xu_ly_tao_buoi_hoc)
            hang_chon_buoi.addWidget(nut_tao_buoi)

        hang_chon_buoi.addWidget(QLabel("Buổi học:"))
        self._o_buoi_hoc = QComboBox()
        self._o_buoi_hoc.currentIndexChanged.connect(self._xu_ly_doi_buoi_hoc)
        hang_chon_buoi.addWidget(self._o_buoi_hoc, stretch=1)
        bo_cuc.addLayout(hang_chon_buoi)

        hang_dieu_khien = QHBoxLayout()
        self._nhan_trang_thai_buoi = QLabel("Chưa chọn buổi học.")
        self._nhan_trang_thai_buoi.setObjectName("nhanTrangThaiBuoiHoc")
        hang_dieu_khien.addWidget(self._nhan_trang_thai_buoi, stretch=1)

        self._nut_mo_diem_danh = QPushButton("Mở Điểm Danh")
        self._nut_mo_diem_danh.setObjectName("nutChinh")
        self._nut_mo_diem_danh.clicked.connect(self._xu_ly_mo_diem_danh)
        hang_dieu_khien.addWidget(self._nut_mo_diem_danh)

        self._nut_dong_diem_danh = QPushButton("Đóng Điểm Danh")
        self._nut_dong_diem_danh.setObjectName("nutNguyHiem")
        self._nut_dong_diem_danh.clicked.connect(self._xu_ly_dong_diem_danh)
        hang_dieu_khien.addWidget(self._nut_dong_diem_danh)
        bo_cuc.addLayout(hang_dieu_khien)

        bo_cuc_ngang = QHBoxLayout()
        bo_cuc_ngang.setSpacing(20)

        # ----- Camera -----
        khung_camera = QFrame()
        bo_cuc_camera = QVBoxLayout(khung_camera)
        self._nhan_camera = QLabel("Camera chưa được bật.")
        self._nhan_camera.setObjectName("khungCamera")
        self._nhan_camera.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._nhan_camera.setMinimumSize(480, 360)
        bo_cuc_camera.addWidget(self._nhan_camera)

        hang_nut_camera = QHBoxLayout()
        self._nut_bat_camera = QPushButton("Bật Camera && Nhận Diện")
        self._nut_bat_camera.clicked.connect(self._xu_ly_bat_tat_camera)
        hang_nut_camera.addWidget(self._nut_bat_camera)
        bo_cuc_camera.addLayout(hang_nut_camera)

        self._nhan_ket_qua_nhan_dien = QLabel("")
        self._nhan_ket_qua_nhan_dien.setWordWrap(True)
        self._nhan_ket_qua_nhan_dien.setObjectName("nhanKetQuaNhanDien")
        bo_cuc_camera.addWidget(self._nhan_ket_qua_nhan_dien)

        bo_cuc_ngang.addWidget(khung_camera, stretch=1)

        # ----- Bang diem danh -----
        khung_bang = QFrame()
        bo_cuc_bang = QVBoxLayout(khung_bang)
        bo_cuc_bang.addWidget(QLabel("Danh sách điểm danh buổi học:"))
        self._bang = QTableWidget(0, 5)
        self._bang.setHorizontalHeaderLabels(
            ["Mã SV", "Họ tên", "Trạng thái", "Phương thức", "Thời gian"]
        )
        self._bang.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._bang.horizontalHeader().setStretchLastSection(False)
        self._bang.horizontalHeader().setMinimumSectionSize(90)
        self._bang.setColumnWidth(2, 100)
        self._bang.setColumnWidth(3, 120)
        self._bang.setColumnWidth(4, 90)
        self._bang.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._bang.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        bo_cuc_bang.addWidget(self._bang, stretch=1)

        if co_quyen(self.phien_dang_nhap.vai_tro, QuyenHeThong.SUA_DIEM_DANH_THU_CONG):
            hang_thu_cong = QHBoxLayout()
            for nhan, trang_thai in (
                ("Có mặt", TrangThaiDiemDanh.CO_MAT),
                ("Đi muộn", TrangThaiDiemDanh.DI_MUON),
                ("Vắng", TrangThaiDiemDanh.VANG),
                ("Có phép", TrangThaiDiemDanh.CO_PHEP),
            ):
                nut = QPushButton(nhan)
                nut.clicked.connect(
                    lambda checked=False, ts=trang_thai: self._xu_ly_diem_danh_thu_cong(ts)
                )
                hang_thu_cong.addWidget(nut)
            bo_cuc_bang.addLayout(hang_thu_cong)

        bo_cuc_ngang.addWidget(khung_bang, stretch=1)
        bo_cuc.addLayout(bo_cuc_ngang, stretch=1)

    # ------------------------------------------------------------------
    def _nap_danh_sach_lop_mon(self) -> None:
        self._danh_sach_lop_mon = danh_muc.lay_danh_sach_lop_mon_hoc()
        self._o_lop_mon.blockSignals(True)
        self._o_lop_mon.clear()
        for lop_mon in self._danh_sach_lop_mon:
            self._o_lop_mon.addItem(f"{lop_mon.ma_lop_mon} - {lop_mon.ten_mon}", lop_mon.id)
        self._o_lop_mon.blockSignals(False)
        self._nap_danh_sach_buoi_hoc()

    def _nap_danh_sach_buoi_hoc(self) -> None:
        lop_mon_hoc_id = self._o_lop_mon.currentData()
        self._o_buoi_hoc.blockSignals(True)
        self._o_buoi_hoc.clear()
        if lop_mon_hoc_id is not None:
            for buoi in dv_diem_danh.lay_danh_sach_buoi_hoc(lop_mon_hoc_id=lop_mon_hoc_id):
                nhan = f"{buoi.ngay_hoc} ({buoi.gio_bat_dau}-{buoi.gio_ket_thuc}) - {_ten_trang_thai_buoi(buoi.trang_thai)}"
                self._o_buoi_hoc.addItem(nhan, buoi.id)
        self._o_buoi_hoc.blockSignals(False)
        self._xu_ly_doi_buoi_hoc()

    def _xu_ly_doi_buoi_hoc(self) -> None:
        self._buoi_hoc_dang_chon_id = self._o_buoi_hoc.currentData()
        self._nap_lai_bang_diem_danh()
        self._cap_nhat_trang_thai_hien_thi()

    def _cap_nhat_trang_thai_hien_thi(self) -> None:
        if self._buoi_hoc_dang_chon_id is None:
            self._nhan_trang_thai_buoi.setText("Chưa chọn buổi học.")
            return
        danh_sach = dv_diem_danh.lay_danh_sach_buoi_hoc(
            lop_mon_hoc_id=self._o_lop_mon.currentData()
        )
        buoi = next((b for b in danh_sach if b.id == self._buoi_hoc_dang_chon_id), None)
        if buoi:
            self._nhan_trang_thai_buoi.setText(
                f"Trạng thái buổi học: {_ten_trang_thai_buoi(buoi.trang_thai)} — "
                f"đã điểm danh {buoi.si_so_da_diem_danh} lượt."
            )

    def _nap_lai_bang_diem_danh(self) -> None:
        if self._buoi_hoc_dang_chon_id is None:
            self._bang.setRowCount(0)
            return
        danh_sach = dv_diem_danh.lay_danh_sach_diem_danh_theo_buoi_hoc(
            self._buoi_hoc_dang_chon_id
        )
        self._bang.setRowCount(len(danh_sach))
        for hang, dd in enumerate(danh_sach):
            thoi_gian_hien_thi = (
                dd.thoi_gian_diem_danh.strftime("%H:%M:%S")
                if isinstance(dd.thoi_gian_diem_danh, _datetime.datetime)
                else "-"
            )
            gia_tri_cac_cot = [
                dd.ma_sinh_vien,
                dd.ho_ten_sinh_vien,
                _ten_trang_thai_diem_danh(dd.trang_thai),
                dd.phuong_thuc,
                thoi_gian_hien_thi,
            ]
            for cot, gia_tri in enumerate(gia_tri_cac_cot):
                muc = QTableWidgetItem(str(gia_tri))
                muc.setData(Qt.ItemDataRole.UserRole, dd.sinh_vien_id)
                self._bang.setItem(hang, cot, muc)

    # ------------------------------------------------------------------
    def _xu_ly_tao_buoi_hoc(self) -> None:
        if not self._danh_sach_lop_mon:
            QMessageBox.information(
                self, "Chưa có lớp học phần", "Vui lòng tạo lớp học phần trước."
            )
            return
        hop_thoai = HopThoaiTaoBuoiHoc(self, self._danh_sach_lop_mon)
        if hop_thoai.exec() != QDialog.DialogCode.Accepted:
            return
        du_lieu = hop_thoai.lay_du_lieu_nhap()
        try:
            dv_diem_danh.tao_buoi_hoc(
                self.phien_dang_nhap.vai_tro,
                nguoi_thuc_hien_id=self.phien_dang_nhap.nguoi_dung_id,
                **du_lieu,
            )
        except LoiDiemDanh as loi:
            QMessageBox.warning(self, "Không thể tạo buổi học", str(loi))
            return
        self._nap_danh_sach_buoi_hoc()

    def _xu_ly_mo_diem_danh(self) -> None:
        if self._buoi_hoc_dang_chon_id is None:
            QMessageBox.information(self, "Chưa chọn", "Vui lòng chọn một buổi học.")
            return
        try:
            dv_diem_danh.mo_diem_danh_cho_buoi_hoc(
                self.phien_dang_nhap.vai_tro,
                self._buoi_hoc_dang_chon_id,
                nguoi_thuc_hien_id=self.phien_dang_nhap.nguoi_dung_id,
            )
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể mở điểm danh", str(loi))
            return
        self._nap_danh_sach_buoi_hoc()

    def _xu_ly_dong_diem_danh(self) -> None:
        if self._buoi_hoc_dang_chon_id is None:
            QMessageBox.information(self, "Chưa chọn", "Vui lòng chọn một buổi học.")
            return
        xac_nhan = QMessageBox.question(
            self,
            "Xác nhận đóng điểm danh",
            "Sau khi đóng, các sinh viên chưa điểm danh sẽ tự động bị đánh dấu VẮNG. Tiếp tục?",
        )
        if xac_nhan != QMessageBox.StandardButton.Yes:
            return
        try:
            dv_diem_danh.dong_diem_danh_cho_buoi_hoc(
                self.phien_dang_nhap.vai_tro,
                self._buoi_hoc_dang_chon_id,
                nguoi_thuc_hien_id=self.phien_dang_nhap.nguoi_dung_id,
            )
        except Exception as loi:  # noqa: BLE001
            QMessageBox.critical(self, "Không thể đóng điểm danh", str(loi))
            return
        self._tat_camera()
        self._nap_danh_sach_buoi_hoc()

    def _xu_ly_diem_danh_thu_cong(self, trang_thai: TrangThaiDiemDanh) -> None:
        if self._buoi_hoc_dang_chon_id is None:
            return
        hang = self._bang.currentRow()
        if hang < 0:
            QMessageBox.information(self, "Chưa chọn", "Vui lòng chọn một sinh viên trong bảng.")
            return
        sinh_vien_id = self._bang.item(hang, 0).data(Qt.ItemDataRole.UserRole)
        try:
            dv_diem_danh.diem_danh_thu_cong(
                self.phien_dang_nhap.vai_tro,
                self._buoi_hoc_dang_chon_id,
                sinh_vien_id,
                trang_thai,
                nguoi_thuc_hien_id=self.phien_dang_nhap.nguoi_dung_id,
            )
        except LoiDiemDanh as loi:
            QMessageBox.warning(self, "Không thể điểm danh", str(loi))
            return
        self._nap_lai_bang_diem_danh()
        self._cap_nhat_trang_thai_hien_thi()

    # ------------------------------------------------------------------
    # CAMERA & NHAN DIEN TU DONG
    # ------------------------------------------------------------------
    def _xu_ly_bat_tat_camera(self) -> None:
        if self._camera is not None:
            self._tat_camera()
            return
        if self._buoi_hoc_dang_chon_id is None:
            QMessageBox.information(self, "Chưa chọn", "Vui lòng chọn một buổi học trước.")
            return

        chi_so_camera = lay_cau_hinh().ai.chi_so_camera_mac_dinh
        camera = cv2.VideoCapture(chi_so_camera)
        if not camera.isOpened():
            QMessageBox.warning(
                self, "Không thể mở camera",
                f"Không thể mở camera tại chỉ số {chi_so_camera}. Kiểm tra webcam hoặc file .env.",
            )
            camera.release()
            return

        self._camera = camera
        self._bo_dem_khung_hinh.clear()
        self._bo_dinh_thoi_camera.start(33)
        self._bo_dinh_thoi_nhan_dien.start(CHU_KY_NHAN_DIEN_MILI_GIAY)
        self._nut_bat_camera.setText("Tắt Camera")

    def _tat_camera(self) -> None:
        self._bo_dinh_thoi_camera.stop()
        self._bo_dinh_thoi_nhan_dien.stop()
        if self._camera is not None:
            self._camera.release()
            self._camera = None
        self._nhan_camera.setText("Camera chưa được bật.")
        self._nhan_camera.setPixmap(QPixmap())
        self._nut_bat_camera.setText("Bật Camera && Nhận Diện")

    def _cap_nhat_khung_hinh(self) -> None:
        if self._camera is None:
            return
        doc_thanh_cong, khung_hinh = self._camera.read()
        if not doc_thanh_cong:
            return
        self._bo_dem_khung_hinh.append(khung_hinh)
        khung_hinh_rgb = cv2.cvtColor(khung_hinh, cv2.COLOR_BGR2RGB)
        cao, rong, kenh = khung_hinh_rgb.shape
        anh_qt = QImage(khung_hinh_rgb.data, rong, cao, kenh * rong, QImage.Format.Format_RGB888)
        self._nhan_camera.setPixmap(
            QPixmap.fromImage(anh_qt).scaled(
                self._nhan_camera.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def _thu_diem_danh_tu_dong(self) -> None:
        if self._buoi_hoc_dang_chon_id is None or len(self._bo_dem_khung_hinh) == 0:
            return
        nguong = lay_cau_hinh().ai.nguong_do_tuong_dong
        try:
            ket_qua = dv_diem_danh.diem_danh_bang_khuon_mat(
                buoi_hoc_id=self._buoi_hoc_dang_chon_id,
                danh_sach_khung_hinh_gan_nhat=list(self._bo_dem_khung_hinh),
                nguong_do_tuong_dong=nguong,
                nguoi_thuc_hien_id=self.phien_dang_nhap.nguoi_dung_id,
            )
        except Exception as loi:  # noqa: BLE001
            _bo_ghi_log.exception("Loi khi thu diem danh bang khuon mat")
            self._cap_nhat_nhan_ket_qua(f"Lỗi hệ thống: {loi}", thanh_cong=False)
            return

        self._cap_nhat_nhan_ket_qua(ket_qua.thong_bao, thanh_cong=ket_qua.thanh_cong)
        if ket_qua.thanh_cong:
            self._nap_lai_bang_diem_danh()
            self._cap_nhat_trang_thai_hien_thi()

    def _cap_nhat_nhan_ket_qua(self, noi_dung: str, thanh_cong: bool) -> None:
        """Cap nhat nhan ket qua nhan dien, doi mau nen theo trang thai thanh cong/that bai."""
        self._nhan_ket_qua_nhan_dien.setText(noi_dung)
        self._nhan_ket_qua_nhan_dien.setProperty(
            "trangThai", "thanhCong" if thanh_cong else "thatBai"
        )
        self._nhan_ket_qua_nhan_dien.style().unpolish(self._nhan_ket_qua_nhan_dien)
        self._nhan_ket_qua_nhan_dien.style().polish(self._nhan_ket_qua_nhan_dien)

    def don_dep_truoc_khi_dong(self) -> None:
        """Duoc CuaSoChinh goi truoc khi dong ung dung, dam bao giai phong camera."""
        self._tat_camera()


def _ten_trang_thai_buoi(trang_thai: str) -> str:
    bang = {
        "CHUA_BAT_DAU": "Chưa bắt đầu",
        "DANG_DIEM_DANH": "Đang điểm danh",
        "DA_KET_THUC": "Đã kết thúc",
    }
    return bang.get(trang_thai, trang_thai)


def _ten_trang_thai_diem_danh(trang_thai: str) -> str:
    bang = {
        "CO_MAT": "Có mặt",
        "DI_MUON": "Đi muộn",
        "VANG": "Vắng",
        "CO_PHEP": "Có phép",
        "CHUA_DIEM_DANH": "Chưa điểm danh",
    }
    return bang.get(trang_thai, trang_thai)
