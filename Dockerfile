FROM python:3.12.3

COPY ./requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY ./app .

ENV FLASK_APP=app/app.py

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]