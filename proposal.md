# Distributed Database Project Proposal

**Due Date:** [Insert Date - Week 3]
**Project ID & Category:** #11: Distributed Semi-Join Implementation - Category 2

## 1. Project Identity
*   **Team Name:** Data Mavericks
*   **Team Members:** Hugh Willliams
*   **Project Title:** Optimizing Distributed Queries with Semi-Join vs. Ship-Whole-Table

## 2. Objective & Problem Statement
*   **The "Why":** Trong môi trường cơ sở dữ liệu phân tán, chi phí truyền tải mạng (Network Communication Cost) thường là nút thắt cổ chai lớn nhất khi thực hiện phép Join giữa các bảng ở các Site khác nhau. Dự án này chứng minh làm thế nào thuật toán Semi-Join giảm thiểu băng thông (Bytes Transferred) so với phương pháp Standard Join (Ship-Whole-Table).
*   **Core Logic:** Thực thi phép toán Semi-Join ($R \ltimes S$). Thay vì gửi toàn bộ bảng Assignments (S) sang Node chứa Employees (R), hệ thống chỉ gửi tập hợp các giá trị khoá (`EmpID`) duy nhất từ S sang R. Sau đó R lọc dữ liệu (Filter) và chỉ gửi lại các dòng khớp.

## 3. Dataset Specification
*   **Source:** Dữ liệu tự sinh ngẫu nhiên (Mock Data) bằng thư viện `Faker` của Python.
*   **Size:** 
    *   Bảng `Employees`: 10,000 dòng.
    *   Bảng `Assignments`: 50,000 dòng.
*   **Schema:** 
    *   `Employees` (EmpID, Name, Department, Email, Salary).
    *   `Assignments` (AssignID, EmpID, ProjectID, HoursLogged).
*   **Fragmentation Strategy:** Dữ liệu được lưu trữ phân tán. Node 1 giữ Employee, Node 2 giữ Assignment.

## 4. System Architecture
*   **Nodes:** 3 Data Nodes (Node 1, Node 3 for Employee fragments, Node 2 for Assignment) + 1 Coordinator Node.
*   **Communication Layer:** HTTP/REST API thông qua framework FastAPI. JSON payload dùng để trao đổi dữ liệu.
*   **Storage:** Local CSV files được nạp vào bộ nhớ RAM (bằng Pandas DataFrame) khi hệ thống khởi động để tối ưu tốc độ đọc.

## 5. Tech Stack & Implementation Plan
*   **Programming Language:** Python 3.10+
*   **Deployment:** Localhost processes.
*   **Libraries/Frameworks:** Pandas (xử lý dữ liệu in-memory), FastAPI (networking & API), HTTPX (client requesting).

## 6. Success Metrics & Analysis
*   **Quantitative Metric:** 
    *   Total Bytes Transferred (Dung lượng truyền tải mạng).
    *   Total Execution Time (Thời gian thực thi).
    *   *Size Reduction Factor* (Tỉ lệ giảm thiểu băng thông).
*   **The "Failure" Scenario:** Kill Node 2 (Assignments Node) khi Coordinator đang cố gắng gửi request. Coordinator sẽ timeout/catch exception thay vì treo toàn bộ hệ thống (Transaction Aborted).

## 7. Project Milestones
*   **Milestone 1:** Thiết lập môi trường và tạo script sinh dữ liệu ngẫu nhiên (10k dòng Employee, 50k dòng Assignment).
*   **Milestone 2:** Xây dựng Node 1 và Node 2 với các API đọc và thực thi thuật toán.
*   **Milestone 3:** Xây dựng Coordinator, tích hợp đo lường chi phí mạng, kiểm thử "Failure Scenario" và viết Design Document.
