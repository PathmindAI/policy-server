FROM python:3.7

ARG MODEL_PATH

WORKDIR /usr/src/app

RUN apt update -y && \
    apt install default-jdk -y && \
    wget https://oss.sonatype.org/content/repositories/releases/io/swagger/swagger-codegen-cli/2.2.1/swagger-codegen-cli-2.2.1.jar

COPY requirements.txt /usr/src/app/
COPY swagger-codegen /bin/

RUN chmod +x /bin/swagger-codegen
RUN pip3 install -r requirements.txt
RUN mkdir models

COPY . /usr/src/app

EXPOSE 8080
RUN TUPLE=True python generate.py schema ${MODEL_PATH}
