from django.shortcuts import render
from .forms import InputUrlForm
import logging
from django.http import HttpResponseRedirect
import os
import json
import sys
import re
from django_q.tasks import async_task

sys.path.append('..')
from StatementAnalysis import StatementAnalysis

data_path = '..'
current_path = os.getcwd()


def processing_task(url):
    print("Async task started")
    os.chdir(data_path)
    StatementAnalysis(url=url, upd=False)
    os.chdir(current_path)


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    error = ''
    if request.method == 'POST':
        form = InputUrlForm(request.POST)
        if form.is_valid():
            root_table_field = form.cleaned_data['root_table_url']
            try:
                os.chdir(data_path)
                url_root_sheet = root_table_field
                url_root_sheet = re.sub(r"/edit(.*)", '', url_root_sheet)
                with open("data/data.json", "r") as f:
                    existing_data = json.load(f)
                if url_root_sheet in existing_data:
                    os.chdir(current_path)
                    request.session['root_table_url'] = root_table_field
                    return render(request, 'blank.html', {'title': 'Главная страница', 'content': ''})
                else:
                    async_task(processing_task, url_root_sheet)
                    return render(request, 'blank.html', {'title': 'Выполнение', 'content':
                        'Выполняется обработка. Пожалуйста, подождите, это может занять до часа.'})
            except Exception as e:
                logging.debug(f"Unable to create StatementAnalysis instance with given url. Error: {str(e)}")
                error = "Неправильный адрес таблицы с ведомостями"
        else:
            error = "Неправильный адрес таблицы с ведомостями"
    form = InputUrlForm()
    return render(request, 'input_root_url.html', {'form': form, 'error': error})