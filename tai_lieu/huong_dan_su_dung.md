# Hướng Dẫn Sử Dụng

## 1. Đăng nhập

Mở chương trình bằng `python run.py`, nhập tên đăng nhập và mật khẩu được
cấp. Sau 5 lần đăng nhập sai liên tiếp (mặc định), tài khoản sẽ tự động bị
khóa 15 phút để chống dò mật khẩu.

## 2. Dành cho Quản Trị Viên (ADMIN)

### 2.1. Quản lý danh mục
Vào **Quản Lý Khoa - Lớp** để thêm Khoa và Lớp hành chính. Vào **Quản Lý
Môn - Lớp Học Phần** để thêm Môn học, mở Lớp học phần (gán giảng viên phụ
trách, học kỳ/năm học), và đăng ký sinh viên vào từng lớp học phần.

### 2.2. Quản lý sinh viên / giảng viên
Vào **Quản Lý Sinh Viên** / **Quản Lý Giảng Viên** để thêm, sửa, tìm kiếm
theo tên/mã, lọc theo lớp. Sinh viên đã có lịch sử điểm danh sẽ không xóa
được — hãy dùng nút **Đổi Trạng Thái** (Nghỉ học/Bảo lưu/Tốt nghiệp) thay
vì xóa.

### 2.3. Quản lý tài khoản & cấu hình
Vào **Cài Đặt → Quản Lý Tài Khoản** để tạo tài khoản đăng nhập mới, khóa/mở
khóa, hoặc đặt lại mật khẩu cho người dùng quên mật khẩu. Vào **Cài Đặt →
Cấu Hình Hệ Thống** để chỉnh ngưỡng nhận diện khuôn mặt, số lần đăng nhập
sai tối đa, thời gian khóa tài khoản — áp dụng ngay không cần khởi động
lại chương trình.

### 2.4. Xem nhật ký hệ thống
Vào **Nhật Ký Hệ Thống** để xem toàn bộ lịch sử thao tác quan trọng: đăng
nhập/thất bại, thêm/sửa/xóa dữ liệu, điểm danh, thay đổi cấu hình... Có
thể lọc theo loại hành động.

## 3. Dành cho Giảng Viên (GIANG_VIEN)

### 3.1. Đăng ký khuôn mặt cho sinh viên
Vào **Đăng Ký Khuôn Mặt**, chọn sinh viên từ danh sách, bật camera, canh
khuôn mặt vào khung hình, nhấn **Chụp & Đăng Ký**. Có thể đăng ký nhiều
ảnh cho cùng một sinh viên (các góc/ánh sáng khác nhau) để tăng độ chính
xác nhận diện.

### 3.2. Thực hiện điểm danh
Vào **Điểm Danh**:
1. Chọn **Lớp học phần**.
2. Nhấn **+ Tạo Buổi Học** nếu buổi học hôm nay chưa có, điền ngày/giờ/phòng.
3. Chọn buổi học vừa tạo trong danh sách **Buổi học**.
4. Nhấn **Mở Điểm Danh**.
5. Nhấn **Bật Camera & Nhận Diện** — hệ thống tự động quét khuôn mặt sinh
   viên đi vào khung hình mỗi 1.5 giây và ghi nhận điểm danh nếu nhận diện
   thành công (thông báo hiện ngay bên dưới khung camera).
6. Sinh viên đến muộn (sau khoảng thời gian cho phép tính từ giờ bắt đầu)
   sẽ tự động được ghi nhận "Đi muộn" thay vì "Có mặt".
7. Với sinh viên không có camera nhận diện được (quên đăng ký khuôn mặt,
   ánh sáng kém...), chọn sinh viên trong bảng bên phải và nhấn nút trạng
   thái thủ công tương ứng (Có mặt/Đi muộn/Vắng/Có phép).
8. Khi kết thúc buổi học, nhấn **Đóng Điểm Danh** — hệ thống tự động đánh
   dấu "Vắng" cho các sinh viên đăng ký lớp nhưng chưa được điểm danh.

### 3.3. Xem báo cáo
Vào **Báo Cáo**, chọn lớp học phần và khoảng thời gian, nhấn **Thống Kê**
để xem tỷ lệ có mặt/đi muộn/vắng/có phép của từng sinh viên. Có thể xuất
ra Excel hoặc PDF để nộp hoặc lưu trữ.

## 4. Dành cho Sinh Viên (SINH_VIEN)

- Vào **Báo Cáo** để xem lịch sử điểm danh của chính mình theo từng môn học.
- Vào **Cài Đặt → Đổi Mật Khẩu** để tự đổi mật khẩu định kỳ.

## 5. Câu hỏi thường gặp

**Vì sao hệ thống điểm danh nhầm sang sinh viên khác?**
Có thể do ngưỡng độ tương đồng đang đặt quá thấp, hoặc dữ liệu khuôn mặt
đăng ký chưa đủ rõ nét. Admin có thể tăng `NGUONG_DO_TUONG_DONG` trong
**Cài Đặt → Cấu Hình Hệ Thống** (giá trị càng cao càng nghiêm ngặt, nhưng
dễ từ chối nhận diện hơn).

**Có thể điểm danh hai lần cho cùng một buổi học không?**
Không. Hệ thống có ràng buộc UNIQUE ở cấp cơ sở dữ liệu (không chỉ ở giao
diện) đảm bảo mỗi sinh viên chỉ có đúng một bản ghi điểm danh cho mỗi
buổi học.

**Sinh viên nghỉ học có bị xóa khỏi hệ thống không?**
Không nên xóa. Hãy đổi trạng thái sang "Nghỉ học" để giữ lại toàn bộ lịch
sử điểm danh trước đó phục vụ tra cứu/báo cáo sau này.
