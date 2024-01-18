#!/bin/bash

nginx
/bin/sh /app/findmysteve.sh &

/app/ot-recorder --config /app/config.yml serve

