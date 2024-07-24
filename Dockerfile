FROM python:3.12.3-slim


RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    gcc \
    libffi-dev \
    python3-tk \
    python3-dev \
    xvfb \
    # For chromedriver
    libglib2.0-0 \
    libnss3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ADD requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN mkdir -p executables/browsers/chrome executables/drivers/chrome

RUN curl -sS -o /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/124.0.6367.201/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver.zip -d /tmp \
    && mv /tmp/chromedriver-linux64/chromedriver executables/drivers/chrome/ \
    && rm -r /tmp/chromedriver.zip /tmp/chromedriver-linux64

RUN curl -sS -o /tmp/chrome.zip https://storage.googleapis.com/chrome-for-testing-public/124.0.6367.201/linux64/chrome-linux64.zip \
    && unzip /tmp/chrome.zip -d /tmp \
    && mv /tmp/chrome-linux64/* executables/browsers/chrome \
    && rm -r /tmp/chrome.zip /tmp/chrome-linux64

ENV DISPLAY=:1

COPY run.sh .

COPY . .

COPY config.docker.ini /app/config.ini

RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]