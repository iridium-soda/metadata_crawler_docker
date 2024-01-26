FROM python:latest
LABEL maintainer="Louis Liu" version="1.0" description="Proxy Server"
WORKDIR /app
COPY src/*.py src/requirements.txt .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
