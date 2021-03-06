# -*- coding: utf-8 -*-
from django.db import models
from urllib import urlopen
import urlparse
import json
import unicodedata
import string
#from vkcpa.UserVk2 import AppMixins

def normText(txt):
    txt = unicode(txt)
    simvols = []
    for simvol in txt:
        try:
            norm = unicodedata.name(simvol)
        except ValueError:
            pass
        else:
            simvols.append(simvol)
    return ''.join(simvols)


def shave_marks(txt):
    norm_txt = unicodedata.normalize('NFD', txt)
    shaved = ''.join(c for c in norm_txt if not unicodedata.combining(c))
    return unicodedata.normalize('NFC', shaved)

def inspection_id(id_group):
    variant = ('deleted', 'banned')
    if not id_group.strip().isdigit():
        id_group = urlparse.urlparse(id_group).path[1:].strip()
        if id_group.startswith('public') and id_group[6:].isdigit():
            id_group = id_group.replace('public','')
    try:
        inquiry = urlopen('http://api.vk.com/method/groups.getById?group_id=%s&v=5.60'%id_group)
        response_dict = json.loads(inquiry.read().decode('utf-8'))
    except:
        return (False, None)
    else:
        try:
            #group_name = response_dict['response'][0]['name']
            group_name = normText(response_dict['response'][0]['name'])
        except:
            return (False, u"<h3 class = 'error'>Группа не доступна для регистрации</h3>")
        if not group_name == '' and group_name.lower() not in variant and not response_dict['response'][0].get('deactivated'):
            if response_dict['response'][0]['is_closed'] == 0:
                if StaticGroups.objects.filter(group_id = int(response_dict['response'][0]['id'])).exists():
                    return (False, u"<h3 class = 'error'>Дублировать группы из вступительного списка запрещено</h3>")
                return (group_name, r'http://vk.com/' + response_dict['response'][0]['screen_name'], response_dict['response'][0]['id'])
            else:
                return (False, u"<h3 class = 'error'>Регистрировать можно только открытые группы</h3>")
        else:
            return (False, u"<h3 class = 'error'>Группа не доступна для регистрации</h3><br /><h4>Попробуйте ввести id группы</h4>")




class UserGroup(models.Model):
    group_id = models.BigIntegerField(unique=True)
    link_group = models.URLField(null = True, blank=True)
    name=models.CharField(u'Название группы', max_length=255, blank=True, null = True)
    start_date = models.DateTimeField(auto_now_add=True)
    banan = models.BooleanField(default = False)
    queue = models.IntegerField(u'Запас кругов', null = True, blank=True, default = 0)
    count = models.IntegerField(u'Пригласил', null = True, blank=True, default = 0)
    limit_impressions = models.IntegerField(default = 100)
    impression = models.BooleanField(default = False)
    end_limit = models.DateTimeField(auto_now=True)
    def save(self, *args,**kwargs):
        if not self.name:
            name_group = inspection_id(str(self.group_id))
            if not name_group[0]:
                return
            else:
                self.name = name_group[0]
                self.link_group = name_group[1]
        super(UserGroup,self).save(*args,**kwargs)
    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return str(self.group_id)
    class Meta:
        ordering = ['group_id']
        db_table = u'Группа пользователя'
        verbose_name = u'Группа'
        verbose_name_plural = u'Группы'


