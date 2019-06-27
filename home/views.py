# 设置本地运行
# local_start = True
local_start = False

import sys

# 判断运行方式
if local_start:
    print("本地运行")
    sys.path.append("ocr")
    import ComputeDistance

    # 取20个形似字
    print("读取全局字典")
    global_dic = ComputeDistance.load_dict('ocr/hei_20.json')

else:
    print("服务器运行")
    # 加载黄政的代码
    sys.path.append("/home/ocr/organize")
    # sys.path.append("/home/huangzheng/ocr")

    # import fp.multi.muldetect

    # detr = fp.multi.muldetect.DetectMultiFp()
    # print("加载多票面识别完成")

    import ComputeDistance
    import os

    # 设置只用前两个GPU
    os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"

    # 取20个形似字
    print("读取全局字典")
    global_dic = ComputeDistance.load_dict('/home/ocr/organize/hei_20.json')
    # global_dic = ComputeDistance.load_dict('/home/huangzheng/ocr/hei_20.json')

    # import Ocr
    # import OcrForVat
    import OcrForSpecVat
    import API

    print("加载模型")
    # from connector import connecter

    # from connector import PipelineInit

    # global_pipeline = PipelineInit.PipelineInit()

import datetime
import json
import zipfile
import base64

from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render

import shutil
import traceback
from .models import Bug
from .models import BugTwo
from .models import BugThree

import cv2



# 多发票检测
# def multi(request):
#     if request.method == "GET":
#         return render(request, 'multi.html')
#     elif request.method == "POST":
#         try:
#             # POST压缩包中的文件
#             filename = request.POST['fileInZip']
#
#             # 文件已通过getFileList方法上传到upload目录，此时不需要上传了
#             # 拼接目录
#             file_path = os.path.join('upload', filename)
#             line_filename = os.path.join('line', filename)
#
#             full_path = os.path.join('allstatic', file_path)
#             line_path = os.path.join('allstatic', line_filename)
#         except Exception as e:
#             traceback.print_exc()
#
#         try:
#             # 识别
#             im = cv2.imread(full_path, 1)
#             res = detr(im)
#             for name, score, rect in res:
#                 print('name:', name)
#                 print('score:', score)
#                 print('rect:', rect)
#
#             # draw results
#             im = fp.multi.muldetect.draw_result(im, res)
#             cv2.imwrite(line_path, im)
#
#             ret = {
#                 'status': True,
#                 'path': file_path,
#                 'line': line_filename,
#                 'result': str(res)
#             }
#
#         # 打印错误原因
#         except Exception as e:
#             print(e)
#             ret = {'status': False, 'path': file_path, 'result': str(e)}
#
#         return HttpResponse(json.dumps(ret))

# API
def QR_API(request):
    if request.method == "POST":
        base64_data = request.POST['picture']
        # 随机文件名
        filename, _ = generate_random_name()
        # 拼接存放位置路径
        file_path = os.path.join('upload', filename)
        full_path = os.path.join('allstatic', file_path)

        # 文件写入
        with open(full_path, "wb") as f:
            f.write(base64.b64decode(base64_data))

        try:
            # 识别 给前端传值
            json_result = API.runQR(full_path)

            if json_result is None:
                ret = {
                    "returnStateInfo": {
                        "returnCode": "9999",
                        "returnMessage": "处理失败: 二维码识别不清晰，识别失败"
                    },
                    "invoice": ""
                }
            else:
                ret = {
                    "returnStateInfo": {
                        "returnCode": "0000",
                        "returnMessage": "处理成功"
                    },
                    "invoice": json.loads(str(json_result).replace("'", "\""))
                }

        # 打印错误原因
        except Exception as e:
            print(e)
            ret = {
                "returnStateInfo": {
                    "returnCode": "9999",
                    "returnMessage": "处理失败:" + str(e)
                },
                "invoice": ""
            }

        return JsonResponse(ret)


