FROM --platform=linux/amd64 python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc ffmpeg libsm6 libxext6 libgl1-mesa-glx git

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
COPY env/dev.env .env

EXPOSE 8000

CMD ["chainlit", "app.py", "-w"]
