# -*- coding: utf-8 -*-
from django.views.generic import View
from django.views.generic.list import ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from vkcpa.models import Users, Groups, UserGroup, StaticGroups, inspection_id
from vkcpa.serena import Serena, conductor, random_generate
from django import forms
from vkcpa.config import ID_APP, SECRET_CODE, DOMAIN, LIMIT_STATIC, LIMIT_GROUPS, _BAN
from urllib import urlopen
from datetime import datetime, timedelta
import hashlib
import json
from django.http import Http404
from django.http import HttpResponse
from django.core import serializers
from django.contrib import messages
from random import random, shuffle
import logging
from django.db.models import Q
import redis

__Version = '2.2' 

logger = logging.getLogger('django')

#Система приоритетов
#сначала сохраняется новый юзер, затем второе место занимает тот, кто его пригласил, после чего на третье место встает тот, у кого обновилась очередь
USER_ = 0
INVITED_ = 1

def redis_connect(host = 'localhost', port=6379, db=0):
    return redis.StrictRedis(host=host, port=port, db=db)

class LinkGroupForm(forms.Form):
    id_group = forms.CharField(max_length = 200)
    def __init__(self, *args, **kwargs):
        super(LinkGroupForm, self).__init__(*args, **kwargs)
        self.fields['id_group'].widget.attrs.update({'class': 'form-control', 'placeholder':u"Введите ссылку или ID группы", 'aria-describedby': 'bad'})

class AppMixins:
    def stack(self, **kwargs):
        if kwargs.get('remove'):
            groups = Groups.objects.filter(behavior = 1).order_by('-sort_position', '-time')
            for gr in groups:
                if gr.group_info.queue > 0:
                    gr.sort_position = kwargs['remove']
                    gr.save()
                    user_group = gr.group_info
                    user_group.queue -= 1
                    user_group.count +=1
                    user_group.save()
        if kwargs.get('new'):
            groups = Groups.objects.filter(behavior = 1)
            if len(groups)>40:
                groups = groups[40:]
                groups = groups[::-1]
                for gr in groups:
                    if gr.group_info.queue == 0:
                        gr.behavior = 2
                        gr.sort_position = 0
                        gr.save()
                        user_gr = gr.group_info
                        user_gr.count += 1
                        user_gr.save()
                groups = Groups.objects.filter(behavior = 1)
                groups = groups[::-1]
                if len(groups) > 40:
                    gr = groups[0]
                    user_gr = gr.group_info
                    gr.sort_position = kwargs['new']
                    user_gr.queue -= 1
                    user_gr.count +=1
                    gr.save()
                    user_gr.save()
        self.order_groups()
        #self.order_groups(3)
    def order_groups(self, behavior = 1):
        sort_position = 1
        list_group = Groups.objects.filter(behavior = 1)
        for gr in list_group:
            gr.sort_position = sort_position
            gr.save()
            sort_position +=1
    def hashGet(self, requestGetPost):
        if requestGetPost.get('uid') and hashlib.md5(ID_APP.encode() + str(requestGetPost.get('uid')).encode()+SECRET_CODE.encode()).hexdigest()==requestGetPost.get('hash'):
            return True
        else:
            return False
    def session_user(self, request, user = None):
        if not user:
            return request.session.get('uid')
        if Users.objects.filter(user_id=int(user['user_id'])).exists():
            return True
        else:
            return False
    def expires_token(self, user_id):
        user = Users.objects.get(user_id = user_id)
        if not user.expires_in and not user.token:
            return False
        elif user.token and user.expires_in == 0:
            return True
        start_date = user.start_date
        delta_time = timedelta(seconds = (user.expires_in-300))
        end_date = start_date + delta_time
        if end_date.replace(tzinfo=None) > datetime.utcnow():
            return True
        else:
            return False
    def remuneration(self, user):
        us_invited = Users.objects.get(user_id = user.who_invited)
        if not us_invited.user_group: return
        user_group_invited = us_invited.user_group
        group = Groups.objects.get(group_info = user_group_invited) if user_group_invited and Groups.objects.filter(group_info = user_group_invited).exists() else None
        if group and group.behavior == 1 and group.sort_position < 41:
            user_group_invited.queue += 1
            user_group_invited.save()
            #self.stack(new = 1)
        elif group:
            group.behavior = 1
            group.sort_position = INVITED_
            group.save()
            self.stack(new = INVITED_ + 1)
        elif group is None and user_group_invited.banan:
            user_group_invited.queue += 1
            user_group_invited.save()
        try:
            us_invited.count += 1
        except:
            us_invited.count = 1
        us_invited.save()
    def registration(self, user, groups, id_group, request):
        user_group_del = False
        group_del = False
        #group_obj_list = map(entry, groups)
        #for gr in group_obj_list:
            #if isinstance(gr, StaticGroups):
                #user.check_group_static.add(gr)
        if UserGroup.objects.filter(group_id = id_group).exists():
            user_group = UserGroup.objects.get(group_id = id_group)
            if not user.user_group:
                user_group.queue += 1
                user_group.save()
                if user.who_invited is not None and Users.objects.filter(user_id = user.who_invited).exists():
                    self.remuneration(user)
            else:
                user_group_del = user.user_group
                try:
                    group_del = Groups.objects.get(group_info = user_group_del)
                    group_del = (group_del.sort_position, group_del.behavior)
                    Groups.objects.get(group_info = user_group_del).delete()
                except:
                    pass
                #users = user_group_del.users_set.all()
                #for us in users:
                    #us.user_group = user_group
                    #us.save()
            group = Groups.objects.get(group_info = user_group) if Groups.objects.filter(group_info = user_group).exists() else None
            if group:
                if group.behavior == 2 or (group.behavior == 1 and group.sort_position > 40 ):
                    group.behavior = 1
                    group.sort_position = USER_
                    group.save()
                    self.stack(new = 1)
                else:
                    group.sort_position = USER_
                    group.save()
                    self.order_groups()
            else:
                sort_position = group_del[0] if group_del else USER_
                behavior = group_del[1] if group_del else 1
                group = Groups.objects.create(group_info = user_group, sort_position = sort_position, behavior = behavior)
                self.stack(new = 1)
        else:
            user_group = UserGroup.objects.create(group_id = id_group)
            group = Groups.objects.create(group_info = user_group, sort_position = USER_, behavior = 1)
            if user.who_invited is not None and Users.objects.filter(user_id = user.who_invited).exists():
                self.remuneration(user)
                self.stack(new = 1)
            else:
                if user.user_group:
                    user_group_del = user.user_group
                    try:
                        group_del = Groups.objects.get(group_info = user_group_del)
                        group_del = (group_del.sort_position, group_del.behavior)
                        Groups.objects.get(group_info = user_group_del).delete()
                        #user_group.delete()
                    except:
                        pass
                    #users = user_group_del.users_set.all()
                    #for us in users:
                        #us.user_group = user_group
                        #us.save()
                if group_del:
                    group.sort_position = group_del[0]
                    group.behavior = group_del[1]
                    group.save()
                else:
                    self.stack(new = 1)
        user.user_group = user_group
        #user.who_invited = None
        user.referals = DOMAIN +'/'+ coding_referal(user.user_id)
        user.save()
        if user_group_del and user_group_del != user_group:
            user_group_del.delete()
        return True

