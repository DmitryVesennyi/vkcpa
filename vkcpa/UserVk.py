# -*- coding: utf-8 -*-
from django.views.generic import View
from django.views.generic.list import ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from vkcpa.models import Users, Groups, UserGroup, StaticGroups, inspection_id
from django import forms
from vkcpa.config import ID_APP, SECRET_CODE, DOMAIN
from urllib import urlopen
from datetime import datetime, timedelta
import hashlib
import json
from django.http import Http404
from django.http import HttpResponse
from django.core import serializers
from django.contrib import messages
import logging

logger = logging.getLogger('django')

#Система приоритетов
#сначала сохраняется новый юзер, затем второе место занимает тот, кто его пригласил, после чего на третье место встает тот, у кого обновилась очередь
USER_ = 0
INVITED_ = 2


class LinkGroupForm(forms.Form):
    id_group = forms.CharField(max_length = 200)
    def __init__(self, *args, **kwargs):
        super(LinkGroupForm, self).__init__(*args, **kwargs)
        self.fields['id_group'].widget.attrs.update({'class': 'form-control', 'placeholder':u"Введите ссылку или ID группы", 'aria-describedby': 'bad'})

class AppMixins:
    def stack(self, **kwargs):
        groups = Groups.objects.filter(behavior = 1).order_by('-sort_position', 'time')
        if kwargs.get('remove'):
            for gr in groups:
                if gr.group_info.queue > 0:
                    gr.sort_position = kwargs['remove']
                    gr.save()
                    user_group = gr.group_info
                    user_group.queue -= 1
                    user_group.count +=1
                    user_group.save()
        if kwargs.get('new'):
            if len(groups)>40:
                groups = groups[:-41]
                for gr in groups:
                    if gr.group_info.queue == 0:
                        gr.behavior = 2
                        gr.sort_position = 0
                        gr.save()
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
        if Users.objects.filter(user_id=user['user_id']).exists():
            return True
        else:
            return False
    def expires_token(self, user_id):
        user = Users.objects.get(user_id = user_id)
        if not user.expires_in and not user.token:
            return False
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
            self.stack(new = 1)
        elif group:
            group.behavior = 1
            group.sort_position = INVITED_
            group.save()
            self.stack(new = INVITED_ + 1)
        elif group is None and user_group_invited.banan:
            user_group_invited.queue += 1
            user_group_invited.save()
    def registration(self, user, groups, id_group, request):
        group_del = False
        group_obj_list = map(entry, groups)
        for gr in group_obj_list:
            if isinstance(gr, UserGroup) and Groups.objects.filter(group_info = gr).exists():
                group = Groups.objects.get(group_info = gr)
                user.check_group.add(group)
            elif isinstance(gr, StaticGroups):
                user.check_group_static.add(gr)
        if UserGroup.objects.filter(group_id = id_group).exists():
            user_group = UserGroup.objects.get(group_id = id_group)
            if not user.user_group:
                user_group.queue += 1
                user_group.save()
                if user.who_invited is not None and Users.objects.filter(user_id = user.who_invited).exists():
                    self.remuneration(user)
            else:
                try:
                    group_del = Groups.objects.get(group_info = user.user_group)
                    group_del = (group_del.sort_position, group_del.behavior)
                    Groups.objects.get(group_info = user.user_group).delete()
                except:
                    pass
                users = user.user_group.users_set.all()
                for us in users:
                    us.user_group = user_group
                    us.save()
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
                sort_position = group_del[0] if group_del else INVITED_
                behavior = group_del[1] if group_del else 1
                group = Groups.objects.create(group_info = user_group, sort_position = sort_position, behavior = behavior)
                self.stack(new = 1)
        else:
            user_group = UserGroup.objects.create(group_id = id_group)
            group = Groups.objects.create(group_info = user_group, sort_position = USER_, behavior = 1)
            if user.who_invited is not None and Users.objects.filter(user_id = user.who_invited).exists():
                self.remuneration(user)
            else:
                if user.user_group:
                    user_group = user.user_group
                    try:
                        group_del = Groups.objects.get(group_info = user_group)
                        group_del = (group_del.sort_position, group_del.behavior)
                        Groups.objects.get(group_info = user_group).delete()
                        #user_group.delete()
                    except:
                        pass
                    users = user.user_group.users_set.all()
                    for us in users:
                        us.user_group = user_group
                        us.save()
                if group_del:
                    group.sort_position = group_del[0]
                    group.behavior = group_del[1]
                    group.save()
                else:
                    self.stack(new = 1)
        user.user_group = user_group
        #user.who_invited = None
        user.referals = DOMAIN +'/'+ str(user.user_id)
        user.save()
        return True




