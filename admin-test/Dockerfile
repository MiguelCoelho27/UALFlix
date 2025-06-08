FROM python:3.11-slim

ENV PYTHONIOENCODING=utf-8

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn
COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]