#!/bin/bash
curl -o /usr/local/share/ca-certificates/seleniumwire-ca.crt "https://raw.githubusercontent.com/wkeeling/selenium-wire/master/seleniumwire/proxy/ca.crt"

sudo update-ca-certificates