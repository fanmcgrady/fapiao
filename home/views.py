import datetime
import json
import os

from django.http import HttpResponse
from django.shortcuts import render

from SemanticCorrect import ComputeDistance
from .models import Img
from .utils import Ocr
from .utils import OcrForVat

# 取20个形似字
print("读取全局字典")
global_dic = ComputeDistance.load_dict('SemanticCorrect/hei_20.json')


def ocrForVat(request):
    OcrForVat.init()
    return render(request, 'index.html')

# Create your views here.
def index(request):
    return render(request, 'index.html')


# 识别demo
def ocrWithoutSurface(request):
    if request.method == "POST":
        out_filename = request.POST["outFilename"]
        out_filename = os.path.join('allstatic', out_filename)

        line_result = request.POST["lineResult"]

        try:
            result, origin = Ocr.ocrWithoutSurface(out_filename, json.loads(line_result.replace("'", "\"")))

            result_dict = json.loads(result)
            origin_dict = json.loads(origin)

            # 找出两个字典不同
            diff_dict = {}
            for k in origin_dict:
                if result_dict['invoice'][k] != origin_dict[k]:
                    diff_dict[k] = "{} -> {}".format(origin_dict[k], result_dict['invoice'][k])

            ret = {
                'status': True,
                'out': out_filename,
                'result': result_dict,
                'diff': diff_dict
            }
        except Exception as e:
            print(e)
            ret = {'status': False, 'out': str(e)}

    return HttpResponse(json.dumps(ret, indent=2))


# 识别demo
def ocr(request):
    if request.method == 'GET':
        img_list = Img.objects.all()
        type = request.GET['type']
        return render(request, 'ocr.html', {'img_list': img_list, 'type': type})
    elif request.method == "POST":
        obj = request.FILES.get('fapiao')
        # 车票类型：blue，excess，red
        type = request.POST['type']

        # 随机文件名
        filename = generate_random_name()

        file_path = os.path.join('upload', filename)
        out_filename = os.path.join('out', filename)
        line_filename = os.path.join('line', filename)

        full_path = os.path.join('allstatic', file_path)
        f = open(full_path, 'wb')
        for chunk in obj.chunks():
            f.write(chunk)
        f.close()

        try:
            _, flag, line_result = Ocr.surface(file_path, type)
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
        type = request.GET['type']
        return render(request, 'detect.html', {'img_list': img_list, 'type': type})
    elif request.method == "POST":
        obj = request.FILES.get('fapiao')
        # 车票类型：blue，excess，red
        type = request.POST['type']

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
            _, flag, line_result = Ocr.surface(file_path, type)
            color = "蓝底车票" if flag == 1 else "红底车票"
            ret = {
                'status': True,
                'path': file_path,
                'out': out_filename,
                'line': line_filename,
                'color': color,
                'lineResult': str(line_result)
            }
            Img.objects.create(path=file_path, out=out_filename, line=line_filename, color=color, type=type)
        except Exception as e:
            print(e)
            ret = {'status': False, 'path': file_path, 'out': str(e)}

        return HttpResponse(json.dumps(ret))


# 按日期生成文件名
def generate_random_name():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return timestamp + ".jpg"


##################
# 其他系统外功能
def resume(request):
    files = os.listdir("allstatic/resume")

    if request.method == 'GET':
        return render(request, 'resume.html', {'count': len(files)})
    elif request.method == "POST":
        resume = request.FILES.get('resume')

        file_path = os.path.join('resume', resume.name)
        full_path = os.path.join('allstatic', file_path)

        f = open(full_path, 'wb')
        for chunk in resume.chunks():
            f.write(chunk)
        f.close()

        try:
            ret = {
                'status': True,
                'path': resume.name,
                'count': len(files) + 1
            }
        except Exception as e:
            print(e)
            ret = {'status': False, 'path': file_path, 'out': str(e)}

        return HttpResponse(json.dumps(ret))

#
# def article(request, aid):
#     thisarticle = list(Article.objects.filter(id=aid).values("id", "title", "author", "content"))[0]
#     return render(request, "detail.html", {"thisarticle": thisarticle, })
#
#
# def reg(request):
#     if request.session.has_key("name617826782"):
#         return HttpResponseRedirect("/")
#     if request.method == "POST":
#         name = request.POST["name"]
#         passwd = request.POST["passwd"]
#         email = request.POST["email"]
#         phone = request.POST["phone"]
#         Usermsg.objects.create(name=name, passwd=passwd, email=email, phone=phone, isadmin=0)
#         return HttpResponse("注册成功！")
#     return render(request, "reg.html")
#
#
# def login(request):
#     if request.session.has_key("name617826782"):
#         return HttpResponseRedirect("/")
#     if request.method == "POST":
#         name = request.POST["name"]
#         passwd = request.POST["passwd"]
#         islogin = Usermsg.objects.filter(name__exact=name, passwd__exact=passwd)
#         if islogin:
#             request.session["name617826782"] = name
#             return HttpResponseRedirect("/")
#         else:
#             return HttpResponse("登录失败！")
#     return render(request, "login.html")
#
#
# def logout(request):
#     del request.session["name617826782"]
#     return HttpResponseRedirect("/")


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


# def alist(request):
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
#     article = Article.objects.values("id", "title", "author", "detail")
#     return render(request, "list.html",
#                   {"article": article, "typename": typename, "nav1": nav1, "nav2": nav2, "nav3": nav3, "nav4": nav4})
#
#
# def postarticles(request):
#     if request.session.has_key('name617826782') == False:
#         return HttpResponseRedirect('/login')
#     else:
#         nav1 = request.session['name617826782']
#         nav2 = "/"
#         nav3 = "退出"
#         nav4 = "/logout"
#     # 查询所有类别ID与名称
#     typeall = Typemsg.objects.values("id", "typename")
#     typeid = []
#     typename = []
#     for item in typeall:
#         typeid.append(item["id"])
#         typename.append(item["typename"])
#     typeidandname = zip(typeid, typename)
#     # 查询当前UID
#     user = list(Usermsg.objects.filter(name=request.session['name617826782']).values())[0]
#     uid = user["id"]
#     uname = user["name"]
#     isadmin = user["isadmin"]
#     if (not isadmin):
#         return HttpResponseRedirect("/")
#     if request.method == "POST":
#         content = request.POST["content"]
#         thistypeid = request.POST["typeid"]
#         postname = request.POST["title"]
#         detail = request.POST["detail"]
#         Article.objects.create(title=postname, content=content, tid=thistypeid, uid=uid, author=uname, detail=detail)
#         return HttpResponseRedirect('/')
#     return render(request, 'postarticles.html',
#                   {"typeidandname": typeidandname, "nav1": nav1, "nav2": nav2, "nav3": nav3, "nav4": nav4})
