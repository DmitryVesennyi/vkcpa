# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib import admin
from vkcpa.models import Users, Groups, StaticGroups, UserGroup
from django.db import models
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from vkcpa.UserVk2 import AppMixins
from django.contrib.contenttypes.models import ContentType
from datetime import datetime

#admin.site.register(Users)
#admin.site.register(Groups)
#admin.site.register(UserGroup)
#admin.site.register(StaticGroups)

class UserGroupInline(admin.StackedInline):
    model = UserGroup

@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'get_group_id', 'countUser', 'group_sort', 'group_behavior', 'plus_html', 'minus_html', 'queue', 'format_date', 'get_impression']
    
    def get_name(self, obj):
        return obj.name
    get_name.allow_tags = True
    get_name.short_description = u'Группа'
    get_name.admin_order_field = '-name'
    
    def format_date(self, obj):
        return obj.start_date.strftime('%d.%m')
    format_date.short_description = u'Дт'
    format_date.admin_order_field = '-start_date'
    def countUser(self, obj):
        try:
            count_user = obj.users_set.all()
        except:
            return u'-'
        else:
            return len(count_user)
            #count_u = len(count_user)

    def get_banan(self, obj):
        if obj.banan:
            status = '<i class="fa fa-exclamation fa-lg text-danger" aria-hidden="true"></i>'
        else:
            status = '<i class="fa fa-check fa-lg text-success" aria-hidden="true"></i>'
        return status
    def get_urls(self):
        urls = super(UserGroupAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^plus/(\d+)/$', self.admin_site.admin_view(self.plus_queue)),
            url(r'^minus/(\d+)/$', self.admin_site.admin_view(self.minus_queue)),)
        return my_urls + urls
    def _get_absolute_url(self):
        content_type = ContentType.objects.get_for_model(UserGroup)
        return reverse ("admin:%s_%s_changelist"%(content_type.app_label, content_type.model))
    def plus_queue(self, request, obj):
        try:
            obj_queue = UserGroup.objects.get(id = obj)
        except UserGroup.DoesNotExist:
            return redirect(self._get_absolute_url())
        try:
            group = Groups.objects.get(group_info = obj_queue)
        except Groups.DoesNotExist:
            Groups.objects.create(group_info = obj_queue, sort_position = 0, behavior = 1)
            AppMixins().stack(new = 1)
            return redirect(self._get_absolute_url())
        else:
            if group.sort_position > 40 or group.behavior == 2:
                group.sort_position = 0
                group.behavior = 1
                group.save()
                AppMixins().stack(new = 1)
            else:
                obj_queue.queue += 1
                obj_queue.save()
            return redirect(self._get_absolute_url())
    def plus_html(self, obj):
        return u'<a href = "plus/%s" class="text-success" data-original-title="Добавить круг" data-toggle="tooltip"><i class="fa fa-plus" aria-hidden="true"></i></a>'%obj.id
    plus_html.short_description = u'+Кр'
    plus_html.allow_tags = True
    def minus_html(self, obj):
        return u'<a href = "minus/%s" class="text-danger" data-original-title="Отнять круг" data-toggle="tooltip"><i class="fa fa-minus" aria-hidden="true"></i></a>'%obj.id
    def minus_queue(self, request, obj):
        try:
            obj_queue = UserGroup.objects.get(id = obj)
        except UserGroup.DoesNotExist:
            return redirect(self._get_absolute_url())
        if obj_queue.queue > 0:
            obj_queue.queue -= 1
            obj_queue.save()
        return redirect(self._get_absolute_url())
    minus_html.short_description = u'-Кр'
    minus_html.allow_tags = True
    get_banan.allow_tags = True
    get_banan.short_description = u'Бан'
    get_banan.admin_order_field = u'-banan'

    countUser.short_description = u'Юз'
    #countUser.admin_order_field = '-count_u'
    #def get_link_group(self, obj):
    #    return obj.link_group
    #get_link_group.allow_tags = True
    #get_link_group.short_description = u'Ссылка'
    #get_link_group.admin_order_field = '-link_group'
    def group_sort(self, obj):
        try:
            group = Groups.objects.get(group_info = obj)
        except Groups.DoesNotExist:
            return u'-'
        else:
            return group.sort_position
    def group_behavior(self, obj):
        try:
            group = Groups.objects.get(group_info = obj)
        except Groups.DoesNotExist:
            return '<i class="fa fa-times" aria-hidden="true" data-original-title="Не участвует" data-toggle="tooltip"></i>'
        else:
            if group.behavior == 1:
                if group.sort_position < 41:
                    return '<i class="fa fa-check text-success" aria-hidden="true" data-original-title="В списке" data-toggle="tooltip"></i>'
                else:
                    return '<i class="fa fa-clock-o text-success" aria-hidden="true" data-original-title="Ожидает..." data-toggle="tooltip"></i>'
            else:
                return '<i class="fa fa-snowflake-o text-danger" aria-hidden="true" data-original-title="Выпала из списка" data-toggle="tooltip"></i>'
    group_sort.allow_tags = True
    group_behavior.allow_tags = True
    group_sort.short_description = u'Пз'
    group_behavior.short_description = 'Сст'
    #group_sort.admin_order_field = 'groups_set.sort_position'?
    def get_group_id(self, obj):
        html = '<a href="{0}" target="_blank" data-original-title="На страницу группы" data-toggle="tooltip">{1}</a>'.format(obj.link_group, obj.group_id)
        return html
    get_group_id.allow_tags = True
    get_group_id.short_description = u'Ид'
    get_group_id.admin_order_field = '-group_id'
    search_fields = ['name', 'group_id']
    fields = ('group_id', 'name', 'queue', 'count')
    def get_impression(self, obj):
        if obj.impression:
            status = '<i class="fa fa-info-circle text-danger" aria-hidden="true" data-original-title="Пауза - Лимит" data-toggle="tooltip"></i>'
        else:
            status = '<i class="fa fa-check-circle text-success" aria-hidden="true" data-original-title="В списке - < 100" data-toggle="tooltip"></i>'
        return status
    get_impression.allow_tags = True
    get_impression.short_description = u'Лмт'
    get_impression.admin_order_field = '-impression'
    