def Type_API(request):
    if request.method == "POST":
        base64_data = request.POST['picture']
        # 随机文件名
        filename, _ = generate_random_name()
        # 拼接存放位置路径
        file_path = os.path.join('upload', filename)
        full_path = os.path.join('allstatic', file_path)

        # 文件写入
        with open(full_path, "wb") as f:
            f.write(base64.b64decode(base64_data))

        try:
            # 识别 给前端传值
            type = API.runType(full_path)
            # ['quota', 'elect', 'airticket', 'special', 'trainticket']
            # 01 *增值税专用发票
            # 02 货运运输业增值税专用发票
            # 03 机动车销售统一发票
            # 04 *增值税普通发票
            # 10 *增值税普通发票(电子)
            # 11 *增值税普通发票(卷式)
            # 91 出租车票
            # 92 *火车票
            # 93 *飞机票
            # 94 汽车票
            # 95 *定额发票
            # 96 长途汽车票
            # 97 通用机打发票
            # 98 政府非税收收入一般缴款书
            # 00 其他类型
            # 注：增值税票目前不能区分具体种类，可统一返回01

            if type == 'quota':
                type = "95"
            elif type == 'elect':
                type = "10"
            elif type == 'airticket':
                type = "93"
            elif type == 'special':
                type = "01"
            elif type == 'trainticket':
                type = "92"
            else:
                type = "00"

            ret = {
                "returnCode": "0000",
                "returnMessage": "处理成功",
                "invoiceType": type
            }

        # 打印错误原因
        except Exception as e:
            print(e)
            ret = {
                "returnCode": "9999",
                "returnMessage": "处理失败:" + str(e),
                "invoiceType": type
            }

        return JsonResponse(ret)


# 专票统一入口
def ocrForSpecVat(request):
    if request.method == "POST":
        # POST压缩包中的文件
        filename = request.POST['fileInZip']

        # 文件已通过getFileList方法上传到upload目录，此时不需要上传了
        # 拼接目录
        file_path = os.path.join('upload', filename)
        line_filename = os.path.join('line', filename)

        full_path = os.path.join('allstatic', file_path)

        try:
            # 识别 给前端传值
            json_result, timer, type = OcrForSpecVat.init(full_path)

            ## type in ['quota', 'elect', 'airticket', 'special', 'trainticket']
            if json_result == '':
                json_result = None
            ## type = 'special'
            else:
                json_result = json.loads(str(json_result).replace("'", "\""))

            ret = {
                'status': True,
                'path': file_path,
                'line': line_filename,
                'result': json_result,
                'timer': timer.__str__(),
                'type': type
            }

        # 打印错误原因
        except Exception as e:
            print(e)
            ret = {'status': False, 'path': file_path, 'result': str(e)}

        return HttpResponse(json.dumps(ret))


# 列出bug
def listBugs(request):
    if request.method == 'GET':
        bug_list = Bug.objects.all()
        return render(request, 'bug.html', {'bug_list': bug_list})
    # 上报错误信息
    elif request.method == "POST":
        try:
            path = request.POST['path']
            line = request.POST['line']
            info = request.POST['info']
            Bug.objects.create(path=path, line=line, info=info)
            ret = {'status': True}
        except Exception as e:
            ret = {'status': False}

        return HttpResponse(json.dumps(ret))


def listBugsTwo(request):
    if request.method == 'GET':
        bugTwo_list = BugTwo.objects.all()
        return render(request, 'bugTwo.html', {'bugTwo_list': bugTwo_list})
    # 上报错误信息
    elif request.method == "POST":
        try:
            path = request.POST['path']
            out = request.POST['out']
            info = request.POST['info']
            BugTwo.objects.create(path=path, out=out, info=info)
            ret = {'status': True}
        except Exception as e:
            ret = {'status': False}

        return HttpResponse(json.dumps(ret))


def listBugsThree(request):
    if request.method == 'GET':
        bugThree_list = BugThree.objects.all()
        return render(request, 'bugThree.html', {'bugThree_list': bugThree_list})
    # 上报错误信息
    elif request.method == "POST":
        try:
            path = request.POST['path']
            out = request.POST['out']
            line = request.POST['line']
            info = request.POST['info']
            BugThree.objects.create(path=path, out=out, line=line, info=info)
            ret = {'status': True}
        except Exception as e:
            ret = {'status': False}

        return HttpResponse(json.dumps(ret))


def deleteInfo(request):
    if request.method == "POST":
        try:
            bugid = request.POST['id']
            Bug.objects.get(id=bugid).delete()
            ret = {'status': True}

        except Exception as e:
            print(e)
            ret = {'status': False}

        return HttpResponse(json.dumps(ret))


