FROM python:3.9-alpine

COPY entrypoint.sh /entrypoint.sh
COPY cmake-format/ /cmake-format/

RUN chmod +x entrypoint.sh

RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir "Cython<3" "cmakelang[YAML]==0.6.13"

ENTRYPOINT ["/entrypoint.sh"]
