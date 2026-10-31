FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt /app/
RUN python -m pip install --upgrade pip
RUN python -m pip install -r /app/requirements.txt

COPY core /app/core/
COPY database /app/database/
COPY dependencies /app/dependencies/
COPY routes /app/routes/
COPY schemas /app/schemas/
COPY src /app/src/
COPY utils /app/utils/

EXPOSE 8001