def UserAuth(method_to_decorate):
    def wrapper(self, request, *args, **kwargs):
        if request.session.get('uid'):
            user = Users.objects.get(user_id = int(request.session['uid'])) if Users.objects.filter(user_id = int(request.session['uid'])).exists() else None
            if user and user.referals:
                if user.user_group and user.user_group.banan == True:
                    if self.__class__.__name__ == 'UserBan':
                        return method_to_decorate(self, request, user, *args, **kwargs)
                    return redirect('%s'%(reverse('banan')))
                if self.__class__.__name__ == 'UserRoom':
                    return method_to_decorate(self, request, user, *args, **kwargs)
                return redirect('%s'%(reverse('useroom')))
            elif user:
                if self.__class__.__name__ == 'GroupsView':
                    return method_to_decorate(self, request, user, *args, **kwargs)
                else:
                    return redirect('%s'%(reverse('group_list')))
            else:
                request.session['uid'] = None
                return redirect('%s?%s'%(reverse('home'), 'session=not_user'))
        else:
            return redirect('%s?%s'%(reverse('home'), 'session=None'))
    return wrapper

#Кабинет пользователя
#useroom
class UserRoom(AppMixins, View):
    template_name = 'user.html'
    @UserAuth
    def get(self, request, user, *args, **kwargs):
        if _BAN:
            group_list = map(lambda x:x.group_info.group_id, user.check_group.all()) + map(lambda x:x.group_id, user.check_group_static.all())
            group_set = inspectionGroups(group_list, user)
        else:
            group_set = False
        if group_set is not False and len(group_set) > 0:#Пользователь выписался из каких-то групп
            #Процедура бана
            if user.ban < 1:
                discharged_groups = map(entry, group_set)
                return render(request, 'user.html', {'discharged_groups':discharged_groups, 'user':user, 'pre-ban':'Вы нарушили правила!!!'})
            gr_user = user.user_group
            gr_user.banan = True
            gr_user.queue = 0
            gr_user.count = 0
            gr_user.save()
            user.zaban = True
            if user.ban < 3:
                user.ban += 1
            user.save()
            try:
                group = Groups.objects.get(group_info = gr_user)
            except Groups.DoesNotExist:
                pass
            else:
                group.delete()
                self.stack(remove = 0)
            #Перенаправляем пользователя на обработчик страницы бана
            return redirect('%s'%(reverse('banan')))
        else:#Если _BAN выключен, отдаем ему его кабинет
            groups = Groups.objects.filter(behavior =1)[:LIMIT_GROUPS]
            day = datetime.utcnow()
            delta1 = timedelta(days = 2)
            delta2 = timedelta(days = 1)
            dateStart = day - delta1
            dateEnd = day - delta2
            statics = UserGroup.objects.filter(Q(start_date__range = (datetime(dateStart.year, dateStart.month, dateStart.day, 0, 0, 0), datetime(dateEnd.year, dateEnd.month, dateEnd.day, 23, 0, 0))))
            static_recommended = (int(round(len(statics)/40)) or 1) + 1
            userCount = user.count - 1 if user.count else 0
            if user.user_group:
                user_group = user.user_group
                if user_group.queue < 0:
                    user_group.queue = 0
                    user_group.save()
                if not Groups.objects.filter(group_info = user.user_group).exists():
                    messages.success(request, 'Ваша группа была удалена Администратором. Для продолжения нажмите - Сменить группу')
                    user.who_invited = None
                    user.save()
                    return render(request, 'user.html', {'static_groups':None, 'user':user, 'count_invited':userCount, 'user_group':u'группы нет', 'groups': groups, 'sort_position':u'группы нет', 'static_count': len(statics), 'static_recommended': static_recommended})
                sort_position = Groups.objects.get(group_info=user.user_group)
                if sort_position.behavior == 1:
                    if sort_position.sort_position > 40:
                        sort_position = 'Ожидает'
                    else:
                        sort_position = sort_position.sort_position
                else:
                    sort_position = 'Выпала'
                return render(request, 'user.html', {'static_groups':None, 'user':user, 'count_invited':userCount, 'user_group':user.user_group, 'groups': groups, 'sort_position': sort_position, 'static_count': len(statics), 'static_recommended': static_recommended})
            else:
                messages.success(request, 'Ваша группа была удалена, по причине нарушения правил.')
                user.who_invited = None
                user.save()
                return render(request, 'user.html', {'static_groups':None, 'user':user, 'count_invited':userCount, 'user_group':u'группы нет', 'groups': groups, 'sort_position':u'группы нет', 'static_count': len(statics), 'static_recommended': static_recommended})
    @UserAuth
    def post(self, request, user, *args, **kwargs):
        if 'amend' in request.POST and 'change' in request.POST:#Пользователь нажал СменитьГруппу
            user.referals = None
            user.check_group.clear()
            user.check_group_static.clear()
            user.who_invited = None
            user.save()
            return redirect('%s?amend=yes'%(reverse('group_list')))
        if 'release' in request.POST and _BAN:
            group_list = map(lambda x:x.group_info.group_id, user.check_group.all()) + map(lambda x:x.group_id, user.check_group_static.all())
            group_set = inspectionGroups(group_list, user)
            if group_set is not False and len(group_set) == 0:
                if user.ban < 3:
                    user.ban += 1
                    user.save()
        return redirect('%s'%(reverse('useroom')))

