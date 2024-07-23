FROM python:3.12.3-slim


RUN apt-get update && apt-get install -y curl unzip gcc libffi-dev python3-tk python3-dev xvfb\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ADD requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p executables/browsers/chrome executables/drivers/chrome

RUN curl -sS -o /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/124.0.6367.201/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver.zip -d executables/drivers/chrome/chromedriver

RUN curl -sS -o /tmp/chrome.zip https://storage.googleapis.com/chrome-for-testing-public/124.0.6367.201/linux64/chrome-linux64.zip \
    && unzip /tmp/chrome.zip -d executables/browsers/chrome \
    && rm /tmp/chrome.zip

ENV DISPLAY=:1

COPY run.sh /app/run.sh

RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]