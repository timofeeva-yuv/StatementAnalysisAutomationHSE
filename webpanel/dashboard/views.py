from django.urls import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from .models import Chart, Dashboard
from .forms import DashboardForm, ChartForm
import sys
import os
import logging
import numpy as np
sys.path.append('..')
from .utils import scale_transform, ultimate_text_to_field
from StatementAnalysis import StatementAnalysis


data = None
data_path = '..'
current_path = os.getcwd()


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    if request.session.get('root_table_url', 'n/a') == 'n/a':
        return HttpResponseRedirect('/')
    user_dashboards = Dashboard.objects.filter(author_id=request.user.id)
    return render(request, 'dashboards_base.html', {'user_dashboards': user_dashboards})


def create_dashboard(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    if request.session.get('root_table_url', 'n/a') == 'n/a':
        return HttpResponseRedirect('/')
    error = ''
    form = None
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            exists = Dashboard.objects.filter(name=name, author_id=request.user.id).exists()
            if exists:
                error = 'Дэшборд с таким названием уже существует'
            else:
                dashboard = Dashboard(name=name, author_id=request.user.id)
                dashboard.save()
                return redirect('main')
        else:
            error = "Невозможно создать такой дэшборд"
    if form is None:
        form = DashboardForm()
    return render(request, 'dashboards_create.html', {'form': form,
                                                      'error': error})


def dashboard_details(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    if request.session.get('root_table_url', 'n/a') == 'n/a':
        return HttpResponseRedirect('/')
    try:
        dashboard_id = request.GET['id']
    except:
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого дэшборда не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    if dashboard_id == '':
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого дэшборда не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    try:
        dashboard = Dashboard.objects.get(id=dashboard_id, author_id=request.user.id)
    except:
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого дэшборда не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    charts = Chart.objects.filter(dashboard_id=dashboard_id)
    return render(request, 'dashboards_details.html', {'charts': charts, 'dashboard': dashboard})


def delete_dashboard(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    if request.session.get('root_table_url', 'n/a') == 'n/a':
        return HttpResponseRedirect('/')
    try:
        dashboard_id = request.GET['id']
    except:
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого дэшборда не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    if dashboard_id == '':
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого дэшборда не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    try:
        dashboard = Dashboard.objects.get(id=dashboard_id, author_id=request.user.id)
    except:
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого дэшборда не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    dashboard.delete()
    return redirect('main')


def rename_dashboard(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    if request.session.get('root_table_url', 'n/a') == 'n/a':
        return HttpResponseRedirect('/')
    try:
        dashboard_id = request.GET['id']
    except:
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого дэшборда не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    if dashboard_id == '':
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого дэшборда не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    try:
        dashboard = Dashboard.objects.get(id=dashboard_id, author_id=request.user.id)
    except:
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого дэшборда не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    error = ''
    form = None
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            exists = Dashboard.objects.filter(name=name, author_id=request.user.id).exists()
            if exists:
                error = 'Дэшборд с таким названием уже существует'
            else:
                dashboard.name = name
                dashboard.save()
                return redirect('main')
        else:
            error = "Невозможно переименовать дэшборд"
    if form is None:
        form = DashboardForm()
    return render(request, 'dashboards_rename.html', {'form': form,
                                                      'error': error})


def create_chart(request):
    global data
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    if request.session.get('root_table_url', 'n/a') == 'n/a':
        return HttpResponseRedirect('/')
    try:
        dashboard_id = request.GET['id']
    except:
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого графика не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    if dashboard_id == '':
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого графика не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    try:
        dashboard = Dashboard.objects.get(id=dashboard_id, author_id=request.user.id)
    except:
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого графика не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    if data is None:
        os.chdir(data_path)
        data = StatementAnalysis(request.session.get('root_table_url', 'n/a'), upd=False)
        os.chdir(current_path)
    error = ''
    form = None
    if request.method == 'POST':
        form = ChartForm(request.POST)
        if form.is_valid():
            try:
                distribution_source = form.cleaned_data['distribution_source']
                database_table = form.cleaned_data['database_table']
                distribution_scale = form.cleaned_data['distribution_scale']
                database_filters = form.cleaned_data['database_filters']
                chart_type = form.cleaned_data['chart_type']
                name = form.cleaned_data['name']
                if distribution_source == "Mark":
                    labels = [i for i in range(11)]
                    values = [0] * 11
                    for source in labels:
                        sql_command = f'SELECT "{source}" FROM {database_table}'
                        if database_filters is not None and not database_filters.isspace() and database_filters != '':
                            sql_command += " WHERE "
                            for elem in database_filters.split():
                                left = int(elem[0] == '(')
                                right = int(elem[-1] == ')')
                                sql_command += ' ' + left * '(' + \
                                               ultimate_text_to_field[database_table].get(elem.lower(), elem) + \
                                               right * ')' + ' '
                        sql_command += ';'
                        db = data.conn.cursor()
                        res = db.execute(sql_command)
                        result = np.array(res.fetchall())
                        db.close()
                        result = result[result != np.array(None)]
                        result = result.astype(int)
                        values[source] = np.sum(result)
                else:
                    sql_command = f"SELECT {distribution_source} FROM {database_table}"
                    if database_filters is not None and not database_filters.isspace() and database_filters != '':
                        sql_command += " WHERE "
                        for elem in database_filters.split():
                            left = int(elem[0] == '(')
                            right = int(elem[-1] == ')')
                            sql_command += ' ' + left * '(' + \
                                           ultimate_text_to_field[database_table].get(elem.lower(), elem) + \
                                           right * ')' + ' '
                    sql_command += ';'
                    db = data.conn.cursor()
                    res = db.execute(sql_command)
                    result = res.fetchall()
                    db.close()
                    labels = [i for i in range(11)]
                    values = [0] * 11
                    for elem in result:
                        elem = elem[0]
                        if elem is not None:
                            elem = round(elem)
                            elem = max(elem, 0)
                            elem = min(elem, 10)
                            values[elem] += 1
                if distribution_scale == '5':
                    labels = ['Неуд', 'Удовл', 'Хор', 'Отл']
                    old_values = values[:]
                    values = [0] * 4
                    for i in range(11):
                        values[scale_transform[i]] += old_values[i]
                chart = Chart(dashboard_id=dashboard_id,
                              name=name,
                              chart_type=chart_type,
                              chart_labels=str(labels),
                              chart_values=str(values),
                              distribution_source=distribution_source,
                              database_table=database_table,
                              distribution_scale=distribution_scale,
                              database_filters=database_filters)
                if 'build' in request.POST:
                    chart.id = 1
                    return render(request, 'create_graph.html', {'form': form,
                                                                 'chart': chart,
                                                                 'error': error})
                else:
                    exist = Chart.objects.filter(name=name, dashboard_id=dashboard_id).exists()
                    if exist:
                        error = 'График с таким именем уже есть на этом дэшборде'
                    else:
                        chart.save()
                        redirect_url = reverse('details')
                        redirect_url += f"?id={dashboard_id}"
                        return redirect(redirect_url)
            except Exception as e:
                logging.debug(f"Unable to generate chart with given data. Error: {str(e)}")
                print(f"Unable to generate chart with given data. Error: {str(e)}")
                error = "Невозможно построить такой график"
        else:
            error = "Невозможно создать такой график"
    if form is None:
        form = ChartForm()
    return render(request, 'create_graph.html', {'form': form,
                                                 'chart': None,
                                                 'error': error})


def edit_chart(request):
    global data
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    if request.session.get('root_table_url', 'n/a') == 'n/a':
        return HttpResponseRedirect('/')
    try:
        dashboard_id = request.GET['id']
    except:
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого графика не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    if dashboard_id == '':
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого графика не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    try:
        chart_id = request.GET['chart-id']
    except:
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого графика не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    if chart_id == '':
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого графика не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    try:
        dashboard = Dashboard.objects.get(id=dashboard_id, author_id=request.user.id)
    except:
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого графика не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    try:
        chart = Chart.objects.get(id=chart_id, dashboard_id=dashboard_id)
    except:
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого графика не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    if data is None:
        os.chdir(data_path)
        data = StatementAnalysis(request.session.get('root_table_url', 'n/a'), upd=False)
        os.chdir(current_path)
    error = ''
    form = ChartForm(instance=chart)
    if request.method == 'POST':
        form = ChartForm(request.POST)
        if form.is_valid():
            try:
                distribution_source = form.cleaned_data['distribution_source']
                database_table = form.cleaned_data['database_table']
                distribution_scale = form.cleaned_data['distribution_scale']
                database_filters = form.cleaned_data['database_filters']
                chart_type = form.cleaned_data['chart_type']
                name = form.cleaned_data['name']
                if distribution_source == "Mark":
                    labels = [i for i in range(11)]
                    values = [0] * 11
                    for source in labels:
                        sql_command = f'SELECT "{source}" FROM {database_table}'
                        if database_filters is not None and not database_filters.isspace() and database_filters != '':
                            sql_command += " WHERE "
                            for elem in database_filters.split():
                                left = int(elem[0] == '(')
                                right = int(elem[-1] == ')')
                                sql_command += ' ' + left * '(' + \
                                               ultimate_text_to_field[database_table].get(elem.lower(), elem) + \
                                               right * ')' + ' '
                        sql_command += ';'
                        db = data.conn.cursor()
                        res = db.execute(sql_command)
                        result = np.array(res.fetchall())
                        db.close()
                        result = result[result != np.array(None)]
                        result = result.astype(int)
                        values[source] = np.sum(result)
                else:
                    sql_command = f"SELECT {distribution_source} FROM {database_table}"
                    if database_filters is not None and not database_filters.isspace() and database_filters != '':
                        sql_command += " WHERE "
                        for elem in database_filters.split():
                            left = int(elem[0] == '(')
                            right = int(elem[-1] == ')')
                            sql_command += ' ' + left * '(' + \
                                           ultimate_text_to_field[database_table].get(elem.lower(), elem) + \
                                           right * ')' + ' '
                    sql_command += ';'
                    db = data.conn.cursor()
                    res = db.execute(sql_command)
                    result = res.fetchall()
                    db.close()
                    labels = [i for i in range(11)]
                    values = [0] * 11
                    for elem in result:
                        elem = elem[0]
                        if elem is not None:
                            elem = round(elem)
                            elem = max(elem, 0)
                            elem = min(elem, 10)
                            values[elem] += 1
                if distribution_scale == '5':
                    labels = ['Неуд', 'Удовл', 'Хор', 'Отл']
                    old_values = values[:]
                    values = [0] * 4
                    for i in range(11):
                        values[scale_transform[i]] += old_values[i]
                chart = Chart(id=chart_id,
                              dashboard_id=dashboard_id,
                              name=name,
                              chart_type=chart_type,
                              chart_labels=str(labels),
                              chart_values=str(values),
                              distribution_source=distribution_source,
                              database_table=database_table,
                              distribution_scale=distribution_scale,
                              database_filters=database_filters)
                if 'build' in request.POST:
                    return render(request, 'create_graph.html', {'form': form,
                                                                 'chart': chart,
                                                                 'error': error})
                else:
                    exist = Chart.objects.filter(name=name, dashboard_id=dashboard_id).exists()
                    if exist:
                        ex = Chart.objects.get(name=name, dashboard_id=dashboard_id)
                        if ex.id != int(chart_id):
                            error = 'График с таким именем уже есть на этом дэшборде'
                        else:
                            chart.save()
                            redirect_url = reverse('details')
                            redirect_url += f"?id={dashboard_id}"
                            return redirect(redirect_url)
                    else:
                        chart.save()
                        redirect_url = reverse('details')
                        redirect_url += f"?id={dashboard_id}"
                        return redirect(redirect_url)
            except Exception as e:
                logging.debug(f"Unable to generate chart with given data. Error: {str(e)}")
                print(f"Unable to generate chart with given data. Error: {str(e)}")
                error = "Невозможно построить такой график"
        else:
            error = "Невозможно создать такой график"
    if form is None:
        form = ChartForm()
        chart = None
    else:
        distribution_source = chart.distribution_source
        database_table = chart.database_table
        distribution_scale = chart.distribution_scale
        database_filters = chart.database_filters
        chart_type = chart.chart_type
        name = chart.name
        if distribution_source == "Mark":
            labels = [i for i in range(11)]
            values = [0] * 11
            for source in labels:
                sql_command = f'SELECT "{source}" FROM {database_table}'
                if database_filters is not None and not database_filters.isspace() and database_filters != '':
                    sql_command += " WHERE "
                    for elem in database_filters.split():
                        left = int(elem[0] == '(')
                        right = int(elem[-1] == ')')
                        sql_command += ' ' + left * '(' + \
                                       ultimate_text_to_field[database_table].get(elem.lower(), elem) + \
                                       right * ')' + ' '
                sql_command += ';'
                db = data.conn.cursor()
                res = db.execute(sql_command)
                result = np.array(res.fetchall())
                db.close()
                result = result[result != np.array(None)]
                result = result.astype(int)
                values[source] = np.sum(result)
        else:
            sql_command = f"SELECT {distribution_source} FROM {database_table}"
            if database_filters is not None and not database_filters.isspace() and database_filters != '':
                sql_command += " WHERE "
                for elem in database_filters.split():
                    left = int(elem[0] == '(')
                    right = int(elem[-1] == ')')
                    sql_command += ' ' + left * '(' + \
                                   ultimate_text_to_field[database_table].get(elem.lower(), elem) + \
                                   right * ')' + ' '
            sql_command += ';'
            db = data.conn.cursor()
            res = db.execute(sql_command)
            result = res.fetchall()
            db.close()
            labels = [i for i in range(11)]
            values = [0] * 11
            for elem in result:
                elem = elem[0]
                if elem is not None:
                    elem = round(elem)
                    elem = max(elem, 0)
                    elem = min(elem, 10)
                    values[elem] += 1
        if distribution_scale == '5':
            labels = ['Неуд', 'Удовл', 'Хор', 'Отл']
            old_values = values[:]
            values = [0] * 4
            for i in range(11):
                values[scale_transform[i]] += old_values[i]
        chart = Chart(id=chart_id,
                      dashboard_id=dashboard_id,
                      name=name,
                      chart_type=chart_type,
                      chart_labels=str(labels),
                      chart_values=str(values),
                      distribution_source=distribution_source,
                      database_table=database_table,
                      distribution_scale=distribution_scale,
                      database_filters=database_filters)
    return render(request, 'change_graph.html', {'form': form,
                                                 'chart': chart,
                                                 'error': error})


def delete_chart(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    if request.session.get('root_table_url', 'n/a') == 'n/a':
        return HttpResponseRedirect('/')
    try:
        dashboard_id = request.GET['id']
    except:
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого графика не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    if dashboard_id == '':
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого графика не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    try:
        chart_id = request.GET['chart-id']
    except:
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого графика не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    if chart_id == '':
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого графика не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    try:
        dashboard = Dashboard.objects.get(id=dashboard_id, author_id=request.user.id)
    except:
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого графика не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    try:
        chart = Chart.objects.get(id=chart_id, dashboard_id=dashboard_id)
    except:
        return render(request, 'blank.html', {'title': 'Ошибка',
                                              'content': '<p style="color: red">Такого графика не существует,'
                                                         ' или у вас нет к нему доступа</p>'})
    chart.delete()
    redirect_url = reverse('details')
    redirect_url += f"?id={dashboard_id}"
    return redirect(redirect_url)