def exit_resource(request):
    if request.method == 'POST' and request.session.get('uid') and 'exit' in request.POST:
        request.session['uid'] = None
        del request.session['uid']
        #return render(request, 'index.html', {'ID_APP':ID_APP, 'DOMAIN':r'http://'+DOMAIN})
        return redirect('%s'%(reverse('home')))
    else:
        return redirect('%s?%s'%(reverse('home'), 'exit=yes'))

def coding_referal(uid):
    m1 = 99
    m2 = 10
    tail = int(round(random()*(m1-m2)+m2))
    code = hex(int(str(uid)+str(tail)))
    code = code.replace('x', 'R')
    return 'ref' + code

def decoding_referal(link):
    if link: 
        return int(str(int(link[3:].replace('R', 'x').strip('L'), 16))[:-2])#haskell style
    else:
        None


#home baze
class UserAutentific(AppMixins, View):
    template_name = 'index.html'
    def get(self, request, *args, **kwargs):
        if request.GET.get('exit'):
            request.session['uid'] = None
            del request.session['uid']
        if request.GET.get('error'):
            request.session['uid'] = None
            if request.GET['error'] == 'update':
                msg = ''
            else:
                msg = u'Что-то пошло не так. Попробуйте авторизоваться снова'
            return render(request, self.template_name, {'message':msg, 'ID_APP':ID_APP, 'DOMAIN':r'http://'+DOMAIN})
        if request.session.get('uid') and Users.objects.filter(user_id = int(request.session['uid'])).exists():
            return redirect('%s'%(reverse('useroom')))
        if request.GET.get('code'):
            try:
                vk_token = urlopen(r'https://oauth.vk.com/access_token?client_id=%s&client_secret=%s&redirect_uri=%s&code=%s&v=5.52'%(ID_APP, SECRET_CODE, DOMAIN, request.GET['code']))
            except:
                return render(request, self.template_name, {'message':'Не удалось подключиться к ВК. Попробуйте немного позже', 'ID_APP':ID_APP, 'DOMAIN':r'http://'+DOMAIN})
            try:
                vk_dict = json.loads(vk_token.read().decode())
            except ValueError, UnicodeDecodeError:
                return render(request, self.template_name, {'message':'Что-то пошло не так|Попробуйте зайти немного позже', 'ID_APP':ID_APP, 'DOMAIN':r'http://'+DOMAIN})
            if vk_dict.get('access_token') and not self.session_user(request, vk_dict):
                userbd = Users.objects.create(user_id = int(vk_dict['user_id']), start_date = datetime.utcnow(), \
                    expires_in = vk_dict['expires_in'], token = vk_dict['access_token'], who_invited = request.session.get('who_invited'))
                try:
                    inquiry = urlopen('http://api.vk.com/method/users.get?user_id=%s&fields=photo_100&lang=ru&v=5.60'%(vk_dict['user_id']))
                    response_dict = json.loads(inquiry.read().decode('utf-8'))
                except:
                    response_dict = None
                else:
                    if response_dict['response'] and len(response_dict['response']) > 0:
                        userbd.name = response_dict['response'][0].get('first_name')
                        userbd.surname = response_dict['response'][0].get('last_name')
                        photo = response_dict['response'][0]['photo_100'] if response_dict['response'][0].get('photo_100') and response_dict['response'][0]['photo_100'].startswith('https:') else 'https://vk.com/images/camera_50.png'
                        userbd.photo = photo
                        userbd.save()
                request.session['uid'] = vk_dict['user_id']
            elif vk_dict.get('access_token') and self.session_user(request, vk_dict):
                userbd = Users.objects.get(user_id = vk_dict['user_id'])
                userbd.token = vk_dict['access_token']
                userbd.expires_in = vk_dict['expires_in']
                userbd.start_date = datetime.utcnow()
                try:
                    inquiry = urlopen('http://api.vk.com/method/users.get?user_id=%s&fields=photo_100&lang=ru&v=5.60'%(vk_dict['user_id']))
                    response_dict = json.loads(inquiry.read().decode('utf-8'))
                except:
                    response_dict = None
                else:
                    if response_dict and ('error' not in response_dict) and len(response_dict['response']) > 0:
                        userbd.name = response_dict['response'][0].get('first_name')
                        userbd.surname = response_dict['response'][0].get('last_name')
                        photo = response_dict['response'][0]['photo_100'] if response_dict['response'][0].get('photo_100') and response_dict['response'][0]['photo_100'].startswith('https:') else 'https://vk.com/images/camera_50.png'
                        userbd.photo = photo
                userbd.save()
                request.session['uid'] = vk_dict['user_id']
            if not userbd.count:
                return redirect('%s'%(reverse('pravila')))
            return redirect('%s'%(reverse('useroom')))
        referal = Users.objects.get(user_id = int(request.session['uid'])).referals if request.session.get('uid') and Users.objects.filter(user_id = int(request.session['uid'])).exists() and Users.objects.get(user_id = int(request.session['uid'])).referals is not None else u'Для получения реферальной ссылки нужно войти на сайт'
        try:
            link = decoding_referal(kwargs.get('referal'))
        except:
            link = None
        request.session['who_invited'] = link
        return render(request, self.template_name, {'referal':referal, 'ID_APP':ID_APP, 'DOMAIN':r'http://'+DOMAIN})
    def post(self, request, *args, **kwargs):
        if request.session.get('uid') and 'exit' in request.POST:
            request.session['uid'] = None
            del request.session['uid']
        return render(request, self.template_name, {'ID_APP':ID_APP, 'DOMAIN':r'http://'+DOMAIN})
            


