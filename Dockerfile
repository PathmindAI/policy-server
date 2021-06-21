FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN mkdir -p /usr/src/app
RUN mkdir -p /usr/src/app/models

WORKDIR /usr/src/app

RUN apt update -y && \
    apt install default-jdk -y && \
    wget https://oss.sonatype.org/content/repositories/releases/io/swagger/swagger-codegen-cli/2.2.1/swagger-codegen-cli-2.2.1.jar

COPY requirements.txt /usr/src/app/
COPY swagger-codegen /usr/src/app/

RUN chmod +x swagger-codegen
RUN cp swagger-codegen-cli-2.2.1.jar swagger-codegen-cli.jar
RUN pip3 install -r requirements.txt

COPY . /usr/src/app

ARG S3BUCKET
ARG S3MODELPATH
ARG S3SCHEMAPATH
ENV AWS_DEFAULT_REGION=us-east-1
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_ACCESS_KEY_ID

RUN aws s3 cp s3://${S3BUCKET}/${S3SCHEMAPATH} ./schema.yaml && \
    aws s3 cp s3://${S3BUCKET}/${S3MODELPATH} ./saved_model.zip && \
    python generate.py unzip

CMD ["uvicorn", "app:app",  "--host", "0.0.0.0"]