def deleteInfoTwo(request):
    if request.method == "POST":
        try:
            bugid = request.POST['id']
            BugTwo.objects.get(id=bugid).delete()
            ret = {'status': True}

        except Exception as e:
            print(e)
            ret = {'status': False}

        return HttpResponse(json.dumps(ret))


def deleteInfoThree(request):
    if request.method == "POST":
        try:
            bugid = request.POST['id']
            BugThree.objects.get(id=bugid).delete()
            ret = {'status': True}

        except Exception as e:
            print(e)
            ret = {'status': False}

        return HttpResponse(json.dumps(ret))


# 批量上传获取文件列表
def getFileList(request):
    if request.method == "POST":
        # 是否使用服务器上的文件，第二个参数是默认值false
        try:
            use_server_path = request.POST.get('useServerPath', 'false')

            if use_server_path == 'true':
                # 随机文件名
                server_path = request.POST['pathInput']
                filename, zip_dir = generate_random_name(server_path)
                # 拼接存放位置路径
                file_path = os.path.join('upload', filename)
                full_path = os.path.join('allstatic', file_path)

                shutil.copyfile(server_path, full_path)  # 复制文件
            else:
                obj = request.FILES.get('fapiao')
                # 随机文件名
                filename, zip_dir = generate_random_name(obj.name)
                # 拼接存放位置路径
                file_path = os.path.join('upload', filename)
                full_path = os.path.join('allstatic', file_path)

                # 上传文件写入
                f = open(full_path, 'wb')
                for chunk in obj.chunks():
                    f.write(chunk)
                f.close()
        except Exception as e:
            traceback.print_exc()

        file_list = []

        try:
            # 是否是zip文件，批量
            if os.path.splitext(full_path)[1] == '.zip':
                # 读zip文件
                file_zip = zipfile.ZipFile(full_path, 'r')
                # 拼接处理后图片路径
                upload_dir = os.path.join('allstatic/upload', zip_dir)
                out_dir = os.path.join('allstatic/out', zip_dir)
                line_dir = os.path.join('allstatic/line', zip_dir)

                # 遍历压缩包内文件 判断扩展名只要图片
                for file in file_zip.namelist():
                    if file.endswith('.jpg') or \
                            file.endswith('.jpeg') or \
                            file.endswith('.png') or \
                            file.endswith('.bmp'):

                        # 创建三个目录 存放压缩包内所有图片的分析后文件
                        upload_file = os.path.join(upload_dir, file)
                        upload_file_root, _ = os.path.split(upload_file)
                        out_file = os.path.join(out_dir, file)
                        out_file_root, _ = os.path.split(out_file)
                        line_file = os.path.join(line_dir, file)
                        line_file_root, _ = os.path.split(line_file)

                        if not os.path.exists(upload_file_root):
                            os.makedirs(upload_file_root)
                        if not os.path.exists(out_file_root):
                            os.makedirs(out_file_root)
                            os.makedirs(os.path.join(out_file_root, 'tmp'))
                        if not os.path.exists(line_file_root):
                            os.makedirs(line_file_root)

                        # 解压到上传目录
                        file_zip.extract(file, upload_dir)
                        file_with_zipfold = os.path.join(zip_dir, file)
                        file_list.append(file_with_zipfold)
                file_zip.close()
                # 清除完整路径
                os.remove(full_path)
            else:
                # 单个处理
                file_list.append(filename)

            # 向前端传值
            ret = {
                'status': True,
                'path': file_path,
                'out': file_list
            }
            # 打印错误内容
        except Exception as e:
            print(e)
            ret = {'status': False, 'path': file_path, 'out': str(e)}

        return HttpResponse(json.dumps(ret))