def pravila(request):
    if request.method == 'POST' and request.session.get('uid') and 'accept' in request.POST:
        try:
            user_bd = Users.objects.get(user_id = int(request.session['uid']))
        except:
            request.session['uid'] = None
            return redirect('%s?%s'%(reverse('home'), 'error=Pravila_not_user_bd'))
        user_bd.count = 1
        user_bd.save()
        return redirect('%s'%(reverse('useroom')))
    elif request.method == 'GET' and request.session.get('uid'):
        try:
            user_bd = Users.objects.get(user_id = int(request.session['uid']))
        except:
            request.session['uid'] = None
            return redirect('%s?%s'%(reverse('home'), 'error=Pravila_not_user_bd'))
        if user_bd.count is None:
            widget = True
            return render(request, 'pravila.html', {'widget':widget})
    
    widget = False
    return render(request, 'pravila.html', {'widget':widget})




#group_list            
class GroupsView(AppMixins, ListView):
    message = u"<h3 class = 'message'>Для продолжения подпишитесь во все группы</h3>"
    template_name = 'groups_list.html'
    model = Groups
    context_object_name = 'groups'
    no_entry_group = None
    button_title = None
    
    @UserAuth
    def get(self, request, user, *args, **kwargs):
        r = redis_connect()
        if not r.get('robot') or r.get('robot') == '0':
            SereNa_th = Serena(conductor)
            SereNa_th.start()
        self.user = user
        activGroups = self.activList()
        if activGroups and self.message != u"<h3 class = 'message'>Для продолжения подпишитесь во все группы</h3>":
            try:
                groups = map(lambda x:x.group_id, activGroups[0]) + map(lambda x:x.group_info.group_id, activGroups[1])
            except:
                groups = map(lambda x:x.group_id, StaticGroups.objects.all()) + map(lambda x:x.group_info.group_id, Groups.objects.filter(behavior =1)[:LIMIT_GROUPS])
        else:
            groups = map(lambda x:x.group_id, StaticGroups.objects.all()) + map(lambda x:x.group_info.group_id, Groups.objects.filter(behavior =1)[:LIMIT_GROUPS])
        self.cap_group = inspectionGroups(groups, user)
        #******************************************************************************
        inspection_ids(map(lambda x:x.group_info.group_id, Groups.objects.filter(behavior =1)[:LIMIT_GROUPS]))
        if user.user_group:
            #self.form = LinkGroupForm()
            #self.form.fields['id_group'].widget.attrs['placeholder'] = user.user_group.link_group or user.user_group.group_id
            user_form_cleaned = 'user_form_cleaned_%s'%user
            if r.get(user_form_cleaned):
                form_initial = r.get(user_form_cleaned)
            else:
                form_initial = user.user_group.link_group or user.user_group.group_id
            self.form = LinkGroupForm(initial = {'id_group':form_initial})
        else:
            self.form = LinkGroupForm()
        if request.GET.get('amend'):
            self.button_title = u'Сохранить'
        return super(GroupsView, self).get(request, *args, **kwargs)
    @UserAuth
    def post(self, request, user, *args, **kwargs):
        r = redis_connect()
        if not r.get('robot') or r.get('robot') == '0':
            SereNa_th = Serena(conductor)
            SereNa_th.start()
        self.user = user
        self.form = LinkGroupForm(request.POST)
        if self.form.is_valid():
            self.data_form = self.form.cleaned_data['id_group']
            user_form_cleaned = 'user_form_cleaned_%s'%user
            r.set(user_form_cleaned, self.data_form)
            #try:
            groups = map(lambda x:x.group_id, self.user.check_group_static.all()) + map(lambda x:x.group_info.group_id, self.user.check_group.all())
            #except:
                #groups = map(lambda x:x.group_id, StaticGroups.objects.all()) + map(lambda x:x.group_info.group_id, Groups.objects.filter(behavior =1)[:LIMIT_GROUPS])
            group_set = inspectionGroups(groups, user)
            self.cap_group = group_set
            logger.debug(str(group_set))
            if group_set is not False and len(group_set) == 0:
                plus_subscriber(groups)
                inspect = inspection_id(self.data_form)
                if not inspect[0]:
                    self.message = inspect[1] if inspect[1] else u"<h3 class = 'error'>Что-то пошло не так, попробуйте повторить попытку</h3>"
                    return self.get(request)
                else:
                    self.data_form = int(inspect[2])
                    request.session['id_group'] = self.data_form
                if UserGroup.objects.filter(group_id = self.data_form).exists():
                    group_add = UserGroup.objects.get(group_id = self.data_form)
                    if group_add.banan:
                        self.message = u"<h3 class = 'error'>Эта группа заблокирована, Вы не можете её продвигать</h3>"
                        return self.get(request)
                    elif len(group_add.users_set.all()) > 5:
                        self.message = u"<h3 class = 'error'>Эту группу продвигает уже 5 пользователей, регистрация невозможна</h3>"
                        return self.get(request)
                #процедура регистрации
                self.no_entry_group = None
                result = self.registration(user, groups, self.data_form, request)
                if result:
                    r.delete(user_form_cleaned)
                    return redirect('%s'%(reverse('useroom')))

            elif not group_set:
                #request.session['uid'] = None
                return redirect('%s?%s'%(reverse('home'), 'error=not_set_connect'))
            else:
                self.no_entry_group = map(entry, group_set)
                self.message = u"<h3 class = 'error'>Вы подписались не во все группы (вступить в: %s гр.)</h3>"%len(self.no_entry_group)
                self.form = LinkGroupForm(initial = {'id_group':self.data_form})
                return self.get(request)
        else:
            self.message = u"<h3 class = 'message'>Введите ссылку или ID вашей группы</h3>"
            self.form = LinkGroupForm()
            return self.get(request)
    
    def get_context_data(self, **kwargs):
        context = super(GroupsView, self).get_context_data(**kwargs)
        context['form'] = self.form
        context['message'] = self.message
        #static_groups = StaticGroups.objects.all()
        #static_id = range(len(static_groups))[:LIMIT_STATIC]
        #shuffle(static_id)
        #context['static_groups'] = map(lambda x: static_groups[x], static_id)
        if self.no_entry_group:
            context['notentry'] = self.no_entry_group
            #context['static_groups'] = None
            context['groups'] = None
        if self.button_title:
            context['button'] = self.button_title
        context['cap'] = self.cap_group
        context['self_user'] = self.user
        return context
    def get_queryset(self):
        activGroups = self.activList()
        if activGroups and self.message != u"<h3 class = 'message'>Для продолжения подпишитесь во все группы</h3>":
            groups_list = activGroups[1]
            static_groups = activGroups[0]
            groups = static_groups + map(lambda x:x.group_info, groups_list)
            static_id = range(len(groups))[:LIMIT_STATIC + LIMIT_GROUPS]
            shuffle(static_id)
            return map(lambda x: groups[x], static_id)
        else:
            self.user.check_group.clear()
            self.user.check_group_static.clear()
            groups = list(StaticGroups.objects.all()) + map(lambda x:x.group_info, Groups.objects.filter(behavior =1))
            groups = manage_groups(groups, self.user)#[:LIMIT_GROUPS + LIMIT_STATIC]
            static_id = range(len(groups))[:LIMIT_STATIC + LIMIT_GROUPS]
            shuffle(static_id)
            return map(lambda x: groups[x], static_id)
    def activList(self):
        groups = (list(self.user.check_group_static.all()), list(self.user.check_group.all()))
        if len(groups[0]) > 0 or len(groups[1]) > 0:
            return groups
        else:
            return None
    
