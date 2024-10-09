# Compile frontend
FROM node:20-alpine3.18 as frontend_build

RUN mkdir /var/gui
WORKDIR /var/gui

COPY gui/ /var/gui

RUN npm install
RUN npm run build

# Python server
FROM python:3.9.19-alpine

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

COPY --from=frontend_build /var/gui/dist /usr/src/app/static

COPY lan-index-api/requirements.txt .
COPY lan-index-api/*.py .
COPY lan-index-api/*.py .
COPY lan-index-api/schema.sqlite .

RUN pip3 install -r requirements.txt

RUN apk update
RUN apk add nmap

ENTRYPOINT ["python3", "app.py"]
