FROM python:3.12.7

COPY ./requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

WORKDIR /app

ENV FLASK_APP=app.py
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