@admin.register(Groups)
class GroupsAdmin(admin.ModelAdmin):
    list_display = ['get_group_info', 'get_sort_position']

    def get_group_info(self, obj):
        return obj.group_info
    get_group_info.allow_tags = True
    get_group_info.short_description = u'Группа'
    get_group_info.admin_order_field = '-group_info'
    
    def get_sort_position(self, obj):
        return obj.sort_position
    get_sort_position.allow_tags = True
    get_sort_position.short_description = u'Место'
    get_sort_position.admin_order_field = '-sort_position'

    fields = ('sort_position', 'behavior')
    
    #def f_sort_position(self, obj):
    #    return obj.sort_position
    #f_sort_position.short_description = u'Место'
    
    
@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ['get_user_photo', 'get_name', 'format_date', 'get_user_group', 'link_group', 'get_count', '_status']
    list_select_related = True
    #inlines = [UserGroupInline]
    #list_editable = ['ban']
    def get_user_photo(self, obj):
        #html = '<img src="{0}" width="30" height="30" />'.format(obj.photo)
        link = 'https://vk.com/id%s'%obj.user_id
        html = '<a href = "{0}" target="_blank"><img src="{1}" width="30" height="30" class="img img-circle" data-original-title="На страницу ВК" data-toggle="tooltip" /></a>'.format(link, obj.photo)
        return html
    def get_name(self, obj):
        show = obj.name+' '+obj.surname
        return show
    get_name.allow_tags = True
    get_name.short_description = u'Имя'
    get_name.admin_order_field = '-name'
    def get_user_id(self, obj):
        return obj.user_id
    get_user_id.allow_tags = True
    get_user_id.short_description = u'ИдВК'
    get_user_id.admin_order_field = '-user_id'
    def get_count(self, obj):
        if obj.count:
            return obj.count
        else:
            return 0
    get_count.allow_tags = True
    get_count.short_description = u'Реф'
    get_count.admin_order_field = '-count'
    def link_group(self, obj):
        if obj.user_group:
            content_type = ContentType.objects.get_for_model(UserGroup)
            link = reverse("admin:%s_%s_changelist"%(content_type.app_label, content_type.model))
            html = '<a href = "{0}{1}" >посм.</a>'.format(link, obj.user_group.id)
            return html
        else:
            return u'нет'
    def get_user_group(self,obj):
        if obj.user_group:
            return obj.user_group.name
        else:
            return u'нет'
    def unBan(self, request, uid):
        user = Users.objects.get(id = uid)
        user_group = user.user_group
        user.zaban = False
        user.referals = None
        user.save()
        if user_group:
            user_group.banan = False
            user_group.save()
        return redirect(self._get_absolute_url())
    def Ban(self, request, uid):
        user = Users.objects.get(id = uid)
        user_group = user.user_group
        if user_group:
            user_group.banan = True
            user_group.queue = 0
            user_group.count = 0
            user_group.save()
        else:
            return redirect(self._get_absolute_url())
        user.zaban = True
        if user.ban == 0:
            user.ban = 1
        user.save()
        try:
            group = Groups.objects.get(group_info = user_group)
        except Groups.DoesNotExist:
            pass
        else:
            group.delete()
            AppMixins().stack(remove = 0)
        return redirect(self._get_absolute_url())
    def get_urls(self):
        urls = super(UsersAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^ban/(\d+)/$', self.admin_site.admin_view(self.Ban)),
            url(r'^unban/(\d+)/$', self.admin_site.admin_view(self.unBan)),)
        return my_urls + urls
    def _get_absolute_url(self):
        content_type = ContentType.objects.get_for_model(Users)
        return reverse("admin:%s_%s_changelist"%(content_type.app_label, content_type.model))
    def _status(self, obj):
        if obj.zaban:
            status = u'<a href = "unban/%s" class="text-danger" data-original-title="Разбанить" data-toggle="tooltip"><i class="fa fa-exclamation fa-lg" aria-hidden="true"></i></a>'%obj.id
        else:
            status = u'<a href = "ban/%s" class="text-success" data-original-title="Забанить" data-toggle="tooltip"><i class="fa fa-check fa-lg" aria-hidden="true"></i></a>'%obj.id
        return status
    def format_date(self, obj):
        return obj.start_date.strftime('%d.%m')
    
    get_user_group.admin_order_field = 'user_group__name'
    format_date.short_description = u'Дата'
    format_date.admin_order_field = '-start_date'
    _status.allow_tags = True
    _status.short_description = u'Бан'
    _status.admin_order_field = '-ban'
    list_max_show_all = 200
    list_per_page = 50
    list_display_links = ['get_name']
    #raw_id_fields = ['user_id']
    #list_filter = ['name', 'surname', 'user_id', 'referals']
    search_fields = ['name', 'surname', 'user_id', 'user_group__name', 'user_group__group_id']
    get_user_photo.allow_tags = True
    get_user_photo.short_description = u'Фото'
    get_user_photo.admin_order_field = '-photo'
    get_user_group.short_description = u'Группа'
    get_user_group.admin_order_field = '-user_group'
    #fields = ('user_id', 'name', 'surname')
    link_group.allow_tags = True
    link_group.short_description = u'Переход'
    fieldsets = (
        (None, {
            'fields': ('user_id', 'name', 'surname', 'referals', 'count', 'ban')
        }),
        (u'Дополнительная информация', {
            #'classes': ('dop_info',),
            'fields': ('who_invited', 'token', 'zaban'),
        }),
    )
    
# Register your models here.

@admin.register(StaticGroups)
class StaticAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'get_link_group', 'format_date', 'get_impression']
    list_select_related = True
    
    def get_name(self, obj):
        return obj.name
    get_name.short_description = u'Группа'
    get_name.admin_order_field = '-name'
    
    def format_date(self, obj):
        return obj.start_date.strftime('%d.%m.%y')
    format_date.short_description = u'Дата'
    format_date.admin_order_field = '-start_date'
    
    def get_link_group(self, obj):
        return obj.link_group
    get_link_group.allow_tags = True
    get_link_group.short_description = u'Ссылка'
    get_link_group.admin_order_field = '-link_group'
    fields = ('group_id', 'name')
    
    def get_impression(self, obj):
        return obj.impression
    get_impression.allow_tags = True
    get_impression.short_description = u'Лимит'
    get_impression.admin_order_field = '-impression'
    