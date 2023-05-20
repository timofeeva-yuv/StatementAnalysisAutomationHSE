from django.shortcuts import render
import pandas as pd
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
        return HttpResponseRedirect('/settings')
    return render(request, 'alarms_base.html')


def unsuccessful(request):
    global data
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    if request.session.get('root_table_url', 'n/a') == 'n/a':
        return HttpResponseRedirect('/settings')
    if data is None:
        os.chdir(data_path)
        data = StatementAnalysis(request.session['root_table_url'], upd=False)
        os.chdir(current_path)
    results = pd.DataFrame(data.get('Неуспевающие'), columns=['ID', 'Имя студента',
                                                              'Доля неудов среди всех оценок студента'])
    return render(request, 'blank.html', {'title': 'Неуспевающие', 'content': results.to_html(index=False)})


def overstatement(request):
    global data
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    if request.session.get('root_table_url', 'n/a') == 'n/a':
        return HttpResponseRedirect('/settings')
    if data is None:
        os.chdir(data_path)
        data = StatementAnalysis(request.session['root_table_url'], upd=False)
        os.chdir(current_path)
    results = pd.DataFrame(data.get('Завышение'))
    return render(request, 'blank.html', {'title': 'Завышение', 'content': results.to_html(index=False)})
