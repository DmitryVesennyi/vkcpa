# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
from vkcpa.UserVk2 import UserAutentific, GroupsView, UserBan, pravila, ajax_session, UserRoom, exit_resource

urlpatterns = patterns('',
    # Examples:
    url(r'^$', UserAutentific.as_view(), name='home'),
    url(r'^(?P<referal>ref[A-Za-z0-9_-]+)/$', UserAutentific.as_view(), name='home'),
    url(r'^group/$', GroupsView.as_view(), name='group_list'),
    url(r'^banan/$', UserBan.as_view(), name='banan'),
    url(r'^partneram/$', TemplateView.as_view(template_name='partneram.html'), name='partneram'),
    url(r'^pravila/$', pravila, name='pravila'),
    url(r'^kak_popast/$', TemplateView.as_view(template_name='kak_popast.html'), name='kak_popast'),
    url(r'^4cf51a96d6/', include(admin.site.urls), name = 'admin'),
    url(r'^updates/(?P<sort_position>\d+)/$', ajax_session),
    url(r'^exit/$', exit_resource, name='exit'),
    url(r'^UserKabinet/$', UserRoom.as_view(), name='useroom'),
)
#handler404 = 'exeption_info.views.tracaBag'
handler404 = 'vkcpa.UserVk.redirect_home'
handler500 = 'exeption_info.views.tracaBag'
