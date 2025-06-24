FROM python:3.12.10

WORKDIR /traceapi

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
