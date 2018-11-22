FROM python:3.6.5-alpine

ARG TERRAFORM_VERSION=0.11.10
ARG HASHICORP_RELEASES=https://releases.hashicorp.com

RUN apk add --no-cache --update \
    ca-certificates \
    openssl

RUN wget ${HASHICORP_RELEASES}/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip -O /tmp/terraform.zip && \
    unzip -d /usr/bin /tmp/terraform.zip && \
    rm /tmp/terraform.zip && \
    chmod +x /usr/bin/terraform

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY . /terrestrial
RUN chown -R nobody:nobody /terrestrial

USER nobody
WORKDIR /terrestrial

ENTRYPOINT ["/terrestrial/entrypoint.sh"]
