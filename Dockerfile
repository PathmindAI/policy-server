FROM tensorflow/tensorflow:latest

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install -r requirements.txt

COPY . /usr/src/app

#CMD ["ray", "start", "--head", "--metrics-export-port=8080"]
#ENTRYPOINT ["uvicorn", "app:app"]

EXPOSE 8080
EXPOSE 8000
