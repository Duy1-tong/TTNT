"""
Module tien ich bao mat: bam/kiem tra mat khau, ma hoa embedding khuon mat.

- Mat khau: bam bang bcrypt, khong bao gio luu/so sanh dang van ban ro.
- Embedding khuon mat: ma hoa doi xung (XOR + khoa dan xuat tu .env) truoc
  khi ghi xuong CSDL, giai ma khi doc ra de tinh toan cosine similarity.
  Day la lop bao ve bo sung; ban than embedding da la du lieu sinh trac hoc
  nhay cam nen KHONG duoc de lo qua log hay giao dien.
"""

from __future__ import annotations

import base64
import hashlib
import logging
import secrets

import bcrypt

from app.cau_hinh.cai_dat import lay_cau_hinh

_bo_ghi_log = logging.getLogger(__name__)

_SO_VONG_BAM_BCRYPT = 12


def bam_mat_khau(mat_khau_ro: str) -> str:
    """Bam mat khau bang bcrypt, tra ve chuoi hash de luu vao CSDL."""
    if not mat_khau_ro:
        raise ValueError("Mat khau khong duoc de trong.")
    muoi = bcrypt.gensalt(rounds=_SO_VONG_BAM_BCRYPT)
    bam = bcrypt.hashpw(mat_khau_ro.encode("utf-8"), muoi)
    return bam.decode("utf-8")


def kiem_tra_mat_khau(mat_khau_ro: str, mat_khau_bam: str) -> bool:
    """So sanh mat khau nguoi dung nhap voi mat khau da bam luu trong CSDL."""
    if not mat_khau_ro or not mat_khau_bam:
        return False
    try:
        return bcrypt.checkpw(mat_khau_ro.encode("utf-8"), mat_khau_bam.encode("utf-8"))
    except ValueError:
        # Chuoi hash khong dung dinh dang bcrypt (du lieu hong hoac cu).
        _bo_ghi_log.warning("Dinh dang mat khau bam khong hop le khi kiem tra.")
        return False


def kiem_tra_do_manh_mat_khau(mat_khau: str) -> tuple[bool, str]:
    """Kiem tra mat khau co du manh khong: toi thieu 8 ky tu, co chu hoa,
    chu thuong, so va ky tu dac biet.
    """
    if len(mat_khau) < 8:
        return False, "Mat khau phai co it nhat 8 ky tu."
    if not any(ky_tu.isupper() for ky_tu in mat_khau):
        return False, "Mat khau phai co it nhat mot chu hoa."
    if not any(ky_tu.islower() for ky_tu in mat_khau):
        return False, "Mat khau phai co it nhat mot chu thuong."
    if not any(ky_tu.isdigit() for ky_tu in mat_khau):
        return False, "Mat khau phai co it nhat mot chu so."
    ky_tu_dac_biet = set("!@#$%^&*()-_=+[]{};:,.<>?/\\|~`")
    if not any(ky_tu in ky_tu_dac_biet for ky_tu in mat_khau):
        return False, "Mat khau phai co it nhat mot ky tu dac biet (vi du: @, #, $...)."
    return True, "Mat khau du manh."


def _lay_khoa_ma_hoa() -> bytes:
    """Lay (hoac dan xuat) khoa dung de ma hoa embedding khuon mat.

    Neu nguoi dung chua cau hinh KHOA_BI_MAT_EMBEDDING trong .env, he thong
    se dan xuat mot khoa co dinh tu ten database de dam bao tinh nhat quan
    trong moi trong hoc tap/demo (khuyen nghi nguoi dung tu dat khoa rieng
    khi trien khai thuc te).
    """
    cau_hinh = lay_cau_hinh()
    khoa_cau_hinh = cau_hinh.bao_mat.khoa_bi_mat_embedding
    if khoa_cau_hinh:
        nguon_khoa = khoa_cau_hinh
    else:
        nguon_khoa = f"khoa-mac-dinh::{cau_hinh.co_so_du_lieu.ten_co_so_du_lieu}"
    return hashlib.sha256(nguon_khoa.encode("utf-8")).digest()


def ma_hoa_du_lieu_nhi_phan(du_lieu_goc: bytes) -> bytes:
    """Ma hoa du lieu nhi phan (vi du embedding khuon mat) bang XOR-stream
    dan xuat tu khoa bi mat, ket hop voi mot vector khoi tao (IV) ngau nhien.

    Dinh dang dau ra: [16 byte IV] + [du lieu da ma hoa].
    """
    khoa = _lay_khoa_ma_hoa()
    vector_khoi_tao = secrets.token_bytes(16)
    dong_khoa = _sinh_dong_khoa(khoa, vector_khoi_tao, len(du_lieu_goc))
    du_lieu_ma_hoa = bytes(a ^ b for a, b in zip(du_lieu_goc, dong_khoa))
    return vector_khoi_tao + du_lieu_ma_hoa


def giai_ma_du_lieu_nhi_phan(du_lieu_da_ma_hoa: bytes) -> bytes:
    """Giai ma du lieu duoc tao boi ham `ma_hoa_du_lieu_nhi_phan`."""
    if len(du_lieu_da_ma_hoa) < 16:
        raise ValueError("Du lieu ma hoa khong hop le (thieu vector khoi tao).")
    vector_khoi_tao, du_lieu_ma_hoa = du_lieu_da_ma_hoa[:16], du_lieu_da_ma_hoa[16:]
    khoa = _lay_khoa_ma_hoa()
    dong_khoa = _sinh_dong_khoa(khoa, vector_khoi_tao, len(du_lieu_ma_hoa))
    return bytes(a ^ b for a, b in zip(du_lieu_ma_hoa, dong_khoa))


def _sinh_dong_khoa(khoa: bytes, vector_khoi_tao: bytes, do_dai: int) -> bytes:
    """Sinh mot dong khoa (keystream) co do dai `do_dai` bang cach bam lien
    tiep SHA-256(khoa + vector_khoi_tao + bo_dem) — tuong tu che do CTR don gian.
    """
    dong_khoa = bytearray()
    bo_dem = 0
    while len(dong_khoa) < do_dai:
        khoi = hashlib.sha256(khoa + vector_khoi_tao + bo_dem.to_bytes(4, "big")).digest()
        dong_khoa.extend(khoi)
        bo_dem += 1
    return bytes(dong_khoa[:do_dai])


def chuyen_mang_so_thanh_base64(du_lieu: bytes) -> str:
    """Chuyen du lieu nhi phan sang chuoi base64 (dung khi can hien thi/ghi log an toan)."""
    return base64.b64encode(du_lieu).decode("ascii")
