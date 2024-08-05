# Sử dụng image python chính thức
FROM python:3.11-slim

# Đặt biến môi trường
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Đặt thư mục làm việc
WORKDIR /app

# Cài đặt các dependencies cần thiết cho việc build psycopg2
RUN apt-get update \
    && apt-get install -y gcc python3-dev libpq-dev \
    && apt-get clean

# Cài đặt các dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy toàn bộ mã nguồn của bạn vào container
COPY . /app/

# Chạy lệnh khởi tạo Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
