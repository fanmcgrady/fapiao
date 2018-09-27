import datetime
import json
import os

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from SemanticCorrect import ComputeDistance
from .models import Article
from .models import Img
from .models import Typemsg
from .models import Usermsg
from .utils import Ocr

# 取20个形似字
print("读取全局字典")
global_dic = ComputeDistance.load_dict('SemanticCorrect/hei_20.json')


# 请求显示首页index.html
def index(request):
    return render(request, 'index.html')


# 识别demo
def ocrWithoutSurface(request):
    if request.method == "POST":
        # 图片文件存入allstatic目录
        out_filename = request.POST["outFilename"]
        out_filename = os.path.join('allstatic', out_filename)

        line_result = request.POST["lineResult"]

        try:
            result, origin = Ocr.ocrWithoutSurface(out_filename, json.loads(line_result.replace("'", "\"")))
            # 解码result和origin对象
            result_dict = json.loads(result)
            origin_dict = json.loads(origin)

            # 找出两个字典不同
            diff_dict = {}
            # 遍历链表
            for k in origin_dict:
                # 找到不同时
                if result_dict['invoice'][k] != origin_dict[k]:
                    # 格式化输出字符串形如origin_dict[k] -> result_dict['invoice'][k]
                    diff_dict[k] = "{} -> {}".format(origin_dict[k], result_dict['invoice'][k])

            # 定义子程序返回字典ret
            ret = {
                'status': True,
                'out': out_filename,
                'result': result_dict,
                'diff': diff_dict
            }
        except Exception as e:
            # 发生错误修改字典值false 输出错误原因
            print(e)
            ret = {'status': False, 'out': str(e)}

    # 返回字典编码成的Json字符串
    return HttpResponse(json.dumps(ret, indent=2))


# 识别demo
def ocr(request):
    # GET方法
    if request.method == 'GET':
        # 全部的图片
        img_list = Img.objects.all()
        # 返回ocr.html界面 全部图片集是用于渲染呈现的数据
        return render(request, 'ocr.html', {'img_list': img_list})
    # POST方法
    elif request.method == "POST":
        # 上传图片须以name='fapiao'上传  (if not obj:???)
        obj = request.FILES.get('fapiao')

        # 随机文件名
        filename = generate_random_name()

        file_path = os.path.join('upload', filename)
        out_filename = os.path.join('out', filename)
        line_filename = os.path.join('line', filename)

        # 完整路径 +/allstatic
        full_path = os.path.join('allstatic', file_path)
        # 进入路径full_path 可写
        f = open(full_path, 'wb')
        # 该文件路径写入上传图片
        for chunk in obj.chunks():
            f.write(chunk)
        f.close()

        try:
            # 调用矫正函数 默认蓝票
            _, flag, line_result = Ocr.surface(file_path)
            color = "蓝底车票" if flag == 1 else "红底车票"
            ret = {
                'status': True,
                'path': file_path,
                'out': out_filename,
                'line': line_filename,
                'color': color,
                'lineResult': str(line_result)
            }
        except Exception as e:
            print(e)
            ret = {'status': False, 'path': file_path, 'out': str(e)}

        return HttpResponse(json.dumps(ret))


# 矫正demo，detect.html页面调用
def surface(request):
    if request.method == 'GET':
        img_list = Img.objects.all().order_by('-id')
        return render(request, 'detect.html', {'img_list': img_list})
    elif request.method == "POST":
        obj = request.FILES.get('fapiao')

        # 随机文件名
        filename = generate_random_name()

        file_path = os.path.join('upload', filename)
        out_filename = os.path.join('out', filename)
        line_filename = os.path.join('line', filename)

        # file_path = os.path.join('upload', obj.name)

        full_path = os.path.join('allstatic', file_path)
        f = open(full_path, 'wb')
        for chunk in obj.chunks():
            f.write(chunk)
        f.close()

        try:
            _, flag, line_result = Ocr.surface(file_path)
            color = "蓝底车票" if flag == 1 else "红底车票"
            ret = {
                'status': True,
                'path': file_path,
                'out': out_filename,
                'line': line_filename,
                'color': color,
                'lineResult': str(line_result)
            }
            Img.objects.create(path=file_path, out=out_filename, line=line_filename, color=color)
        except Exception as e:
            print(e)
            ret = {'status': False, 'path': file_path, 'out': str(e)}

        return HttpResponse(json.dumps(ret))


def article(request, aid):
    thisarticle = list(Article.objects.filter(id=aid).values("id", "title", "author", "content"))[0]
    return render(request, "detail.html", {"thisarticle": thisarticle, })

# 注册
def reg(request):
    # 验证键值
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

# 登录验证
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

# 注销
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
