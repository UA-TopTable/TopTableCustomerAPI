FROM python:3.12.7

COPY ./requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

WORKDIR /app

CMD ["python3","-m","flask","run","--host=${HOST:-0.0.0.0}","--port=${PORT:-5000}","--debug"]
