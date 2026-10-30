# decnond

`decnond` chạy một tệp Python sau khi chuyển các literal số thực thập phân
trong tệp đó thành `decimal.Decimal` chính xác. Đây là công cụ chạy tệp, không
thay đổi cách Python phân tích mã trong chương trình đang gọi.

Sao chép thư mục này vào một nơi Python có thể tìm thấy, ví dụ thêm
`Tools/decnond` vào `PYTHONPATH`, rồi gọi:

```python
import decnond

decnond.run("filename.py")
```

Các literal như `0.1`, `.25`, `1e3` và `1_234.50` được chuyển thành
`Decimal`; số nguyên và số phức không bị thay đổi. Tệp được chạy với
`__name__ == "__main__"`, `sys.argv[0]` là đường dẫn tệp, và thư mục chứa tệp
được thêm tạm thời vào đầu `sys.path`. Trạng thái `sys.argv` và `sys.path`
được khôi phục sau khi chạy, kể cả khi tệp phát sinh ngoại lệ.
Khi dùng `run()`, `print()` hiển thị giá trị `Decimal` ở dạng fixed-point đầy
đủ thay vì dạng số mũ, đồng thời giữ nguyên các đối số như `sep`, `end`, `file`
và `flush`.

Việc chỉ `import decnond` không thay đổi cách phân tích literal trong mã gọi.
Chỉ các literal trong tệp được truyền vào `decnond.run()` mới được chuyển đổi.

Để chạy tệp với cách xử lý số thực mặc định của Python (`float`), dùng:

```python
decnond.killrun("filename.py")
```

`killrun()` không cần hoàn tác thay đổi nào trên tệp: `run()` chỉ biến đổi mã
trong bộ nhớ khi thực thi, không sửa nội dung file `.py`.
