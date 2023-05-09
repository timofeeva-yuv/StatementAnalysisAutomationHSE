from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from .forms import InputUrlForm
import os
import sys
import logging
sys.path.append('..')
from StatementAnalysis import StatementAnalysis


data_path = '..'
current_path = os.getcwd()


def index(request):
    if request.user.is_authenticated:
        if request.session.get('root_table_url', 'n/a') == 'n/a':
            error = ''
            if request.method == 'POST':
                form = InputUrlForm(request.POST)
                if form.is_valid():
                    root_table_field = form.cleaned_data['root_table_url']
                    try:
                        os.chdir(data_path)
                        StatementAnalysis(root_table_field, upd=False)
                        os.chdir(current_path)
                        request.session['root_table_url'] = root_table_field
                    except Exception as e:
                        logging.debug(f"Unable to create StatementAnalysis instance with given url. Error: {str(e)}")
                        error = "Неправильный адрес таблицы с ведомостями"
                else:
                    error = "Неправильный адрес таблицы с ведомостями"
            form = InputUrlForm()
            return render(request, 'input_root_url.html', {'form': form, 'error': error})
        return HttpResponseRedirect('/alarms')
    error = ''
    if request.method == "POST":
        user = authenticate(request, username=request.POST['username'], password=request.POST['pass'])
        if user is not None:
            login(request, user)
            request.session['auth'] = 1
            return HttpResponseRedirect('/')
        else:
            error = "Invalid username and/or password"
    return render(request, "login.html", {'error': error})
