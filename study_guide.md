# Hướng dẫn Ôn tập Vấn đáp: Distributed Semi-Join (Topic #11)

Tài liệu này tóm tắt toàn bộ kiến thức lý thuyết và thực hành của dự án để bạn tự tin trả lời vấn đáp cuối kỳ.

---

## 1. Lý thuyết Hệ CSDL Phân tán (Özsu & Valduriez)

### 1.1. Tại sao phải tối ưu hóa truy vấn phân tán?
Trong hệ thống tập trung (Centralized), chi phí chính là đọc/ghi ổ đĩa (I/O). Nhưng trong hệ thống **Phân tán (Distributed)**, dữ liệu nằm ở các Site khác nhau, nên **Chi phí truyền tải mạng (Communication Cost)** là lớn nhất và là nút thắt cổ chai của hệ thống.

### 1.2. Mô hình chi phí (Cost Model)
Công thức tổng quát:
$$Total\_Cost = C_{io} + C_{cpu} + C_{comm}$$

Trong đó, dự án tập trung vào tối ưu $C_{comm}$:
$$C_{comm}(size) = C_{msg} + C_{tr} \times size$$
- $C_{msg}$: Chi phí thiết lập kết nối (Latency).
- $C_{tr}$: Chi phí truyền tải trên mỗi đơn vị dữ liệu (Bandwidth).
- **Mục tiêu:** Giảm `size` (kích thước dữ liệu truyền đi) để giảm tổng chi phí.

---

## 2. Thuật toán Semi-Join ($R \ltimes S$)

Đây là nội dung cốt lõi của Topic #11. Giả sử ta muốn Join bảng `Employees` (R - ở Site 1) và `Assignments` (S - ở Site 2).

### Quy trình 4 bước của Semi-Join trong dự án:
1.  **Chiếu (Projection):** Tại Site 2, ta chỉ lấy cột `EmpID` từ bảng `Assignments` và loại bỏ các giá trị trùng lặp. Kết quả là một tập nhỏ các mã nhân viên ($S'$).
2.  **Truyền tải (Reduction):** Gửi tập $S'$ (rất nhẹ) từ Site 2 sang Site 1.
3.  **Lọc (Filtering):** Tại Site 1, ta lấy bảng `Employees` (R) đem Join với tập $S'$. Những nhân viên nào có mã nằm trong $S'$ thì giữ lại. Kết quả là $R' = R \ltimes S$.
4.  **Kết quả:** Gửi $R'$ về cho bộ điều phối (Coordinator) để hiển thị.

**=> So sánh:** Thay vì gửi toàn bộ 50,000 dòng của bảng Assignments (Standard Join), ta chỉ gửi một danh sách mã nhân viên duy nhất (Semi-Join).

---

## 3. Các thông số đo lường (Metrics)

Bạn cần nhớ các định nghĩa này để giải thích kết quả trên UI:
- **Bytes Transferred:** Tổng số byte đã đi qua dây cáp mạng.
- **Execution Time:** Tổng thời gian từ lúc bấm nút đến lúc có kết quả.
- **Size Reduction Factor:** Tỉ lệ dữ liệu đã được cắt giảm nhờ Semi-Join. (Ví dụ: Giảm 77% nghĩa là Semi-Join chỉ tốn 23% băng thông so với Standard Join).
- **Speedup Factor:** Semi-Join nhanh hơn Standard Join bao nhiêu lần.

---

## 4. Các câu hỏi vấn đáp thường gặp (Q&A)

**Q1: Tại sao em lại chọn FastAPI và Pandas?**
*Trả lời:* FastAPI giúp mô phỏng việc giao tiếp giữa các Site qua giao thức HTTP (thực tế nhất). Pandas giúp xử lý dữ liệu cực nhanh trong bộ nhớ RAM để tập trung đo lường độ trễ mạng.

**Q2: Nếu bảng Assignments rất nhỏ (ví dụ 10 dòng), em có dùng Semi-Join không?**
*Trả lời:* Có thể không. Vì Semi-Join tốn thêm chi phí tính toán (Projection) và thêm một lần gửi tin nhắn ($C_{msg}$). Nếu bảng quá nhỏ, việc gửi thẳng (Standard Join) có thể nhanh hơn. Semi-Join phát huy tác dụng nhất khi bảng tham gia Join rất lớn.

**Q3: Tính "Localization" (Bản địa hóa) trong bài của em thể hiện ở đâu?**
*Trả lời:* Thể hiện ở việc Site 1 và Site 2 chỉ xử lý dữ liệu cục bộ của chính nó (Local Query). Site 1 tự lọc Employee, Site 2 tự lấy EmpID, không site nào can thiệp vào ổ đĩa của site nào.

**Q4: Làm sao em biết kết quả của Semi-Join và Standard Join là giống nhau?**
*Trả lời:* Cả hai đều trả về cùng một danh sách nhân viên có tham gia dự án. Semi-Join chỉ là "con đường" khác tối ưu hơn để đi đến cùng một đích.

---

## 5. Cấu trúc hệ thống (Kiến trúc 3 Node)
- **Node 1 (Port 8001):** "Kho" dữ liệu nhân viên.
- **Node 2 (Port 8002):** "Kho" dữ liệu dự án.
- **Coordinator (Port 8000):** "Bộ não" điều khiển, nhận lệnh từ người dùng và điều phối 2 kho trên.

---
*Chúc bạn ôn tập tốt và đạt kết quả cao!*
