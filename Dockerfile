FROM python:3.7-alpine
RUN mkdir -p /app/templates &&\
    addgroup -S vcode-operator &&\
    adduser vcode-operator -S -u 1000  -G vcode-operator -h /app &&\
    chown -R vcode-operator:vcode-operator /app
COPY requirements.txt /app
WORKDIR /app
RUN pip install -r requirements.txt
USER vcode-operator
CMD kopf run -A --peering=vcode-operator /app/vcode-operator.py 