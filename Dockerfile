FROM python:3.10.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

WORKDIR /app/my-app

RUN pip install --no-cache-dir -r ../requirements.txt

EXPOSE 5000

CMD ["python", "run.py"]
