"""
Module tao vector dac trung (embedding) tu anh khuon mat da duoc cat.

Uu tien su dung InsightFace/ArcFace (do chinh xac cao). Neu `insightface`
hoac `onnxruntime` chua duoc cai dat / khong tuong thich voi may nguoi
dung, tu dong fallback sang phuong phap trich xuat dac trung bang OpenCV
(HOG + histogram mau da chuan hoa), van cho phep he thong hoat dong day
du chuc nang o muc do chap nhan duoc trong moi truong khong co GPU/thu
vien AI nang cao.
"""

from __future__ import annotations

import logging

import cv2
import numpy as np

from app.cau_hinh.cai_dat import lay_cau_hinh

_bo_ghi_log = logging.getLogger(__name__)

KICH_THUOC_ANH_CHUAN_HOA = (112, 112)
PHIEN_BAN_MO_HINH_INSIGHTFACE = "buffalo_l"
PHIEN_BAN_MO_HINH_DU_PHONG = "hog_histogram_v1"


class BoTaoEmbedding:
    """Sinh vector dac trung khuon mat, tu dong chon InsightFace hoac fallback OpenCV."""

    def __init__(self) -> None:
        self._cau_hinh = lay_cau_hinh()
        self._ung_dung_insightface = None
        self._bo_mo_ta_hog = cv2.HOGDescriptor(
            _winSize=(64, 64),
            _blockSize=(16, 16),
            _blockStride=(8, 8),
            _cellSize=(8, 8),
            _nbins=9,
        )
        self.dang_dung_insightface = self._thu_nap_insightface()
        self.ten_mo_hinh = "insightface_arcface" if self.dang_dung_insightface else "opencv_fallback"
        self.phien_ban_mo_hinh = (
            PHIEN_BAN_MO_HINH_INSIGHTFACE if self.dang_dung_insightface else PHIEN_BAN_MO_HINH_DU_PHONG
        )

    def _thu_nap_insightface(self) -> bool:
        thu_muc_model = self._cau_hinh.duong_dan_tuyet_doi(self._cau_hinh.ai.thu_muc_model)
        try:
            from insightface.app import FaceAnalysis  # import tre

            self._ung_dung_insightface = FaceAnalysis(
                name=PHIEN_BAN_MO_HINH_INSIGHTFACE,
                root=str(thu_muc_model),
                providers=["CPUExecutionProvider"],
            )
            self._ung_dung_insightface.prepare(ctx_id=-1, det_size=(320, 320))
            _bo_ghi_log.info("Da nap InsightFace (%s) de tao embedding.", PHIEN_BAN_MO_HINH_INSIGHTFACE)
            return True
        except ImportError:
            _bo_ghi_log.warning(
                "Thu vien 'insightface' hoac 'onnxruntime' chua duoc cai dat. "
                "Chay: pip install insightface onnxruntime. "
                "He thong se dung phuong phap trich xuat dac trung du phong (OpenCV)."
            )
            return False
        except Exception as loi:  # noqa: BLE001
            _bo_ghi_log.warning(
                "Khong the khoi tao InsightFace (%s). Dung phuong phap du phong OpenCV.", loi
            )
            return False

    def tao_embedding(self, anh_khuon_mat_bgr: np.ndarray) -> np.ndarray | None:
        """Tao embedding tu khuon mat.

        Neu InsightFace khong duoc khoi tao ngay tu dau,
        he thong moi su dung phuong phap du phong OpenCV.

        Neu InsightFace dang hoat dong nhung khong tao duoc
        embedding tu anh hien tai, khong tu dong chuyen
        sang fallback de tranh thay doi backend nhan dien
        mot cach khong kiem soat.
        """
        if anh_khuon_mat_bgr is None or anh_khuon_mat_bgr.size == 0:
            return None

        if not self.dang_dung_insightface:
            _bo_ghi_log.warning(
                "InsightFace khong kha dung. "
                "Dang su dung phuong phap nhan dien du phong OpenCV."
            )

            return self._tao_embedding_du_phong(
                anh_khuon_mat_bgr
            )

        embedding = self._tao_embedding_insightface(
            anh_khuon_mat_bgr
        )

        if embedding is None:
            _bo_ghi_log.warning(
                "InsightFace khong tao duoc embedding "
                "cho anh khuon mat hien tai. "
                "Khong tu dong chuyen sang fallback."
            )
            return None

        return embedding

    def _tao_embedding_insightface(self, anh_khuon_mat_bgr: np.ndarray) -> np.ndarray | None:
        try:
            cac_khuon_mat = self._ung_dung_insightface.get(anh_khuon_mat_bgr)
            if not cac_khuon_mat:
                return None
            khuon_mat_lon_nhat = max(
                cac_khuon_mat,
                key=lambda k: (k.bbox[2] - k.bbox[0]) * (k.bbox[3] - k.bbox[1]),
            )
            vector = khuon_mat_lon_nhat.normed_embedding.astype(np.float32)
            return vector
        except Exception as loi:  # noqa: BLE001
            _bo_ghi_log.error("Loi khi tao embedding bang InsightFace: %s", loi)
            return None

    def _tao_embedding_du_phong(self, anh_khuon_mat_bgr: np.ndarray) -> np.ndarray:
        """Trich xuat dac trung bang HOG + histogram mau, chuan hoa ve vector don vi.

        Day KHONG phai la embedding sinh trac hoc chinh xac cao nhu ArcFace,
        nhung du de phan biet cac khuon mat khac nhau trong pham vi mot lop
        hoc/mot khoa trong dieu kien khong the cai InsightFace.
        """
        anh_chuan_hoa = cv2.resize(anh_khuon_mat_bgr, KICH_THUOC_ANH_CHUAN_HOA)
        anh_xam = cv2.cvtColor(anh_chuan_hoa, cv2.COLOR_BGR2GRAY)
        anh_xam = cv2.equalizeHist(anh_xam)

        anh_hog = cv2.resize(anh_xam, (64, 64))
        vector_hog = self._bo_mo_ta_hog.compute(anh_hog)
        vector_hog = vector_hog.flatten() if vector_hog is not None else np.zeros(1764, dtype=np.float32)

        histogram_mau = cv2.calcHist(
            [anh_chuan_hoa], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256]
        )
        histogram_mau = cv2.normalize(histogram_mau, histogram_mau).flatten()

        vector_ket_hop = np.concatenate([vector_hog, histogram_mau]).astype(np.float32)
        chuan_l2 = np.linalg.norm(vector_ket_hop)
        if chuan_l2 > 0:
            vector_ket_hop = vector_ket_hop / chuan_l2
        return vector_ket_hop