#ban & banan   
class UserBan(AppMixins, View):
    @UserAuth
    def get(self, request, user, *args, **kwargs):
        if not user.user_group.banan:
            return redirect('%s'%(reverse('home')))
        elif user.zaban:
            if user.ban == 2:
                count = u'одного нового участника'
            elif user.ban == 3:
                count = u'двух новых участников'
            else:
                count = u'0 новых участников'
            return render(request, 'ban.html', {'user':user, 'user_group':user.user_group, 'count':count})
        else:
            form = LinkGroupForm()
            return render(request, 'banan.html', {'user':user, 'user_group':user.user_group, 'form':form})
    @UserAuth            
    def post(self, request, user, *args, **kwargs):
        groups = Groups.objects.filter(behavior =1)[:LIMIT_GROUPS]
        if user.user_group.banan and user.zaban and user.ban > 1:
            if ((user.ban - 1) - user.user_group.queue) <= 0:
                user.referals = None
                user.check_group.clear()
                user.check_group_static.clear()
                user.who_invited = None
                user_group = user.user_group
                user_group.banan = False
                user_group.queue = user_group.queue - (user.ban - 1)
                user_group.save()
                user.zaban = False
                user.save()
                return redirect('%s'%(reverse('group_list')))
            else:
                return render(request, 'ban.html', {'user':user, 'user_group':user.user_group, 'message':u"<h3 class = 'error'>Пока по вашей ссылке прошло недостаточно человек</h3>"})
        elif user.user_group.banan and not user.zaban:
            user.referals = None
            user.check_group.clear()
            user.check_group_static.clear()
            user.who_invited = None
            user.save()
            return redirect('%s'%(reverse('group_list')))
        else:
            request.session['uid'] = None
            return redirect('%s'%(reverse('home')))
            


