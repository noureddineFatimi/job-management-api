FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/app

EXPOSE 90

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "90"]