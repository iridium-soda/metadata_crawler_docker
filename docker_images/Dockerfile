FROM python:latest
LABEL maintainer="Louis Liu"
WORKDIR /
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone
COPY src/ /
COPY requirements.txt /
RUN pip install -r requirements.txt
CMD ["python", "main.py"]