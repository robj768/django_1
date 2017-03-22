from django.contrib import admin
from .models import Category, Page
from main.models import UserProfile
# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name',)


class PageAdmin(admin.ModelAdmin):
	list_display = ('title', 'category', 'url')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)