def manage_groups(groups, obj = None):
    count_static = 0
    count_group = 0
    for nomer, group in enumerate(groups):
        if group.impression:
            groups.pop(nomer)
            continue
        else:
            if obj:
                if isinstance(group, StaticGroups) and count_static < LIMIT_STATIC:
                    obj.check_group_static.add(group)
                    count_static += 1
                elif isinstance(group, UserGroup) and count_group < LIMIT_GROUPS:
                    try:
                        group_list = Groups.objects.get(group_info = group)
                    except Groups.DoesNotExist:
                        pass
                    else:
                        obj.check_group.add(group_list)
                        count_group += 1
    return groups

    
#Проверяем, не выписался ли участник из ранее подписанных групп
#Оформляем в виде функции, чтобы использовать в дальнейшем при асинхронной проверкe
def inspectionGroups(arr, user):
    try:
        user_group_id = urlopen('https://api.vk.com/method/groups.get?user_id=%s&extended=0&access_token=%s&v=5.60'%(user.user_id, user.token), '2')
    except:
        #'message':'ошибка подключения|Попробуйте повторить попытку позже'
        
        return False
    try:
        response_dict = json.loads(user_group_id.read().decode('utf-8'))
    except ValueError, UnicodeDecodeError:
        #'message':'Неверный id |Попробуйте повторить попытку'
        return False
    if 'error' in response_dict:
        #'message':'Неверный id |Попробуйте повторить попытку'
        return False
    return list(set(arr) - set(response_dict['response']['items']))


