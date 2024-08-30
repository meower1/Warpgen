# Warpgen

<p align="center">
  <img src="https://github.com/user-attachments/assets/5e25f0cf-c4a1-479a-a6f3-24f31d9f7fbd" alt="Aggify">
</p>
<p align="center">
    <em>Warpgen is an API that generates Warp+ keys</em>
</p>

## 📚 Overview

This API allows you to generate fully functioning warp+ subscription keys
It does so by scraping the keys from t.me/warpplus every hour
It also comes with rate limitting to prevent spam/abuse

## 🎯 Endpoints

There are two available endpoints to use:

| Method | Endpoint   | Description                                        |
| ------ | ---------- | -------------------------------------------------- |
| GET    | **"/"**    | Access the WebUI                                   |
| GET    | **"/api"** | Primary endpoint to recieve the key as plain text. |

## 💻 Development

The development process is fairly simple.
All you gotta do is run the dev docker compose file using the following command:

```sh
docker compose --file docker-compose-dev.yml up
```

## ☁️ Deployment

First you must get an ssl certificate. I'll be using acme here.
Run the following commands in the given order. Make sure to replace your domain in the commands

```sh
curl https://get.acme.sh/ | sh

~/.acme.sh/acme.sh --set-default-ca --server letsencrypt

~/.acme.sh/acme.sh --register-account -m your@gmail.com

~/.acme.sh/acme.sh --issue -d host.mydomain.com --standalone
```

After running the given commands your certificate files will be in
/etc/letsencrypt/live/host.mydomain.com

You need the following files:
fullchain.pem, privkey.pem, options-ssl-nginx.conf & ssl-dhparams.pem

Carefully copy the given files into the nginx directory of the project.

```sh
cd nginx/
cp /etc/letsencrypt/options-ssl-nginx.conf .
cp /etc/letsencrypt/ssl-dhparams.pem .
cp /etc/letsencrypt/live/host.mydomain.com/fullchain.pem .
cp /etc/letsencrypt/live/host.mydomain.com/privkey.pem .
```

Modify the nginx/Dockerfile to match the file names.

nginx/Dockerfile:

```yaml
FROM nginx

RUN apt-get update && \
    apt-get install -y curl

COPY nginx.conf /etc/nginx/nginx.conf
COPY fullchain.pem /etc/letsencrypt/host.mydomain.com/fullchain.cer # Change to your own domain/format
COPY privkey.pem /etc/letsencrypt/host.mydomain.com/privkey.pem # Change to your own domain/format
COPY options-ssl-nginx.conf /etc/letsencrypt/options-ssl-nginx.conf
COPY ssl-dhparams.pem /etc/letsencrypt/ssl-dhparams.pem
```

And after following the given steps run the docker compose file to deploy your project! 🎉🎉

```sh
docker compose up -d
```

## 🌟 Contribution

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change

**Credits:**

- [TelegramChannelScraper](https://github.com/abdiu34567/Telegram-Channel-Scraper_API-DOC)
