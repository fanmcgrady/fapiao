"""fapiao URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url

from home import views as home_views


urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    # url(r'^articles/(.*?)$',home_views.article),
    # url(r"^reg$",home_views.reg),
    # url(r"^login$", home_views.login),
    #
    # url(r"^logout$", home_views.logout),
    # url(r"^list$", home_views.alist),
    # url(r"^postarticles$", home_views.postarticles),

    # 统一入口
    url(r"^$", home_views.index),
    url(r"^ocrForSpecVat$", home_views.ocrForSpecVat),

    # API
    url(r"^qr_api$", home_views.QR_API),
    url(r"^type_api$", home_views.Type_API),

    # 原首页
    url(r"^old$", home_views.old),

    url(r"^detect$", home_views.surface),
    url(r"^ocr$", home_views.ocr),
    url(r"^ocrWithoutSurface$", home_views.ocrWithoutSurface),
    url(r"^ocrForVat$", home_views.ocrForVat),
    url(r"^bug$", home_views.listBugs),
    url(r"^bugTwo$", home_views.listBugsTwo),
    url(r"^bugThree$", home_views.listBugsThree),
    url(r"^deleteInfo$", home_views.deleteInfo),
    url(r"^deleteInfoTwo$", home_views.deleteInfoTwo),
    url(r"^deleteInfoThree$", home_views.deleteInfoThree),

    # 批量上传
    url(r"^getFileList$", home_views.getFileList),

    # 多票面检测
    url(r"^multi1$", home_views.multi)
]

