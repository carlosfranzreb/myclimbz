#!/bin/bash
set -e

git checkout main
git pull
systemctl restart myclimbz
sleep 10
chmod 777 /root/boulders/gunicorn_socket/myclimbz.sock