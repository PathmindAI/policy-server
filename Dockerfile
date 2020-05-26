FROM python:3

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install -r requirements.txt

COPY . /usr/src/app

EXPOSE 8080

ENTRYPOINT ["gunicorn"]

CMD ["app:app", "-b", ":8080", "--log-level", "debug", "-w", "4"]
