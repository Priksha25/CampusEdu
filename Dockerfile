        ############################################
        #  CampusEdu Smart Chatbot  —  Dockerfile  #
        ############################################

FROM python:3.11-slim

LABEL maintainer="CampusEdu"
LABEL description="CampusEdu Smart Chatbot v2.0"
LABEL version="2.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
    && rm -rf /var/lib/apt/lists/*


COPY requirement.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirement.txt

COPY . .

RUN mkdir -p /app/data

EXPOSE 8000

CMD ["python", "web.py"]
