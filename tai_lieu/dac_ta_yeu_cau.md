# Đặc Tả Yêu Cầu — Hệ Thống Điểm Danh Sinh Viên Bằng Khuôn Mặt

## 1. Giới thiệu

### 1.1. Mục đích
Xây dựng một phần mềm desktop chạy trên máy tính cá nhân, cho phép các
trường/khoa quản lý sinh viên, lớp học phần và thực hiện điểm danh tự động
bằng công nghệ nhận diện khuôn mặt (AI), thay thế cho việc điểm danh thủ
công bằng giấy hoặc gọi tên.

### 1.2. Phạm vi
Phần mềm phục vụ một cơ sở đào tạo (trường/khoa), gồm các nhóm chức năng:
quản lý danh mục (khoa, lớp, môn học), quản lý người dùng và phân quyền,
đăng ký khuôn mặt sinh viên, điểm danh bằng khuôn mặt/thủ công, báo cáo —
thống kê, và nhật ký hệ thống (audit log).

### 1.3. Đối tượng sử dụng (Actors)

| Vai trò | Mô tả | Quyền hạn chính |
|---|---|---|
| **ADMIN** (Quản trị viên) | Quản lý toàn bộ hệ thống | Toàn quyền: tài khoản, danh mục, cấu hình, xem mọi báo cáo/nhật ký |
| **GIANG_VIEN** (Giảng viên) | Phụ trách giảng dạy lớp học phần | Tạo buổi học, mở/đóng điểm danh, điểm danh thủ công, xem báo cáo lớp mình dạy |
| **SINH_VIEN** (Sinh viên) | Người học, đối tượng được điểm danh | Xem lịch sử điểm danh của bản thân, đổi mật khẩu |

## 2. Yêu cầu chức năng

### 2.1. Xác thực và bảo mật
- FR-01: Đăng nhập bằng tên đăng nhập/mật khẩu; mật khẩu được băm bằng bcrypt.
- FR-02: Tự động khóa tài khoản sau N lần đăng nhập sai liên tiếp (mặc định 5), tự mở khóa sau thời gian cấu hình (mặc định 15 phút).
- FR-03: Đổi mật khẩu, kiểm tra độ mạnh mật khẩu mới.
- FR-04: Phân quyền RBAC theo 3 vai trò, kiểm tra ở tầng Service (không chỉ ẩn nút giao diện).

### 2.2. Quản lý danh mục
- FR-05: Quản lý Khoa (thêm/xem).
- FR-06: Quản lý Lớp hành chính (thêm/xem/lọc theo khoa).
- FR-07: Quản lý Môn học (thêm/xem).
- FR-08: Quản lý Lớp học phần (thêm/xem, gán giảng viên phụ trách).
- FR-09: Đăng ký sinh viên vào lớp học phần (chống đăng ký trùng).

### 2.3. Quản lý sinh viên / giảng viên
- FR-10: Thêm/sửa/đổi trạng thái/xóa sinh viên. Không cho xóa vật lý sinh viên đã có lịch sử điểm danh (chỉ đổi trạng thái: Nghỉ học/Bảo lưu/Tốt nghiệp).
- FR-11: Tìm kiếm, lọc danh sách sinh viên theo lớp/từ khóa.
- FR-12: Thêm/sửa/xóa giảng viên.

### 2.4. Đăng ký khuôn mặt (sinh trắc học)
- FR-13: Chụp ảnh khuôn mặt qua webcam, trích xuất đặc trưng (embedding) và lưu vào CSDL ở dạng đã mã hóa.
- FR-14: Cho phép đăng ký nhiều mẫu khuôn mặt cho một sinh viên (tăng độ chính xác).
- FR-15: Xóa một mẫu khuôn mặt đã đăng ký.
- FR-16: Từ chối đăng ký nếu không phát hiện được khuôn mặt trong ảnh.

