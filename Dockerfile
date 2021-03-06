FROM python:3.8

COPY ./requirements.txt /requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

WORKDIR /engie
COPY . /engie

ENV PYTHONPATH /engie

EXPOSE 8888

CMD ["python", "app/app.py" ]