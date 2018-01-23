# -*- coding: utf-8 -*-
from django.db import models

class TracebagModel(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    user_session = models.BigIntegerField(null = True, blank=True)
    info = models.TextField(blank=True)
    def __unicode__(self):
        if self.user_session:
            return '%s <%s>'%(self.date, self.user_session)
        else:
            return self.date
    class Meta:
        ordering = ['date']
        db_table = u'Только для супер-админов'
        verbose_name = u'Трейсбэг'
        verbose_name_plural = u'Трейсбэги'
# Create your models here.