#home baze
class UserAutentific(AppMixins, View):
    template_name = 'index.html'
    def get(self, request, *args, **kwargs):
        if request.GET.get('error'):
            request.session['uid'] = None
            if request.GET['error'] == 'update':
                msg = ''
            else:
                msg = u'Что-то пошло не так. Попробуйте авторизоваться снова'
            return render(request, self.template_name, {'message':msg, 'ID_APP':ID_APP, 'DOMAIN':r'http://'+DOMAIN})
        #if request.session.get('uid') and Users.objects.filter(user_id = request.session['uid']).exists():
        #    user_bd = Users.objects.get(user_id = int(request.session['uid']))
        #    if not user_bd.count:
        #        return redirect('%s?uid=%s&hash=%s'%(reverse('pravila'), request.session['uid'], hashlib.md5(ID_APP.encode() + str(request.session['uid']).encode()+SECRET_CODE.encode()).hexdigest()))
        #    return redirect('%s?uid=%s&hash=%s'%(reverse('group_list'), request.session['uid'], hashlib.md5(ID_APP.encode() + str(request.session['uid']).encode()+SECRET_CODE.encode()).hexdigest()))
        if request.GET.get('code') and not self.session_user(request):
            try:
                vk_token = urlopen(r'https://oauth.vk.com/access_token?client_id=%s&client_secret=%s&redirect_uri=%s&code=%s&v=5.52'%(ID_APP, SECRET_CODE, DOMAIN, request.GET['code']))
            except:
                return render(request, self.template_name, {'message':'Не удалось подключиться к ВК. Попробуйте немного позже', 'ID_APP':ID_APP, 'DOMAIN':r'http://'+DOMAIN})
            try:
                vk_dict = json.loads(vk_token.read().decode())
            except ValueError, UnicodeDecodeError:
                return render(request, self.template_name, {'message':'Что-то пошло не так|Попробуйте зайти немного позже', 'ID_APP':ID_APP, 'DOMAIN':r'http://'+DOMAIN})
            if vk_dict.get('access_token') and not self.session_user(request, vk_dict):
                userbd = Users.objects.create(user_id = vk_dict['user_id'], start_date = datetime.utcnow(), \
                    expires_in = vk_dict['expires_in'], token = vk_dict['access_token'], who_invited = kwargs.get('referal'))
                request.session['uid'] = vk_dict['user_id']
                return redirect('%s?uid=%s&hash=%s'%(reverse('group_list'), vk_dict['user_id'], hashlib.md5(ID_APP.encode() + str(vk_dict['user_id']).encode()+SECRET_CODE.encode()).hexdigest()))
            elif vk_dict.get('access_token') and self.session_user(request, vk_dict):
                userbd = Users.objects.get(user_id = vk_dict['user_id'])
                userbd.token = vk_dict['access_token']
                userbd.expires_in = vk_dict['expires_in']
                userbd.start_date = datetime.utcnow()
                userbd.save()
                request.session['uid'] = vk_dict['user_id']
                if not userbd.count:
                    return redirect('%s?uid=%s&hash=%s'%(reverse('pravila'), vk_dict['user_id'], hashlib.md5(ID_APP.encode() + str(vk_dict['user_id']).encode()+SECRET_CODE.encode()).hexdigest()))
                return redirect('%s?uid=%s&hash=%s'%(reverse('group_list'), vk_dict['user_id'], hashlib.md5(ID_APP.encode() + str(vk_dict['user_id']).encode()+SECRET_CODE.encode()).hexdigest()))
        if self.hashGet(request.GET):
            user = {'user_id':request.GET.get('uid'), 'first_name':request.GET.get('first_name'), 'last_name':request.GET.get('last_name'), 'photo':request.GET.get('photo_rec')}
            #request.session['photo'] = request.GET.get('photo_rec')
            if self.session_user(request, user):
                if self.expires_token(int(user['user_id'])):
                    #если срок годности токена жив, то отправляем на страницу юзера
                    request.session['uid'] = request.GET.get('uid')
                    user_bd = Users.objects.get(user_id = int(request.GET['uid']))
                    if not user_bd.count:
                        return redirect('%s?uid=%s&hash=%s'%(reverse('pravila'), request.GET['uid'], request.GET['hash']))
                    return redirect('%s?uid=%s&hash=%s'%(reverse('group_list'), request.GET['uid'], request.GET['hash']))#4в этом месте редиректим с параметрами uid и hash
                else:
                    request.session['uid'] = None
                    return redirect(r'https://oauth.vk.com/authorize?client_id=%s&display=popup&redirect_uri=http://%s&scope=groups &response_type=code&v=5.60'%(ID_APP, DOMAIN))
            else:
                photo = request.GET['photo_rec'] if request.GET.get('photo_rec') and request.GET['photo_rec'].startswith('https:') else 'https://vk.com/images/camera_50.png'
                Users.objects.create(user_id = request.GET.get('uid'), name=request.GET.get('first_name'), surname=request.GET.get('last_name'), start_date = datetime.utcnow(), who_invited = request.session.get('who_invited'), photo = photo)
                return redirect(r'https://oauth.vk.com/authorize?client_id=%s&display=popup&redirect_uri=http://%s&scope=groups &response_type=code&v=5.60'%(ID_APP, DOMAIN))
        referal = Users.objects.get(user_id = int(request.session['uid'])).referals if request.session.get('uid') and Users.objects.filter(user_id = int(request.session['uid'])).exists() and Users.objects.get(user_id = int(request.session['uid'])).referals is not None else u'Для получения реферальной ссылки нужно зарегистрироваться'
        request.session['who_invited'] = kwargs.get('referal')
        return render(request, self.template_name, {'referal':referal, 'ID_APP':ID_APP, 'DOMAIN':r'http://'+DOMAIN})
    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, {'ID_APP':ID_APP, 'DOMAIN':r'http://'+DOMAIN})
            


