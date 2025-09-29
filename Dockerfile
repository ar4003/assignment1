FROM python:3.11-slim

# Install system dependencies for building scientific libraries
RUN apt-get update && apt-get install -y build-essential gcc g++ libatlas-base-dev

WORKDIR /app

COPY . .

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

CMD ["gunicorn", "main:app"]
