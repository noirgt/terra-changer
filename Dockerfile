FROM alpine:3.15.0

ARG version

ENV PYTHONUNBUFFERED=1
ENV PYCURL_SSL_LIBRARY=openssl
ENV CHANGER_VERSION=$version

WORKDIR /changer
COPY changer_py changer_py/
COPY main.py .
COPY requirements.txt .
COPY multiple.sh /bin/multiple

RUN apk add --no-cache libcurl
RUN apk --update add python3 \
py3-requests py3-bcrypt py3-cryptography py3-pynacl curl-dev git openssh \
    && apk add --update --no-cache --virtual \
    .build-dependencies py3-pip python3-dev build-base \
    && pip install -r requirements.txt \
    && apk del .build-dependencies \
    && rm -rf /var/cache/apk/*

RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

ENTRYPOINT ["/bin/multiple"]
