FROM nginx

RUN apt-get update && \
    apt-get install -y curl

COPY nginx.conf /etc/nginx/nginx.conf
COPY fullchain.pem /etc/letsencrypt/live/warp.meower1.dev/fullchain.pem
COPY privkey.pem /etc/letsencrypt/live/warp.meower1.dev/privkey.pem
COPY options-ssl-nginx.conf /etc/letsencrypt/options-ssl-nginx.conf
COPY ssl-dhparams.pem /etc/letsencrypt/ssl-dhparams.pem

