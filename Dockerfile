FROM python:3.12.3-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ["python3", "-m", "src.astra"]