### 2.5. Điểm danh
- FR-17: Tạo buổi học cho một lớp học phần (ngày, giờ bắt đầu/kết thúc, phòng học).
- FR-18: Mở/đóng điểm danh cho một buổi học; chỉ điểm danh được trong thời gian đã mở.
- FR-19: Điểm danh tự động bằng khuôn mặt qua camera trực tiếp, có kiểm tra người thật (chống giả mạo bằng ảnh tĩnh).
- FR-20: Chống điểm danh trùng: mỗi sinh viên chỉ có một bản ghi điểm danh cho mỗi buổi học (ràng buộc UNIQUE ở CSDL).
- FR-21: Tự động phân loại "Có mặt"/"Đi muộn" dựa trên thời điểm điểm danh so với giờ bắt đầu.
- FR-22: Điểm danh thủ công / sửa kết quả điểm danh (dành cho Giảng viên, Admin).
- FR-23: Khi đóng điểm danh, tự động đánh dấu "Vắng" cho sinh viên đăng ký lớp nhưng chưa có bản ghi điểm danh.
- FR-24: Kiểm tra sinh viên có thuộc lớp học phần trước khi ghi nhận điểm danh.

### 2.6. Báo cáo
- FR-25: Thống kê điểm danh theo lớp học phần, theo khoảng thời gian (ngày/tháng/học kỳ tùy người dùng chọn).
- FR-26: Xem lịch sử điểm danh cá nhân (dành cho sinh viên).
- FR-27: Xuất báo cáo ra Excel (.xlsx) và PDF.

### 2.7. Nhật ký & Cấu hình
- FR-28: Ghi nhật ký (audit log) cho: đăng nhập/thất bại, đăng xuất, đổi mật khẩu, đăng ký/xóa khuôn mặt, điểm danh/sửa điểm danh, thêm/sửa/xóa danh mục, thay đổi cấu hình. Không bao giờ ghi mật khẩu.
- FR-29: Xem, lọc nhật ký hệ thống (chỉ Admin).
- FR-30: Cấu hình động: ngưỡng độ tương đồng khuôn mặt, số lần đăng nhập sai tối đa, thời gian khóa tài khoản, số phút tính đi muộn — chỉnh sửa được ngay khi ứng dụng đang chạy.
- FR-31: Quản lý tài khoản: tạo mới, khóa/mở khóa, đặt lại mật khẩu (chỉ Admin).

## 3. Yêu cầu phi chức năng

| Mã | Yêu cầu | Ghi chú |
|---|---|---|
| NFR-01 | Bảo mật mật khẩu | bcrypt, không lưu văn bản rõ |
| NFR-02 | Bảo vệ dữ liệu sinh trắc học | Embedding khuôn mặt được mã hóa trước khi lưu CSDL |
| NFR-03 | Chống SQL Injection | Toàn bộ truy vấn qua SQLAlchemy ORM, không nối chuỗi SQL thủ công |
| NFR-04 | Toàn vẹn dữ liệu | Khóa ngoại, ràng buộc duy nhất, transaction cho các thao tác nhiều bước |
| NFR-05 | Khả năng phục hồi khi AI nâng cao không khả dụng | Cơ chế fallback OpenCV khi thiếu InsightFace/YOLO/onnxruntime, không crash |
| NFR-06 | Khả năng phục hồi khi MySQL chưa sẵn sàng | Hiển thị hướng dẫn rõ ràng, không crash ứng dụng |
| NFR-07 | Giao diện tiếng Việt có dấu | 100% nhãn, thông báo hiển thị bằng tiếng Việt có dấu |
| NFR-08 | Khả năng bảo trì | Code chia module rõ ràng theo tầng: Giao diện → Service → ORM → CSDL |
| NFR-09 | Khả năng kiểm thử | Bộ kiểm thử tự động (pytest) cho các luồng nghiệp vụ cốt lõi |

## 4. Ràng buộc

- Chỉ dùng MySQL/MariaDB (qua XAMPP), không dùng SQLite.
- Không dùng API AI trả phí (OpenAI, Google Gemini...); toàn bộ AI chạy offline.
- Thông tin kết nối CSDL cấu hình qua file `.env`, không hard-code trong mã nguồn.
