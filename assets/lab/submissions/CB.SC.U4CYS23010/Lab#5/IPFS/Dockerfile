
FROM alpine:latest


RUN apk add --no-cache wget tar bash libc6-compat


RUN wget https://dist.ipfs.tech/kubo/v0.29.0/kubo_v0.29.0_linux-amd64.tar.gz -O /tmp/kubo.tar.gz \
    && tar -xzf /tmp/kubo.tar.gz -C /tmp \
    && mv /tmp/kubo/ipfs /usr/local/bin/ipfs \
    && rm -rf /tmp/kubo /tmp/kubo.tar.gz \
    && ipfs --version


WORKDIR /app


COPY hi.txt .


COPY upload_to_ipfs.sh .


RUN chmod +x upload_to_ipfs.sh


CMD ["sh", "/app/upload_to_ipfs.sh"]
