FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

ARG MODEL_PATH

RUN mkdir -p /usr/src/app
RUN mkdir -p /usr/src/app/models

WORKDIR /usr/src/app

RUN apt update -y && \
    apt install default-jdk -y && \
    wget https://oss.sonatype.org/content/repositories/releases/io/swagger/swagger-codegen-cli/2.2.1/swagger-codegen-cli-2.2.1.jar

COPY requirements.txt /usr/src/app/
COPY swagger-codegen /bin/

RUN chmod +x /bin/swagger-codegen
RUN pip3 install -r requirements.txt

COPY . /usr/src/app

RUN cp ${MODEL_PATH}/schema.yaml ./ && \
    cp ${MODEL_PATH}/saved_model.zip ./ && \
    python generate.py unzip

CMD ["uvicorn", "app:app",  "--host", "0.0.0.0"]
