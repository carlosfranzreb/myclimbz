# Important things to know about the server

I mainly followed this guide: <https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-22-04>

## Install NGINX

1. `apt update`
2. `apt install nginx`
3. `ufw allow NGINX HTTP(S)`
4. Check that it's running with `systemctl status nginx`

Read about the different options here: <https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-22-04>

## How to create the prod database

This guide can also be used to add new users to an existing database.

1. `docker compose build`
2. `docker run --rm -it --entrypoint bash -v ./instance:/usr/src/instance -v ./climbz:/usr/src/climbz ghcr.io/carlosfranzreb/boulders:latest`
3. From another terminal copy create_db.py and add_user_to_db.py with `docker cp ./scripts/db/create_db.py 66ba6b039776:/usr/src/create_db.py`, where `66ba6b039776` is the container ID (you can find it with `docker ps`).
4. Create the prod database and add users

## How the app is started

We have configured it as a service under `/etc/systemd/system/myclimbz.service`, which can be managed with `systemctl`.

The service starts docker compose. For the production DB to be used the environment variable `PROD` must be set to 1 in the `.env` file.

The configuration for gunicorn is in `gunicorn_config.py`. The web is available in a socket, which is accessible for NGINX.

If you pull new code, restart the service with `systemctl restart myclimbz`. Once the new socket is created, change its permissions with `chmod 777 /root/boulders/gunicorn_socket/myclimbz.sock`. (TODO: are these permissions dangerous? It does not work with 755)


## Nginx config

- The server is configured in `/etc/nginx/sites-available/myclimbz`
- The config is enabled with this link: `ln -s /etc/nginx/sites-available/myclimbz /etc/nginx/sites-enabled`
- The Nginx service can be managed with `systemctl`
- If any errors happen, check the error log by running: `less /var/log/nginx/error.log`


## Certbot

- `apt install python3-certbot-nginx`
- `certbot --nginx -d myclimbz.com -d www.myclimbz.com`
