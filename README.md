# Facility Management (Django)

Simple facility management app for university assets and maintenance requests.

Setup (PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open http://127.0.0.1:8000/ and log in via /admin/ for admin tasks.

Features:
- Quản lý tài sản: Thêm/Sửa/Xóa (Admin)
- Tạo yêu cầu bảo trì (Người dùng)
- Cập nhật tiến độ (Admin)
- Dashboard với Chart.js
