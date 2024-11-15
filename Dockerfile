FROM python:3.12.3-slim:2a6386ad2db20e7f55073f69a98d6da2cf9f168e05e7487d2670baeb9b7601c5


RUN apt-get update && apt-get install -y \
    procps curl unzip gcc libffi-dev python3-tk python3-dev \
    xorg xvfb gtk2-engines-pixbuf x11vnc dbus-x11 xfonts-base xfonts-100dpi xfonts-75dpi xfonts-scalable \
    # For Chrome
    libxpm4 libxrender1 libgtk2.0-0 libnss3 libgconf-2-4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxcomposite1 libxdamage1 libgbm1 libxkbcommon0 libpango-1.0-0 libcairo2 libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ADD requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN mkdir -p executables/browsers/chrome

RUN curl -sS -o /tmp/chrome.zip https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.58/linux64/chrome-linux64.zip \
    && unzip /tmp/chrome.zip -d /tmp \
    && mv /tmp/chrome-linux64/* executables/browsers/chrome \
    && rm -r /tmp/chrome.zip /tmp/chrome-linux64

ENV DISPLAY=:0

COPY . .

RUN chmod +x run.sh create_display.sh

EXPOSE 5900

CMD ["/app/run.sh"]