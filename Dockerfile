FROM python:3-alpine

COPY entrypoint.sh /entrypoint.sh
COPY cmake-format/ /cmake-format/

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
