FROM hrshadhin/ot-recorder
COPY config.yml /app/config.yml
COPY nginx.conf /etc/nginx/nginx.conf
COPY runstuff.sh /app/runstuff.sh
COPY htpasswd /etc/nginx/htpasswd
COPY findmysteve.py /app/findmysteve.py
COPY findmysteve.sh /app/findmysteve.sh

USER root
RUN apk add nginx
RUN apk add python3
RUN apk add py3-pip
RUN apk add vim
RUN pip3 install psycopg2-binary
RUN pip3 install slack_bolt
RUN pip3 install requests
RUN pip3 install pytz
ENTRYPOINT ["/bin/sh"]
CMD ["/app/runstuff.sh"]