class StaticGroups(models.Model):
    group_id = models.BigIntegerField(unique=True)
    link_group = models.URLField(null = True, blank=True)
    name=models.CharField(u'Название группы', max_length=255, blank=True, null = True)
    start_date = models.DateTimeField(auto_now_add=True)
    sort_position = models.IntegerField(blank=True, null = True)
    limit_impressions = models.IntegerField(default = 100)
    impression = models.BooleanField(default = False)
    end_limit = models.DateTimeField(auto_now=True)
    def save(self, *args,**kwargs):
        #super(StaticGroups,self).save(*args,**kwargs)
        if not self.name:
            name_group = inspection_id(str(self.group_id))
            if not name_group[0]:
                return
            else:
                self.name = name_group[0]
                self.link_group = name_group[1]
        if not self.sort_position:
            self.sort_position = len(StaticGroups.objects.all()) + 1
        super(StaticGroups,self).save(*args,**kwargs)
    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return str(self.group_id)
    class Meta:
        ordering = ['sort_position', 'start_date']
        db_table = u'Список статичных групп'
        verbose_name = u'Партнер'
        verbose_name_plural = u'Партнеры'



#Эта таблица выполняет роль хранилища стека, она обновляется каждый раз при регистрации или бане
class Groups(models.Model):
    group_info = models.ForeignKey(UserGroup, null = True, blank = True, on_delete = models.SET_NULL)
    sort_position = models.IntegerField(blank=True, null = True)
    ##если 1, то выводятся отдельно и изменить может только админ,
    ##если 2,  то новые вытесняют другие и они не выводятся, так как получают код 3
    time = models.DateTimeField(auto_now=True)
    behavior = models.IntegerField(default = 1)

    def __unicode__(self):
        try:
            return self.group_info.name
        except:
            return self.pk
    #def delete(self, *args, **kwargs):
    #    try:
    #        if len(self.group_info.users_set.all()) == 0:
    #            user_group = self.group_info
    #            user_group.delete()
    #    except:
    #        pass
    #    super(Groups, self).delete(*args, **kwargs) Этот метод вызывает ошибку, нарушается логика
    class Meta:
        ordering = ['behavior', 'sort_position', 'time']
        db_table = u'Стек групп юзеров'
        verbose_name = u'Список'
        verbose_name_plural = u'Список'



class Users(models.Model):
    user_id = models.BigIntegerField(unique=True)
    name=models.CharField(u'Имя',max_length=255, blank=True, null = True)
    surname=models.CharField(u'Фамилия', max_length=255, blank=True, null = True)
    photo = models.URLField(blank=True, null = True)
    start_date = models.DateTimeField()
    expires_in = models.IntegerField(null = True)
    token = models.CharField(u'Токен',max_length=255, null = True)
    user_group = models.ForeignKey(UserGroup, null = True, blank = True, on_delete =\
                                                                     models.SET_NULL)
    check_group = models.ManyToManyField(Groups)
    check_group_static = models.ManyToManyField(StaticGroups)
    ban = models.IntegerField(default = 0)
    zaban = models.BooleanField(default = False)
    referals = models.CharField(u'Реферальная ссылка', max_length=255, null = True)
    who_invited = models.BigIntegerField(null = True, blank=True)
    count = models.IntegerField(u'Количество приглашенных', null = True, blank=True)
       
    def save(self, *args, **kwargs):
        if self.name:
            self.name = normText(self.name)
        if self.surname:
            self.surname = normText(self.surname)
        super(Users,self).save(*args,**kwargs)


    def __unicode__(self):
        if self.name and self.surname:
            show = self.name+' '+self.surname
        elif self.name:
            show = self.name
        else:
            show = str(self.user_id)
        #if self.photo:
        #    return '<img src="%s" width="30" height="30" />  %s'%(self.photo, show)
        #else:
        return show
    #def ban(self):
        #gr_user = self.user_group
        #gr_user.banan = True
        #gr_user.queue = 0
        #gr_user.count = 0
        #gr_user.save()
        #self.ban = True
        #self.save()
        #try:
        #    group = Groups.objects.get(group_info = gr_user)
        #except Groups.DoesNotExist:
        #    pass
        #else:
        #    group.delete()
        #    AppMixins().stack(remove = 0)
    class Meta:
        ordering = ['user_id']
        db_table = u'Юзеры'
        verbose_name = u'Юзер'
        verbose_name_plural = u'Юзеры'




