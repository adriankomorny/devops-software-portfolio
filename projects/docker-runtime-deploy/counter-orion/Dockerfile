FROM python:3.12-alpine

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY manage.py .

ENV APP_NAME=counter-orion
ENV APP_VERSION=dev

EXPOSE 8080
CMD ["python", "app.py"]
