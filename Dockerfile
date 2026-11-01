FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

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

COPY alembic /app/alembic/
COPY alembic.ini /app/alembic.ini
COPY main.py /app/main.py
COPY seed_data.py /app/seed_data.py

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]