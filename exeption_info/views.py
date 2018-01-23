# -*- coding: utf-8 -*-
from django.shortcuts import render
import traceback
from exeption_info.models import TracebagModel

def tracaBag(request):
    TracebagModel.objects.create(user_session = request.session.get('uid'), info = traceback.format_exc())
    return render(request, '500.html')
# Create your views here.
