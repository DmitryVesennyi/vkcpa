# -*- coding: utf-8 -*-
from django.contrib import admin
from exeption_info.models import TracebagModel
from datetime import datetime
from django.apps import AppConfig

@admin.register(TracebagModel)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ['format_date', 'get_user_session']
    
    def format_date(self, obj):
        return obj.date.strftime('%d.%m.%Y')
    format_date.short_description = u'Дата'
    format_date.admin_order_field = '-date'

    def get_user_session(self, obj):
        if obj.user_session:
            return obj.user_session
        else:
            return u'нет'
    get_user_session.short_description = u'Юзер'
    get_user_session.admin_order_field = '-user_session'
    
class InterstoreAppConfig(AppConfig):
    name = "exeption_info"
    verbose_name = u"В помощь супер-админу"
# Register your models here.
