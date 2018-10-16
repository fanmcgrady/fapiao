# 关闭原有服务
ps -ef|grep "runserver 0.0.0.0"|grep -v grep|cut -c 10-15|xargs kill -9
# 切换到anaconda环境
source activate fapiao
# 更新代码
git pull
# 后台启动django服务
nohup python manage.py runserver 0.0.0.0:8000 --insecure &
