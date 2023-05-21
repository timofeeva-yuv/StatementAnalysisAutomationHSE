from django.shortcuts import render, redirect
from .forms import InputUrlForm, UploadStudentsForm
import logging
from django.http import HttpResponseRedirect, HttpResponse
import os
import json
import sys
import re
import uuid
from django_q.tasks import async_task

sys.path.append('..')
from StatementAnalysis import StatementAnalysis

data_path = '..'
current_path = os.getcwd()


def processing_task(url, filenames):
    print("Async task started")
    os.chdir(data_path)
    StatementAnalysis(url=url, upd=False, student_files=filenames)
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
                os.chdir(current_path)
                request.session['root_table_url'] = url_root_sheet
                if url_root_sheet in existing_data:
                    return render(request, 'blank.html', {'title': 'Главная страница', 'content': ''})
                else:
                    return redirect('get_students')
            except Exception as e:
                logging.debug(f"Unable to create StatementAnalysis instance with given url. Error: {str(e)}")
                error = "Неправильный адрес таблицы с ведомостями"
        else:
            error = "Неправильный адрес таблицы с ведомостями"
    form = InputUrlForm()
    return render(request, 'input_root_url.html', {'form': form, 'error': error})


def handle_uploaded_file(f):
    filename = f'{uuid.uuid4()}_{f.name}'
    if not os.path.exists('../tmp'):
        os.mkdir('../tmp')
    with open(os.path.join('../tmp', filename), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return filename


def get_students(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    error = ''
    if request.method == 'POST':
        form = UploadStudentsForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('files')
            filenames = []
            for f in files:
                filenames.append(handle_uploaded_file(f))
            url_root_sheet = request.session['root_table_url']
            async_task(processing_task, url_root_sheet, filenames)
            return render(request, 'blank.html', {'title': 'Выполнение', 'content':
                'Выполняется обработка. Пожалуйста, подождите, это может занять несколько часов.'})
        else:
            print(form.errors)
            error = "Что-то пошло не так при загрузке файлов"
    form = UploadStudentsForm()
    return render(request, 'upload_students.html', {'form': form,
                                                    'error': error,
                                                    'root_table_url': request.session['root_table_url']})
