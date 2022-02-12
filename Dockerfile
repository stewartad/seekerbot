# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-alpine

WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFER 1

COPY requirements.txt .
RUN apk update \
    && apk add --virtual build-deps python3-dev gcc musl-dev \
    && pip install --upgrade pip \
    && pip install --no-cache -r requirements.txt \
    && apk del build-deps

RUN apk add --no-cache curl

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh # Removes Windows line endings
RUN chmod +x /usr/src/app/entrypoint.sh

COPY ./seeker.py .

ENTRYPOINT [ "/usr/src/app/entrypoint.sh" ]