# 专票
def ocrForVat(request):
    if request.method == 'GET':
        # GET车票类型
        type = request.GET['type']
        if type == 'special':
            typeText = "专票"
        elif type == 'normal':
            typeText = "普票"
        elif type == 'elec':
            typeText = "电子票"
        else:
            typeText = "错误"
        # GET方法跳转到ocrForVat.html界面
        return render(request, 'ocrForVat.html', {'type': type, 'typeText': typeText})
    elif request.method == "POST":
        # 发票类型：special，normal，elec
        type = request.POST['type']
        # POST压缩包中的文件
        filename = request.POST['fileInZip']

        # 文件已通过getFileList方法上传到upload目录，此时不需要上传了
        # 拼接目录
        file_path = os.path.join('upload', filename)
        line_filename = os.path.join('line', filename)

        full_path = os.path.join('allstatic', file_path)

        try:
            # 识别 给前端传值
            json_result, timer = OcrForVat.init(full_path, type=type)

            ret = {
                'status': True,
                'path': file_path,
                'line': line_filename,
                'result': json.loads(str(json_result).replace("'", "\"")),
                'timer': timer.__str__()
            }

        # 打印错误原因
        except Exception as e:
            print(e)
            ret = {'status': False, 'path': file_path, 'result': str(e)}

        return HttpResponse(json.dumps(ret))


# 首页
def index(request):
    return render(request, 'allInOne.html')


def old(request):
    return render(request, 'index.html')


# 识别demo
def ocrWithoutSurface(request):
    if request.method == "POST":
        # POST矫正后的图片
        out_filename = request.POST["outFilename"]
        out_filename = os.path.join('allstatic', out_filename)

        # POST行提取结果
        line_result = request.POST["lineResult"]

        path = request.POST["path"]

        try:
            # 行提取结果语义矫正 语义识别
            result, origin = Ocr.ocrWithoutSurface(out_filename, json.loads(line_result.replace("'", "\"")))

            result_dict = json.loads(result)
            origin_dict = json.loads(origin)

            # 找出两个字典不同
            diff_dict = {}
            for k in origin_dict:
                if result_dict['invoice'][k] != origin_dict[k]:
                    diff_dict[k] = "{} -> {}".format(origin_dict[k], result_dict['invoice'][k])
            # 向前端传值
            ret = {
                'status': True,
                'out': out_filename,
                'result': result_dict,
                'diff': diff_dict,
                'path': path
            }
        except Exception as e:
            print(e)
            ret = {'status': False, 'path': path, 'out': str(e)}

    return HttpResponse(json.dumps(ret, indent=2))


# 识别demo
def ocr(request):
    if request.method == 'GET':
        # GET车票类型
        type = request.GET['type']
        # 返回ocr.html界面 传参type
        return render(request, 'ocr.html', {'type': type})
    elif request.method == "POST":
        # POST压缩包中的文件
        filename = request.POST['fileInZip']
        # 车票类型：blue，excess，red
        type = request.POST['type']

        # 拼接目录
        file_path = os.path.join('upload', filename)
        out_filename = os.path.join('out', filename)
        line_filename = os.path.join('line', filename)

        try:
            # 矫正 行提取
            _, flag, line_result = Ocr.surface(file_path, type)
            # 传值
            ret = {
                'status': True,
                'path': file_path,
                'out': out_filename,
                'line': line_filename,
                'lineResult': str(line_result)
            }
        except Exception as e:
            print(e)
            ret = {'status': False, 'path': file_path, 'out': str(e)}

        return HttpResponse(json.dumps(ret))


# 矫正demo，detect.html页面调用
def surface(request):
    if request.method == 'GET':
        # GET车票类型
        type = request.GET['type']
        # 返回detect.html界面并传参type
        return render(request, 'detect.html', {'type': type})
    elif request.method == "POST":
        # POST压缩包中的文件
        filename = request.POST['fileInZip']
        # 车票类型：blue，excess，red
        type = request.POST['type']

        # 拼接目录
        file_path = os.path.join('upload', filename)
        out_filename = os.path.join('out', filename)
        line_filename = os.path.join('line', filename)

        try:
            # 矫正 行提取
            _, flag, line_result = Ocr.surface(file_path, type)
            # 传值
            ret = {
                'status': True,
                'path': file_path,
                'out': out_filename,
                'line': line_filename
            }
        except Exception as e:
            print(e)
            ret = {'status': False, 'path': file_path, 'out': str(e)}

        return HttpResponse(json.dumps(ret))


# 按日期生成文件名
def generate_random_name(file_name=None):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    if file_name is None:
        ext = ".jpg"
    else:
        _, ext = os.path.splitext(file_name)

    return timestamp + ext, timestamp
