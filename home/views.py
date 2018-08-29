import datetime
import json
import os

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .models import Article
from .models import Img
from .models import Typemsg
from .models import Usermsg
from .utils import detectType
from .utils import Ocr

# Create your views here.
def index(request):
    return render(request, 'index.html')

# 识别demo
def ocr(request):
    if request.method == 'GET':
        img_list = Img.objects.all()
        return render(request, 'ocr.html', {'img_list': img_list})
    elif request.method == "POST":
        obj = request.FILES.get('fapiao')

        # 随机文件名
        filename = generate_random_name()

        file_path = os.path.join('upload', filename)
        out_filename = os.path.join('out', filename)

        full_path = os.path.join('allstatic', file_path)
        f = open(full_path, 'wb')
        for chunk in obj.chunks():
            f.write(chunk)
        f.close()

        try:
            jsonResult, flag = Ocr.init(file_path)
            ret = {
                'status': True,
                'path': file_path,
                'out': out_filename,
                'color': "蓝底车票" if flag == 1 else "红底车票",
                'result' : json.loads(jsonResult)
            }
            # Img.objects.create(path=file_path, out=out_filename, color=color)
        except Exception as e:
            ret = {'status': False, 'path': file_path, 'out': str(e)}

        return HttpResponse(json.dumps(ret, indent=2))

# 矫正demo
def surface(request):
    if request.method == 'GET':
        img_list = Img.objects.all()
        return render(request, 'detect.html', {'img_list': img_list})
    elif request.method == "POST":
        obj = request.FILES.get('fapiao')

        # 随机文件名
        filename = generate_random_name()

        file_path = os.path.join('upload', filename)
        out_filename = os.path.join('out', filename)

        # file_path = os.path.join('upload', obj.name)

        full_path = os.path.join('allstatic', file_path)
        f = open(full_path, 'wb')
        for chunk in obj.chunks():
            f.write(chunk)
        f.close()

        try:
            _, flag = detectType.detectType('allstatic', file_path)
            color = "蓝底车票" if flag == 1 else "红底车票"
            ret = {
                'status': True,
                'path': file_path,
                'out': out_filename,
                'color': color
            }
            Img.objects.create(path=file_path, out=out_filename, color=color)
        except Exception as e:
            print(e)
            ret = {'status': False, 'path': file_path, 'out': str(e)}

        return HttpResponse(json.dumps(ret))
        # img_list = Img.objects.all()
        # return render(request, 'upload.html', {'img_list': img_list})


def article(request, aid):
    thisarticle = list(Article.objects.filter(id=aid).values("id", "title", "author", "content"))[0]
    return render(request, "detail.html", {"thisarticle": thisarticle, })


def reg(request):
    if request.session.has_key("name617826782"):
        return HttpResponseRedirect("/")
    if request.method == "POST":
        name = request.POST["name"]
        passwd = request.POST["passwd"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        Usermsg.objects.create(name=name, passwd=passwd, email=email, phone=phone, isadmin=0)
        return HttpResponse("注册成功！")
    return render(request, "reg.html")


def login(request):
    if request.session.has_key("name617826782"):
        return HttpResponseRedirect("/")
    if request.method == "POST":
        name = request.POST["name"]
        passwd = request.POST["passwd"]
        islogin = Usermsg.objects.filter(name__exact=name, passwd__exact=passwd)
        if islogin:
            request.session["name617826782"] = name
            return HttpResponseRedirect("/")
        else:
            return HttpResponse("登录失败！")
    return render(request, "login.html")


def logout(request):
    del request.session["name617826782"]
    return HttpResponseRedirect("/")


# def index(request):
#     if request.session.has_key("name617826782"):
#         nav1 = request.session["name617826782"]
#         nav2 = "/"
#         nav3 = "退出"
#         nav4 = "/logout"
#     else:
#         nav1 = "注册"
#         nav2 = "/reg"
#         nav3 = "登录"
#         nav4 = "/login"
#     typename = Typemsg.objects.values("id", "typename")
#     article = Article.objects.values("id", "title", "author", "detail")[:20]
#     return render(request, "index.html",
#                   {"article": article, "typename": typename, "nav1": nav1, "nav2": nav2, "nav3": nav3, "nav4": nav4})


def alist(request):
    if request.session.has_key("name617826782"):
        nav1 = request.session["name617826782"]
        nav2 = "/"
        nav3 = "退出"
        nav4 = "/logout"
    else:
        nav1 = "注册"
        nav2 = "/reg"
        nav3 = "登录"
        nav4 = "/login"
    typename = Typemsg.objects.values("id", "typename")
    article = Article.objects.values("id", "title", "author", "detail")
    return render(request, "list.html",
                  {"article": article, "typename": typename, "nav1": nav1, "nav2": nav2, "nav3": nav3, "nav4": nav4})


def postarticles(request):
    if request.session.has_key('name617826782') == False:
        return HttpResponseRedirect('/login')
    else:
        nav1 = request.session['name617826782']
        nav2 = "/"
        nav3 = "退出"
        nav4 = "/logout"
    # 查询所有类别ID与名称
    typeall = Typemsg.objects.values("id", "typename")
    typeid = []
    typename = []
    for item in typeall:
        typeid.append(item["id"])
        typename.append(item["typename"])
    typeidandname = zip(typeid, typename)
    # 查询当前UID
    user = list(Usermsg.objects.filter(name=request.session['name617826782']).values())[0]
    uid = user["id"]
    uname = user["name"]
    isadmin = user["isadmin"]
    if (not isadmin):
        return HttpResponseRedirect("/")
    if request.method == "POST":
        content = request.POST["content"]
        thistypeid = request.POST["typeid"]
        postname = request.POST["title"]
        detail = request.POST["detail"]
        Article.objects.create(title=postname, content=content, tid=thistypeid, uid=uid, author=uname, detail=detail)
        return HttpResponseRedirect('/')
    return render(request, 'postarticles.html',
                  {"typeidandname": typeidandname, "nav1": nav1, "nav2": nav2, "nav3": nav3, "nav4": nav4})

def generate_random_name():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return timestamp + ".jpg"
