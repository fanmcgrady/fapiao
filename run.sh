ps -ef|grep "runserver 0.0.0.0"|grep -v grep|cut -c 10-15|xargs kill -9
source activate django
git pull
nohup python manage.py runserver 0.0.0.0:8000 &