def entry(x):
    if StaticGroups.objects.filter(group_id = x).exists():
        return StaticGroups.objects.get(group_id = x)
    elif UserGroup.objects.filter(group_id = x).exists():
        return UserGroup.objects.get(group_id = x)


def inspection_ids(args):
    groups_str = ','.join(map(lambda x: str(x), args))
    try:
        inquiry = urlopen('http://api.vk.com/method/groups.getById?group_ids=%s&v=5.60'%groups_str)
        response_dict = json.loads(inquiry.read().decode('utf-8'))
    except:
        return
    else:
        for group in response_dict['response']:
            if group['name'] == '' or group['name'] =='DELETED' or  group.get('deactivated') or group['is_closed'] > 0:
                user_group = UserGroup.objects.get(group_id = group['id']) if UserGroup.objects.filter(group_id = group['id']).exists() else None
                if user_group:
                    try:
                        Groups.objects.get(group_info = user_group).delete()
                    except:
                        pass
                    user_group.delete()

def plus_subscriber(groups):
    r = redis_connect()
    def plus_(x):
        group_sign = r.get(x)
        if group_sign:
            r.set(x, int(group_sign) + 1)
        else:
            r.set(x, '1')
    map(plus_, groups)



def ajax_session(request, sort_position):
    group = Groups.objects.filter(sort_position = sort_position)
    
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(serializers.serialize("json", group))#[group, group.group_info]
    return response

def redirect_home(request):
    return redirect('%s'%(reverse('home')))


