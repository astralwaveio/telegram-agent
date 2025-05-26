FROM python:3.12.3-slim

WORKDIR /app

COPY . .

RUN python -m pip install --upgrade pip --no-cache-dir \
    && pip install --no-cache-dir -r requirements.txt

CMD ["python3", "-m", "src.astra"]
