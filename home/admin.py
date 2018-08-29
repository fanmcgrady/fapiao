from django.contrib import admin
from .models import Usermsg
from .models import Article
from .models import Typemsg
# Register your models here.
class UsermsgAdmin(admin.ModelAdmin):
    list_display = ("name","email","phone","isadmin")
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title","author","detail","content","uid","tid")
class TypemsgAdmin(admin.ModelAdmin):
    list_display = ("typename",)
admin.site.register(Usermsg,UsermsgAdmin)
admin.site.register(Article,ArticleAdmin)
admin.site.register(Typemsg,TypemsgAdmin)