# Co so du lieu — Huong dan import bang XAMPP / phpMyAdmin

Du an nay **chi su dung MySQL/MariaDB thong qua XAMPP**. Khong su dung SQLite.

## Cach 1 — Import thu cong bang phpMyAdmin (khuyen nghi cho sinh vien)

1. Mo **XAMPP Control Panel**.
2. Nhan **Start** o dong `Apache`.
3. Nhan **Start** o dong `MySQL`.
4. Mo trinh duyet, truy cap: `http://localhost/phpmyadmin`
5. Chon tab **Databases**, tao moi database ten `diem_danh_khuon_mat`
   (collation `utf8mb4_unicode_ci`) — hoac bo qua buoc nay vi `schema.sql`
   tu tao database neu chua co.
6. Chon database `diem_danh_khuon_mat` (neu da tao) hoac o trang chu,
   chon tab **Import**.
7. Chon file `database/schema.sql` → nhan **Go / Thuc hien**.
8. Lap lai buoc Import voi file `database/du_lieu_mau.sql` de nap du lieu mau
   (tai khoan Admin, Giang vien, Sinh vien mau).
9. Kiem tra ben trai da xuat hien du 14 bang: `nguoi_dung, khoa, lop_hoc,
   giang_vien, sinh_vien, mon_hoc, lop_mon_hoc, sinh_vien_lop, buoi_hoc,
   diem_danh, khuon_mat, camera, nhat_ky_he_thong, cau_hinh`.
10. Mo file `.env` (sao chep tu `.env.example`) va cau hinh dung theo
    tai khoan MySQL cua ban (mac dinh XAMPP la `root` / mat khau rong).
11. Chay chuong trinh: `python run.py`

## Cach 2 — Tu dong hoa bang script Python

Neu khong muon thao tac tay tren phpMyAdmin, chi can chay:

```bash
python cai_dat.py
```

Script se tu kiem tra XAMPP/MySQL dang chay, tu tao database
`diem_danh_khuon_mat` (neu chua co), tao toan bo bang va nap du lieu mau
tuong duong voi hai file SQL trong thu muc nay.

## Cau truc file

| File               | Noi dung                                            |
|--------------------|------------------------------------------------------|
| `schema.sql`       | Tao database va toan bo 14 bang, khoa chinh, khoa ngoai, rang buoc duy nhat, chi muc |
| `du_lieu_mau.sql`  | Du lieu mau: 3 tai khoan (Admin/Giang vien/Sinh vien), khoa, lop, mon hoc, buoi hoc... |

## Luu y quan trong

- File `schema.sql` va `du_lieu_mau.sql` **khong chua du lieu ca nhan that**,
  chi la du lieu minh hoa cho muc dich hoc tap.
- Mat khau mau da duoc **bam bang bcrypt**, khong luu dang van ban ro.
- Khong dua database that (ban `.sql` export tu du lieu thuc te) vao Git
  hoac file nen ZIP nop bai.
