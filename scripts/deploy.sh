git checkout main
git pull
systemctl restart myclimbz
chmod 777 /root/boulders/gunicorn_socket/myclimbz.sock
systemctl restart nginx
