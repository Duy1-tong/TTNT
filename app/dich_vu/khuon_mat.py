"""
Dich vu Khuon Mat: dang ky, quan ly va truy van embedding khuon mat cua sinh vien.

Day la tang service DUY NHAT duoc phep doc/ghi bang `khuon_mat`. Giao dien
(PySide6) chi duoc gui anh (numpy array) toi day, khong tu tinh embedding
hay tu ma hoa/giai ma du lieu sinh trac hoc.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

from app.co_so_du_lieu.ket_noi import mo_phien_lam_viec
from app.dich_vu.nhat_ky import ghi_nhat_ky
from app.dich_vu.phan_quyen import QuyenHeThong, yeu_cau_quyen
from app.mo_hinh.khuon_mat import KhuonMat
from app.mo_hinh.sinh_vien import SinhVien
from app.tien_ich.bao_mat import giai_ma_du_lieu_nhi_phan, ma_hoa_du_lieu_nhi_phan
from app.tri_tue_nhan_tao.nhan_dien_khuon_mat import BoNhanDienKhuonMat

_bo_ghi_log = logging.getLogger(__name__)

# Bo nhan dien duoc khoi tao MOT LAN va dung chung cho toan ung dung, tranh
# nap lai model AI (rat ton thoi gian) moi khi goi ham.
_bo_nhan_dien_dung_chung: BoNhanDienKhuonMat | None = None


class LoiDangKyKhuonMat(Exception):
    """Loi nghiep vu lien quan den dang ky/nhan dien khuon mat."""


@dataclass
class ThongTinKhuonMatDaDangKy:
    """DTO the hien mot ban ghi embedding khuon mat da dang ky."""

    id: int
    sinh_vien_id: int
    mo_hinh: str
    phien_ban_mo_hinh: str


def lay_bo_nhan_dien() -> BoNhanDienKhuonMat:
    """Tra ve instance dung chung cua BoNhanDienKhuonMat (khoi tao mot lan duy nhat)."""
    global _bo_nhan_dien_dung_chung
    if _bo_nhan_dien_dung_chung is None:
        _bo_nhan_dien_dung_chung = BoNhanDienKhuonMat()
    return _bo_nhan_dien_dung_chung


def _serialize_embedding(embedding: np.ndarray) -> bytes:
    """Chuyen vector numpy sang bytes roi ma hoa truoc khi luu CSDL."""
    du_lieu_tho = embedding.astype(np.float32).tobytes()
    return ma_hoa_du_lieu_nhi_phan(du_lieu_tho)


def _deserialize_embedding(du_lieu_da_ma_hoa: bytes) -> np.ndarray:
    """Giai ma bytes tu CSDL va chuyen lai thanh vector numpy float32."""
    du_lieu_tho = giai_ma_du_lieu_nhi_phan(du_lieu_da_ma_hoa)
    return np.frombuffer(du_lieu_tho, dtype=np.float32)


def dang_ky_khuon_mat_tu_anh(
    vai_tro_nguoi_thuc_hien: str,
    sinh_vien_id: int,
    anh_bgr: np.ndarray,
    nguoi_thuc_hien_id: int | None = None,
) -> ThongTinKhuonMatDaDangKy:
    """Trich xuat embedding tu mot anh chup khuon mat va luu vao CSDL cho sinh vien.

    Phat sinh LoiDangKyKhuonMat neu khong phat hien duoc khuon mat trong anh.
    """
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.DANG_KY_KHUON_MAT)

    bo_nhan_dien = lay_bo_nhan_dien()
    ket_qua = bo_nhan_dien.trich_xuat_embedding_tu_anh(anh_bgr)
    if not ket_qua.tim_thay_khuon_mat or ket_qua.embedding is None:
        raise LoiDangKyKhuonMat(ket_qua.thong_bao)

    with mo_phien_lam_viec() as phien:
        sinh_vien = phien.get(SinhVien, sinh_vien_id)
        if sinh_vien is None:
            raise LoiDangKyKhuonMat("Khong tim thay sinh vien.")

        ban_ghi_moi = KhuonMat(
            sinh_vien_id=sinh_vien_id,
            embedding=_serialize_embedding(ket_qua.embedding),
            mo_hinh=bo_nhan_dien.bo_tao_embedding.ten_mo_hinh,
            phien_ban_mo_hinh=bo_nhan_dien.bo_tao_embedding.phien_ban_mo_hinh,
        )
        phien.add(ban_ghi_moi)
        phien.commit()

        ghi_nhat_ky(
            hanh_dong="DANG_KY_KHUON_MAT",
            nguoi_dung_id=nguoi_thuc_hien_id,
            doi_tuong="khuon_mat",
            doi_tuong_id=ban_ghi_moi.id,
            noi_dung=(
                f"Dang ky khuon mat cho sinh vien {sinh_vien.ma_sinh_vien} "
                f"bang mo hinh '{ban_ghi_moi.mo_hinh}'."
            ),
        )

        return ThongTinKhuonMatDaDangKy(
            id=ban_ghi_moi.id,
            sinh_vien_id=sinh_vien_id,
            mo_hinh=ban_ghi_moi.mo_hinh,
            phien_ban_mo_hinh=ban_ghi_moi.phien_ban_mo_hinh,
        )


def lay_danh_sach_khuon_mat_cua_sinh_vien(sinh_vien_id: int) -> list[ThongTinKhuonMatDaDangKy]:
    """Lay danh sach embedding da dang ky cua mot sinh vien (khong bao gom du lieu tho)."""
    with mo_phien_lam_viec() as phien:
        danh_sach = phien.query(KhuonMat).filter_by(sinh_vien_id=sinh_vien_id).all()
        return [
            ThongTinKhuonMatDaDangKy(
                id=b.id, sinh_vien_id=b.sinh_vien_id, mo_hinh=b.mo_hinh,
                phien_ban_mo_hinh=b.phien_ban_mo_hinh,
            )
            for b in danh_sach
        ]


def xoa_khuon_mat(
    vai_tro_nguoi_thuc_hien: str, khuon_mat_id: int, nguoi_thuc_hien_id: int | None = None
) -> None:
    """Xoa mot ban ghi embedding khuon mat da dang ky (vi du dang ky nham/muon cap nhat lai)."""
    yeu_cau_quyen(vai_tro_nguoi_thuc_hien, QuyenHeThong.DANG_KY_KHUON_MAT)
    with mo_phien_lam_viec() as phien:
        ban_ghi = phien.get(KhuonMat, khuon_mat_id)
        if ban_ghi is None:
            raise LoiDangKyKhuonMat("Khong tim thay du lieu khuon mat can xoa.")
        sinh_vien_id = ban_ghi.sinh_vien_id
        phien.delete(ban_ghi)
        phien.commit()

        ghi_nhat_ky(
            hanh_dong="XOA_KHUON_MAT",
            nguoi_dung_id=nguoi_thuc_hien_id,
            doi_tuong="khuon_mat",
            doi_tuong_id=khuon_mat_id,
            noi_dung=f"Xoa du lieu khuon mat cua sinh vien id={sinh_vien_id}.",
        )


def lay_toan_bo_embedding_de_nhan_dien(
    lop_mon_hoc_id: int | None = None,
) -> list[tuple[int, np.ndarray]]:
    """Lay toan bo (sinh_vien_id, vector_embedding) da giai ma, san sang de so sanh.

    Neu `lop_mon_hoc_id` duoc chi dinh, chi lay embedding cua cac sinh vien
    dang dang ky hoc lop hoc phan do (giup thu hep pham vi tim kiem khi
    diem danh, tang toc do va giam nham lan giua cac lop khac nhau).
    """
    from app.mo_hinh.sinh_vien_lop import SinhVienLop, TrangThaiDangKy

    with mo_phien_lam_viec() as phien:
        truy_van = phien.query(KhuonMat)
        if lop_mon_hoc_id is not None:
            cac_sinh_vien_id = [
                hang[0]
                for hang in phien.query(SinhVienLop.sinh_vien_id)
                .filter(
                    SinhVienLop.lop_mon_hoc_id == lop_mon_hoc_id,
                    SinhVienLop.trang_thai == TrangThaiDangKy.DANG_HOC,
                )
                .all()
            ]
            truy_van = truy_van.filter(KhuonMat.sinh_vien_id.in_(cac_sinh_vien_id))

        ket_qua: list[tuple[int, np.ndarray]] = []
        for ban_ghi in truy_van.all():
            try:
                vector = _deserialize_embedding(ban_ghi.embedding)
                ket_qua.append((ban_ghi.sinh_vien_id, vector))
            except Exception as loi:  # noqa: BLE001
                _bo_ghi_log.error(
                    "Khong the giai ma embedding id=%s: %s", ban_ghi.id, loi
                )
        return ket_qua
