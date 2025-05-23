FROM python:3.12.3-slim

WORKDIR /app

COPY . .

WORKDIR /app/my-app

RUN pip install --no-cache-dir -r ../requirements.txt

EXPOSE 5000

CMD ["python", "run.py"]
