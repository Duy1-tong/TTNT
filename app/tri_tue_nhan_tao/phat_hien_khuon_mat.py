"""
Module phat hien khuon mat trong anh.

Uu tien su dung YOLO (thong qua thu vien `ultralytics`) neu co model phat
hien khuon mat duoc dat trong thu muc model. Neu `ultralytics` chua duoc
cai, khong co model, hoac qua trinh nap model that bai, tu dong fallback
sang OpenCV DNN Face Detector (res10_300x300_ssd) va cuoi cung la Haar
Cascade (luon co san trong moi ban cai OpenCV) de dam bao chuong trinh
khong bao gio crash vi thieu thu vien AI nang cao.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from app.cau_hinh.cai_dat import lay_cau_hinh

_bo_ghi_log = logging.getLogger(__name__)


@dataclass
class HopGioiHanKhuonMat:
    """Toa do hop gioi han (bounding box) cua mot khuon mat duoc phat hien."""

    x: int
    y: int
    rong: int
    cao: int
    do_tin_cay: float

    def cat_anh(self, anh_goc: np.ndarray, le_them: float = 0.15) -> np.ndarray:
        """Cat vung khuon mat ra khoi anh goc, co them mot khoang le nho xung quanh."""
        chieu_cao_anh, chieu_rong_anh = anh_goc.shape[:2]
        le_x = int(self.rong * le_them)
        le_y = int(self.cao * le_them)
        x1 = max(0, self.x - le_x)
        y1 = max(0, self.y - le_y)
        x2 = min(chieu_rong_anh, self.x + self.rong + le_x)
        y2 = min(chieu_cao_anh, self.y + self.cao + le_y)
        return anh_goc[y1:y2, x1:x2]


class BoPhatHienKhuonMat:
    """Bo phat hien khuon mat voi co che fallback ba lop: YOLO -> DNN -> Haar Cascade."""

    def __init__(self) -> None:
        self._cau_hinh = lay_cau_hinh()
        self._mo_hinh_yolo = None
        self._mang_dnn = None
        self._bo_phan_loai_haar: cv2.CascadeClassifier | None = None
        self.ten_phuong_phap_dang_dung = "KHONG_XAC_DINH"
        self._khoi_tao_mo_hinh()

    # ------------------------------------------------------------------
    # Khoi tao / nap model theo thu tu uu tien
    # ------------------------------------------------------------------
    def _khoi_tao_mo_hinh(self) -> None:
        if self._thu_nap_yolo():
            self.ten_phuong_phap_dang_dung = "YOLO"
            return
        if self._thu_nap_dnn_opencv():
            self.ten_phuong_phap_dang_dung = "OPENCV_DNN"
            return
        self._nap_haar_cascade()
        self.ten_phuong_phap_dang_dung = "OPENCV_HAAR_CASCADE"

    def _thu_nap_yolo(self) -> bool:
        """Thu nap model YOLO phat hien khuon mat (vi du yolov8n-face.pt)."""
        duong_dan_model = self._cau_hinh.duong_dan_tuyet_doi(
            f"{self._cau_hinh.ai.thu_muc_model}/yolov8n-face.pt"
        )
        if not duong_dan_model.exists():
            _bo_ghi_log.info(
                "Khong tim thay model YOLO tai %s, chuyen sang phuong an du phong.",
                duong_dan_model,
            )
            return False
        try:
            from ultralytics import YOLO  # import tre de tranh loi neu chua cai

            self._mo_hinh_yolo = YOLO(str(duong_dan_model))
            _bo_ghi_log.info("Da nap model YOLO phat hien khuon mat: %s", duong_dan_model)
            return True
        except ImportError:
            _bo_ghi_log.warning(
                "Thu vien 'ultralytics' chua duoc cai dat. "
                "Chay: pip install ultralytics. Dang chuyen sang phuong an du phong."
            )
            return False
        except Exception as loi:  # noqa: BLE001
            _bo_ghi_log.warning("Khong the nap model YOLO (%s). Dung phuong an du phong.", loi)
            return False

    def _thu_nap_dnn_opencv(self) -> bool:
        """Thu nap OpenCV DNN Face Detector (Caffe res10_300x300_ssd)."""
        thu_muc_model = self._cau_hinh.duong_dan_tuyet_doi(self._cau_hinh.ai.thu_muc_model)
        duong_dan_prototxt = thu_muc_model / "deploy.prototxt"
        duong_dan_trong_so = thu_muc_model / "res10_300x300_ssd_iter_140000.caffemodel"
        if not (duong_dan_prototxt.exists() and duong_dan_trong_so.exists()):
            _bo_ghi_log.info(
                "Khong tim thay model OpenCV DNN tai %s, chuyen sang Haar Cascade.",
                thu_muc_model,
            )
            return False
        try:
            self._mang_dnn = cv2.dnn.readNetFromCaffe(
                str(duong_dan_prototxt), str(duong_dan_trong_so)
            )
            _bo_ghi_log.info("Da nap OpenCV DNN Face Detector.")
            return True
        except Exception as loi:  # noqa: BLE001
            _bo_ghi_log.warning("Khong the nap OpenCV DNN Face Detector (%s).", loi)
            return False

    def _nap_haar_cascade(self) -> None:
        """Nap Haar Cascade — phuong an du phong cuoi cung, luon co san trong OpenCV."""
        duong_dan_haar = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
        self._bo_phan_loai_haar = cv2.CascadeClassifier(str(duong_dan_haar))
        if self._bo_phan_loai_haar.empty():
            raise RuntimeError(
                "Khong the nap Haar Cascade mac dinh cua OpenCV. "
                "Vui long kiem tra lai qua trinh cai dat opencv-python."
            )
        _bo_ghi_log.info("Da nap Haar Cascade lam phuong an phat hien khuon mat du phong.")

    # ------------------------------------------------------------------
    # API cong khai
    # ------------------------------------------------------------------
    def phat_hien(
        self, anh_bgr: np.ndarray, nguong_tin_cay: float = 0.5
    ) -> list[HopGioiHanKhuonMat]:
        """Phat hien tat ca khuon mat trong anh (dinh dang BGR nhu OpenCV doc)."""
        if anh_bgr is None or anh_bgr.size == 0:
            return []
        if self._mo_hinh_yolo is not None:
            return self._phat_hien_bang_yolo(anh_bgr, nguong_tin_cay)
        if self._mang_dnn is not None:
            return self._phat_hien_bang_dnn(anh_bgr, nguong_tin_cay)
        return self._phat_hien_bang_haar(anh_bgr)

    def _phat_hien_bang_yolo(
        self, anh_bgr: np.ndarray, nguong_tin_cay: float
    ) -> list[HopGioiHanKhuonMat]:
        ket_qua = self._mo_hinh_yolo.predict(anh_bgr, verbose=False, conf=nguong_tin_cay)
        danh_sach_hop: list[HopGioiHanKhuonMat] = []
        for du_doan in ket_qua:
            for hop in du_doan.boxes:
                x1, y1, x2, y2 = (int(gia_tri) for gia_tri in hop.xyxy[0].tolist())
                do_tin_cay = float(hop.conf[0]) if hop.conf is not None else 0.0
                danh_sach_hop.append(
                    HopGioiHanKhuonMat(x=x1, y=y1, rong=x2 - x1, cao=y2 - y1, do_tin_cay=do_tin_cay)
                )
        return danh_sach_hop

    def _phat_hien_bang_dnn(
        self, anh_bgr: np.ndarray, nguong_tin_cay: float
    ) -> list[HopGioiHanKhuonMat]:
        chieu_cao, chieu_rong = anh_bgr.shape[:2]
        khoi_dau_vao = cv2.dnn.blobFromImage(
            cv2.resize(anh_bgr, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0)
        )
        self._mang_dnn.setInput(khoi_dau_vao)
        cac_du_doan = self._mang_dnn.forward()
        danh_sach_hop: list[HopGioiHanKhuonMat] = []
        for i in range(cac_du_doan.shape[2]):
            do_tin_cay = float(cac_du_doan[0, 0, i, 2])
            if do_tin_cay < nguong_tin_cay:
                continue
            hop = cac_du_doan[0, 0, i, 3:7] * np.array(
                [chieu_rong, chieu_cao, chieu_rong, chieu_cao]
            )
            x1, y1, x2, y2 = hop.astype(int)
            x1, y1 = max(0, x1), max(0, y1)
            danh_sach_hop.append(
                HopGioiHanKhuonMat(x=x1, y=y1, rong=x2 - x1, cao=y2 - y1, do_tin_cay=do_tin_cay)
            )
        return danh_sach_hop

    def _phat_hien_bang_haar(self, anh_bgr: np.ndarray) -> list[HopGioiHanKhuonMat]:
        anh_xam = cv2.cvtColor(anh_bgr, cv2.COLOR_BGR2GRAY)
        anh_xam = cv2.equalizeHist(anh_xam)
        cac_khuon_mat = self._bo_phan_loai_haar.detectMultiScale(
            anh_xam, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
        )
        return [
            HopGioiHanKhuonMat(x=int(x), y=int(y), rong=int(w), cao=int(h), do_tin_cay=0.99)
            for (x, y, w, h) in cac_khuon_mat
        ]
