FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install -r requirements.txt

COPY . /usr/src/app

CMD ["uvicorn", "app:app",  "--host", "0.0.0.0"]