def pravila(request):
    if request.method == 'POST' and AppMixins().hashGet(request.POST) and 'accept' in request.POST:
        user_bd = Users.objects.get(user_id = int(request.POST['uid']))
        user_bd.count = 1
        user_bd.save()
        request.session['uid'] = request.POST['uid']
        return redirect('%s?uid=%s&hash=%s'%(reverse('group_list'), request.POST['uid'], request.POST['hash']))
    elif request.method == 'GET' and AppMixins().hashGet(request.GET):
        user_bd = Users.objects.get(user_id = int(request.GET['uid']))
        if user_bd.count is None:
            request.session['uid'] = None
            widget = True
            return render(request, 'pravila.html', {'widget':widget, 'post_uid': request.GET['uid'], 'post_hash':request.GET['hash']})
    else:
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
    def get(self, request, *args, **kwargs):
        #Проверка переданных хеш ключей
        if not self.hashGet(request.GET):
            #********************
            return redirect('%s?%s'%(reverse('home'), 'error=nothash'))
        user = get_object_or_404(Users, user_id = int(request.GET['uid']))
        self.data_reguest = dict(uid = request.GET['uid'], hash = request.GET['hash'])
        if user.referals:#если есть ссылка, значит уже зарегистрирован(наличие ссылки - признак регистрации)
            if user.user_group and user.user_group.banan == True:
                #переход на страницу бана
                #********************
                return redirect('%s?uid=%s&hash=%s'%(reverse('banan'), request.GET['uid'], request.GET['hash']))
            #если какие-то группы не найдены в аккаунте ВК пользователя, то запускаем процедуру бана
            group_list = map(lambda x:x.group_info.group_id, user.check_group.all()) + map(lambda x:x.group_id, user.check_group_static.all())
            group_set = inspectionGroups(group_list, user)
            logger.debug(str(group_set))
            if group_set is not False and len(group_set) > 0:
                #Процедура бана
                gr_user = user.user_group
                gr_user.banan = True
                gr_user.queue = 0
                gr_user.count = 0
                gr_user.save()
                user.ban = True
                user.save()
                group = Groups.objects.get(group_info = gr_user)
                group.delete()
                self.stack(remove = 0)
                #********************
                return redirect('%s?uid=%s&hash=%s'%(reverse('banan'), request.GET['uid'], request.GET['hash']))

            elif group_set is not False and len(group_set) == 0:
                groups = Groups.objects.filter(behavior =1).filter(sort_position__lte = 40)
                if user.user_group:
                    day = datetime.utcnow()
                    statics = UserGroup.objects.filter(start_date__range = (datetime(day.year, day.month, day.day-2, 0, 0, 0), datetime(day.year, day.month, day.day-1, 0, 0, 0)))
                    static_recommended = int(round(len(statics)/40)) or 1
                    return render(request, 'user.html', {'user':user, 'user_group':user.user_group, 'data_post':self.data_reguest, 'groups': groups, 'sort_position':Groups.objects.get(group_info=user.user_group).sort_position, 'static_count': len(statics), 'static_recommended': static_recommended})
                else:
                    messages.success(request, 'Ваша группа была удалена, по причине нарушения правил.')
                    user.who_invited = None
                    user.save()
                    return render(request, 'user.html', {'user':user, 'user_group':u'группы нет', 'data_post':self.data_reguest, 'groups': groups, 'sort_position':u'группы нет'})
            else:
                #*******************
                #request.session['uid'] = None
                return redirect('%s?%s'%(reverse('home'), 'error=not_vk_connect'))
        else:#пользователь только регистрируется, пропускаем его на страницу регистрации
            inspection_ids(map(lambda x:x.group_info.group_id, Groups.objects.filter(behavior = 1).filter(sort_position__lte = 40)))
            if user.user_group:
                self.form = LinkGroupForm()
                self.form.fields['id_group'].widget.attrs['placeholder'] = user.user_group.link_group or user.user_group.group_id
                
            else:
                self.form = LinkGroupForm()
        if request.GET.get('amend'):
            self.button_title = u'Сменить группу'
        return super(GroupsView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.hashGet(request.POST):
            #************************
            #request.session['uid'] = None
            return redirect('%s?%s'%(reverse('home'), 'error=not_hash'))
        
        self.form = LinkGroupForm(request.POST)
        self.data_reguest = dict(uid = request.POST['uid'], hash = request.POST['hash'])
        #Процедура смены группы
        if 'amend' in request.POST and 'change' in request.POST:
            user = get_object_or_404(Users, user_id = int(request.POST['uid']))
            user.referals = None
            user.check_group.clear()
            user.who_invited = None
            user.save()
            return redirect('%s?uid=%s&hash=%s&amend=yes'%(reverse('group_list'), request.POST['uid'], request.POST['hash']))        

        if self.form.is_valid():
            self.data_form = self.form.cleaned_data['id_group']
            user = get_object_or_404(Users, user_id = int(request.POST['uid']))
            groups = map(lambda x: int(x), self.request.session['db'].split()) if self.request.session.get('db') else map(lambda x:x.group_id, StaticGroups.objects.all()) + map(lambda x:x.group_info.group_id, Groups.objects.filter(behavior = 1).filter(sort_position__lte = 40))
            #return render(request, 'groups_list.html', {'groups':groups})
            group_set = inspectionGroups(groups, user)
            logger.debug(str(group_set))
            if group_set is not False and len(group_set) == 0:
                inspect = inspection_id(self.data_form)
                if not inspect[0]:
                    self.message = inspect[1] if inspect[1] else u"<h3 class = 'error'>Что-то пошло не так, попробуйте повторить попытку</h3>"
                    return self.get(request)
                else:
                    self.data_form = int(inspect[2])
                    request.session['id_group'] = self.data_form
                if UserGroup.objects.filter(group_id = self.data_form).exists():
                    if UserGroup.objects.get(group_id = self.data_form).banan:
                        self.message = u"<h3 class = 'error'>Эта группа заблокирована, ВЫ не можете её регистрировать</h3>"
                        return self.get(request)
                #процедура регистрации
                self.no_entry_group = None
                result = self.registration(user, groups, self.data_form, request)
                if result:
                    if self.request.session.get('db'): del self.request.session['db']
                    groups = Groups.objects.filter(behavior =1).filter(sort_position__lte = 40)
                    day = datetime.utcnow()
                    statics = UserGroup.objects.filter(start_date__range = (datetime(day.year, day.month, day.day-2, 0, 0, 0), datetime(day.year, day.month, day.day-1, 0, 0, 0)))
                    static_recommended = int(round(len(statics)/40)) or 1
                    return render(request, 'user.html', {'user':user, 'user_group':user.user_group, 'data_post':self.data_reguest, 'groups': groups, 'sort_position':Groups.objects.get(group_info=user.user_group).sort_position, 'static_count': len(statics), 'static_recommended': static_recommended})
                    
            elif not group_set:
                #request.session['uid'] = None
                return redirect('%s?%s'%(reverse('home'), 'error=not_set_connect'))
            else:
                self.no_entry_group = map(entry, group_set)
                self.message = u"<h3 class = 'error'>Вы не подписались в %s групп</h3>"%len(self.no_entry_group)
                self.form = LinkGroupForm(initial = {'id_group':self.data_form})
                return self.get(request)
        else:
            self.message = u"<h3 class = 'message'>Введите ID вашей группы</h3>"
            self.form = LinkGroupForm()
            return self.get(request)
        #return render(request, 'groups_list.html', {'form':self.form, 'data_post':self.data_reguest})
    def get_context_data(self, **kwargs):
        context = super(GroupsView, self).get_context_data(**kwargs)
        context['form'] = self.form
        context['message'] = self.message
        context['data_post'] = self.data_reguest
        context['static_groups'] = StaticGroups.objects.all()
        if self.no_entry_group:
            context['notentry'] = self.no_entry_group
            context['static_groups'] = None
            context['groups'] = None
        if self.button_title:
            context['button'] = self.button_title
        
        
        return context
    def get_queryset(self):
        groups = Groups.objects.filter(behavior =1).filter(sort_position__lte = 40) 
        self.request.session['db'] = ' '.join(map(lambda x:str(x.group_id), StaticGroups.objects.all()) + map(lambda x:str(x.group_info.group_id), groups)) if len(StaticGroups.objects.all()) > 0 and len(groups) > 0 else None
        return groups

    
#ban & banan   
class UserBan(AppMixins, View):
    def get(self, request, *args, **kwargs):
        if self.hashGet(request.GET):
            context = dict(uid = request.GET['uid'], hash = request.GET['hash'])
            user = get_object_or_404(Users, user_id = int(request.GET['uid']))
            groups = Groups.objects.filter(behavior = 1).filter(sort_position__lte = 40)
            if not user.user_group.banan:
                #request.session['uid'] = None
                return redirect('%s'%(reverse('home')))
            elif user.ban:
                return render(request, 'ban.html', {'user':user, 'user_group':user.user_group, 'context':context, 'groups':groups})
            else:
                form = LinkGroupForm()
                return render(request, 'banan.html', {'user':user, 'user_group':user.user_group, 'form':form, 'context':context, 'groups':groups})
                
    def post(self, request, *args, **kwargs):
        if self.hashGet(request.POST):
            context = dict(uid = request.POST['uid'], hash = request.POST['hash'])
            user = get_object_or_404(Users, user_id = int(request.POST['uid']))
            groups = Groups.objects.filter(behavior = 1).filter(sort_position__lte = 40)
            if user.user_group.banan and user.ban:
                if user.user_group.queue > 0:
                    user.referals = None
                    user.check_group.clear()
                    user.who_invited = None
                    user_group = user.user_group
                    user_group.banan = False
                    user_group.queue = 0
                    user_group.save()
                    user.ban = False
                    user.save()
                    return redirect('%s?uid=%s&hash=%s'%(reverse('group_list'), request.POST['uid'], request.POST['hash']))
                else:
                    return render(request, 'ban.html', {'user':user, 'user_group':user.user_group, 'groups':groups, 'context':context, 'message':u"<h3 class = 'error'>Пока по вашей ссылке никто не прошел</h3>"})
            elif user.user_group.banan and not user.ban:
                user.referals = None
                user.check_group.clear()
                user.who_invited = None
                #user.user_group.clear()
                user.save()
                return redirect('%s?uid=%s&hash=%s'%(reverse('group_list'), request.POST['uid'], request.POST['hash']))
            else:
                #request.session['uid'] = None
                return redirect('%s'%(reverse('home')))
            
class PravilaView(AppMixins, View):
    def get(self, request, *args, **kwargs):
        pass
    def post(self, request, *args, **kwargs):
        pass

    
    
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


def ajax_session(request, sort_position):
    group = Groups.objects.filter(sort_position = sort_position)
    
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(serializers.serialize("json", group))#[group, group.group_info]
    return response

def redirect_home(request):
    return redirect('%s?%s'%(reverse('home'), 'error=not_page'))