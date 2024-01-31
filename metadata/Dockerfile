FROM python:latest
LABEL maintainer="Louis Liu" version="1.0"
WORKDIR /app
COPY src/*.py requirements.txt .
RUN echo 'Asia/Shanghai' >/etc/timezone && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && pip3 install -r requirements.txt 
CMD ["python3", "main.py"]
