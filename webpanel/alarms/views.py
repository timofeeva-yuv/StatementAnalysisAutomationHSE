from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
import sys
import os
sys.path.append('..')
from StatementAnalysis import StatementAnalysis


data = None
data_path = '..'
current_path = os.getcwd()
alarm_types = ("Неуспевающие", "Завышение")


def index(request):
    global data
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    if request.session.get('root_table_url', 'n/a') == 'n/a':
        return HttpResponseRedirect('/')
    if data is None:
        os.chdir(data_path)
        data = StatementAnalysis(request.session['root_table_url'], upd=False)
        os.chdir(current_path)
    return HttpResponse(data.get(alarm_types[0]))

