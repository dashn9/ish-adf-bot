FROM python:3.12.3-slim


RUN apt-get update && apt-get install -y \
    curl unzip gcc libffi-dev python3-tk python3-dev xvfb x11vnc \
    # For chromedriver
    libglib2.0-0 libnss3 \
    # For Chrome
    libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxcomposite1 libxdamage1 libgbm1 libxkbcommon0 libpango-1.0-0 libcairo2 libasound2 \
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

ENV DISPLAY=:0

# You can configure a color depth of 8 here to save memory, however ad detection systems might look into it for patterns
ENV RESOLUTION=1920x1080x24

COPY . .

COPY config.docker.ini /app/config.ini

RUN chmod +x run.sh setup.sh

RUN ./setup.sh

EXPOSE 5900

CMD ["/app/run.sh"]