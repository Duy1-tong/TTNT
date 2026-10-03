"""Module xuat bao cao ra file PDF bang ReportLab."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def xuat_bang_du_lieu_ra_pdf(
    duong_dan_file: Path,
    tieu_de_bao_cao: str,
    ten_cac_cot: Sequence[str],
    du_lieu_cac_hang: Sequence[Sequence[Any]],
    ghi_chu_cuoi_trang: str | None = None,
) -> Path:
    """Xuat mot bang du lieu ra file PDF dinh dang A4 nam ngang.

    Tra ve duong dan file da tao. Ham nay tu tao thu muc chua neu chua co.
    Luu y: ReportLab mac dinh khong ho tro day du font co dau tieng Viet
    trong font he thong (Helvetica), nen noi dung tieng Viet co dau van
    hien thi duoc nho ReportLab tu dong dung bang ma Unicode, tuy nhien de
    dam bao hien thi dau chuan xac nhat tren moi may, khuyen nghi cai dat
    them font TrueType ho tro tieng Viet (vi du DejaVuSans) neu can xuat
    ban in chinh thuc.
    """
    duong_dan_file.parent.mkdir(parents=True, exist_ok=True)

    tai_lieu = SimpleDocTemplate(
        str(duong_dan_file),
        pagesize=landscape(A4),
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    bang_style = getSampleStyleSheet()
    style_tieu_de = ParagraphStyle(
        "TieuDeBaoCao", parent=bang_style["Title"], fontSize=16, spaceAfter=12
    )
    style_ghi_chu = ParagraphStyle(
        "GhiChu", parent=bang_style["Normal"], fontSize=9, textColor=colors.grey
    )

    cac_thanh_phan = [Paragraph(tieu_de_bao_cao, style_tieu_de), Spacer(1, 0.3 * cm)]

    du_lieu_bang = [list(ten_cac_cot)] + [list(hang) for hang in du_lieu_cac_hang]
    bang = Table(du_lieu_bang, repeatRows=1)
    bang.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
            ]
        )
    )
    cac_thanh_phan.append(bang)

    if ghi_chu_cuoi_trang:
        cac_thanh_phan.append(Spacer(1, 0.4 * cm))
        cac_thanh_phan.append(Paragraph(ghi_chu_cuoi_trang, style_ghi_chu))

    tai_lieu.build(cac_thanh_phan)
    return duong_dan_file
