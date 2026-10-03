"""
Goi Tri Tue Nhan Tao: phat hien khuon mat, tao embedding, so sanh, kiem tra nguoi that.

Kien truc uu tien:
    OpenCV -> YOLO (phat hien) -> Face Alignment -> InsightFace/ArcFace (embedding)
    -> Cosine Similarity -> Sinh vien

Neu YOLO/InsightFace khong the cai dat hoac khong tuong thich voi may nguoi
dung, he thong TU DONG fallback sang:
    OpenCV Haar Cascade / DNN (phat hien) -> Vector dac trung HOG+Histogram (embedding)
    -> Cosine Similarity -> Sinh vien

Co che fallback dam bao chuong trinh luon chay duoc, khong crash, du may
khong cai duoc thu vien AI nang cao.
"""
