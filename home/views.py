import datetime
import json
import os
import zipfile

from django.http import HttpResponse
from django.shortcuts import render

from SemanticCorrect import ComputeDistance

# 取20个形似字
print("读取全局字典")
global_dic = ComputeDistance.load_dict('SemanticCorrect/hei_20.json')

# 设置本地运行
local_start = False

if local_start:
    print("本地运行")
else:
    print("服务器运行")

from .utils import Ocr
from .utils import OcrForVat


# 批量上传获取文件列表
def getFileList(request):
    if request.method == "POST":
        obj = request.FILES.get('fapiao')

        # 随机文件名
        filename, zip_dir = generate_random_name(obj.name)

        file_path = os.path.join('upload', filename)
        full_path = os.path.join('allstatic', file_path)
        f = open(full_path, 'wb')
        for chunk in obj.chunks():
            f.write(chunk)
        f.close()

        file_list = []

        # 是否是zip文件，批量
        if os.path.splitext(full_path)[1] == '.zip':
            file_zip = zipfile.ZipFile(full_path, 'r')

            upload_dir = os.path.join('allstatic/upload', zip_dir)
            out_dir = os.path.join('allstatic/out', zip_dir)
            line_dir = os.path.join('allstatic/line', zip_dir)

            for file in file_zip.namelist():
                if file.endswith('.jpg') or \
                        file.endswith('.jpeg') or \
                        file.endswith('.png') or \
                        file.endswith('.bmp'):

                    # 创建三个目录
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

                    file_zip.extract(file, upload_dir)
                    file_with_zipfold = os.path.join(zip_dir, file)
                    file_list.append(file_with_zipfold)
            file_zip.close()
            os.remove(full_path)
        else:
            # 单个处理
            file_list.append(filename)

        print(file_list)

        try:
            ret = {
                'status': True,
                'path': file_path,
                'out': file_list
            }
        except Exception as e:
            print(e)
            ret = {'status': False, 'path': file_path, 'out': str(e)}

        return HttpResponse(json.dumps(ret))


# 专票
def ocrForVat(request):
    if request.method == 'GET':
        return render(request, 'ocrForVat.html')
    elif request.method == "POST":
        # obj = request.FILES.get('fapiao')
        filename = request.POST['fileInZip']

        # 文件已通过getFileList方法上传到upload目录，此时不需要上传了
        file_path = os.path.join('upload', filename)
        line_filename = os.path.join('line', filename)

        full_path = os.path.join('allstatic', file_path)

        try:
            json_result = OcrForVat.init(full_path)
            ret = {
                'status': True,
                'path': file_path,
                'line': line_filename,
                'result': json.loads(str(json_result).replace("'", "\""))
            }
        except Exception as e:
            print(e)
            ret = {'status': False, 'path': file_path, 'out': str(e)}

        return HttpResponse(json.dumps(ret))


# 首页
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
        type = request.GET['type']
        return render(request, 'ocr.html', {'type': type})
    elif request.method == "POST":
        filename = request.POST['fileInZip']
        # 车票类型：blue，excess，red
        type = request.POST['type']

        file_path = os.path.join('upload', filename)
        out_filename = os.path.join('out', filename)
        line_filename = os.path.join('line', filename)

        try:
            _, flag, line_result = Ocr.surface(file_path, type)
            # color = "蓝底车票" if flag == 1 else "红底车票"
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
        type = request.GET['type']
        return render(request, 'detect.html', {'type': type})
    elif request.method == "POST":
        filename = request.POST['fileInZip']
        # 车票类型：blue，excess，red
        type = request.POST['type']

        file_path = os.path.join('upload', filename)
        out_filename = os.path.join('out', filename)
        line_filename = os.path.join('line', filename)

        try:
            _, flag, line_result = Ocr.surface(file_path, type)
            # color = "蓝底车票" if flag == 1 else "红底车票"
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
def generate_random_name(file_name):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    _, ext = os.path.splitext(file_name)

    return timestamp + ext, timestamp


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
