FROM python:3.11-slim

# Install system libraries that MediaPipe needs
RUN apt-get update && apt-get install -y \
    libgles2 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/dpkg/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]