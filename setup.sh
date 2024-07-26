#!/bin/bash
python -m seleniumwire extractcert
mv ca.crt /usr/local/share/ca-certificates/seleniumwire-ca.crt
update-ca-certificates