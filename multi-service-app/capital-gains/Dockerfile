FROM python:3.12-slim

WORKDIR /app

COPY .. .

# Install the iputils-ping package so we can use the ping command
RUN apt-get update && apt-get install -y iputils-ping && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["python", "app.py"]