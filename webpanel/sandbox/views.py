from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from .forms import SelectTypeForm, DistributionChartForm, ConstantForm
from .utils import scale_transform, ultimate_text_to_field, ultimate_fields_text, ultimate_field_to_text, \
    root_fields, students_fields, aggregation_funcs
import sys
import os
import logging
import numpy as np

sys.path.append('..')
from StatementAnalysis import StatementAnalysis

data = None
data_path = '..'
current_path = os.getcwd()


def index(request):
    global data
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    if request.session.get('root_table_url', 'n/a') != 'n/a':
        os.chdir(data_path)
        data = StatementAnalysis(request.session.get('root_table_url', 'n/a'), upd=False)
        os.chdir(current_path)
        return redirect('select_type')
    return HttpResponseRedirect('/settings')


def select_type(request):
    global data
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    if request.session.get('root_table_url', 'n/a') == 'n/a':
        return HttpResponseRedirect('/settings')
    root_table_url = request.session.get('root_table_url')
    if root_table_url is None or data is None:
        return redirect('input_url')
    error = ''
    form = None
    if request.method == 'POST':
        form = SelectTypeForm(request.POST)
        if form.is_valid():
            chart_type_name = form.cleaned_data['chart_type_name']
            request.session['chart_type_name'] = chart_type_name
            return redirect(chart_type_name)
        else:
            error = "Неправильный тип графика"
    if form is None:
        form = SelectTypeForm()
    return render(request, 'sandbox_template_2.html', {'form': form,
                                                       'root_table_url': root_table_url,
                                                       'error': error})


def distribution_chart(request):
    global data
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    if request.session.get('root_table_url', 'n/a') == 'n/a':
        return HttpResponseRedirect('/settings')
    root_table_url = request.session.get('root_table_url')
    chart_type_name = request.session.get('chart_type_name')
    if root_table_url is None or data is None:
        return redirect('input_url')
    if chart_type_name is None or chart_type_name != "distribution_chart":
        return redirect('select_type')
    error = ''
    form = None
    if request.method == 'POST':
        form = DistributionChartForm(request.POST)
        if form.is_valid():
            try:
                distribution_source = form.cleaned_data['distribution_source']
                database_table = form.cleaned_data['database_table']
                distribution_scale = form.cleaned_data['distribution_scale']
                database_filters = form.cleaned_data['database_filters']
                if distribution_source == "Mark":
                    labels = [i for i in range(11)]
                    values = [0] * 11
                    for source in labels:
                        sql_command = f'SELECT "{source}" FROM {database_table}'
                        if database_filters is not None and not database_filters.isspace() and database_filters != '':
                            sql_command += " WHERE "
                            for elem in database_filters.split():
                                if elem.lower().replace('_', ' ') in ultimate_fields_text[database_table]:
                                    elem = elem.lower().replace('_', ' ')
                                left = int(elem[0] == '(')
                                right = int(elem[-1] == ')')
                                if elem.count(';') == 0:
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
                            if elem.lower().replace('_', ' ') in ultimate_fields_text[database_table]:
                                elem = elem.lower().replace('_', ' ')
                            left = int(elem[0] == '(')
                            right = int(elem[-1] == ')')
                            if elem.count(';') == 0:
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
                return render(request, 'sandbox_distribution_chart.html', {'form': form,
                                                                           'root_table_url': root_table_url,
                                                                           'chart_type_name': SelectTypeForm.types_dict[
                                                                               chart_type_name],  # noqa
                                                                           'error': error,
                                                                           'chart_type': 'distribution-chart.html',
                                                                           'chart_id': '1',
                                                                           'labels': labels,
                                                                           'values': values})
            except Exception as e:
                logging.debug(f"Unable to generate chart with given data. Error: {str(e)}")
                print(f"Unable to generate chart with given data. Error: {str(e)}")
                error = "Невозможно построить такой график"
        else:
            error = 'Невозможно построить такой график'
    if form is None:
        form = DistributionChartForm()
    return render(request, 'sandbox_distribution_chart.html', {'form': form,
                                                               'root_table_url': root_table_url,
                                                               'chart_type_name': SelectTypeForm.types_dict[
                                                                   chart_type_name],  # noqa
                                                               'error': error})


def distribution_doughnut_chart(request):
    global data
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    if request.session.get('root_table_url', 'n/a') == 'n/a':
        return HttpResponseRedirect('/settings')
    root_table_url = request.session.get('root_table_url')
    chart_type_name = request.session.get('chart_type_name')
    if root_table_url is None or data is None:
        return redirect('input_url')
    if chart_type_name is None or chart_type_name != "distribution_doughnut_chart":
        return redirect('select_type')
    error = ''
    form = None
    if request.method == 'POST':
        form = DistributionChartForm(request.POST)
        if form.is_valid():
            try:
                distribution_source = form.cleaned_data['distribution_source']
                database_table = form.cleaned_data['database_table']
                distribution_scale = form.cleaned_data['distribution_scale']
                database_filters = form.cleaned_data['database_filters']
                if distribution_source == "Mark":
                    labels = [i for i in range(11)]
                    values = [0] * 11
                    for source in labels:
                        sql_command = f'SELECT "{source}" FROM {database_table}'
                        if database_filters is not None and not database_filters.isspace() and database_filters != '':
                            sql_command += " WHERE "
                            for elem in database_filters.split():
                                if elem.lower().replace('_', ' ') in ultimate_fields_text[database_table]:
                                    elem = elem.lower().replace('_', ' ')
                                left = int(elem[0] == '(')
                                right = int(elem[-1] == ')')
                                if elem.count(';') == 0:
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
                            if elem.lower().replace('_', ' ') in ultimate_fields_text[database_table]:
                                elem = elem.lower().replace('_', ' ')
                            left = int(elem[0] == '(')
                            right = int(elem[-1] == ')')
                            if elem.count(';') == 0:
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
                return render(request, 'sandbox_distribution_chart.html', {'form': form,
                                                                           'root_table_url': root_table_url,
                                                                           'chart_type_name': SelectTypeForm.types_dict[
                                                                               chart_type_name],  # noqa
                                                                           'error': error,
                                                                           'chart_type': 'distribution-doughnut-chart.html',
                                                                           'chart_id': '1',
                                                                           'labels': labels,
                                                                           'values': values})
            except Exception as e:
                logging.debug(f"Unable to generate chart with given data. Error: {str(e)}")
                print(f"Unable to generate chart with given data. Error: {str(e)}")
                error = "Невозможно построить такой график"
        else:
            error = 'Невозможно построить такой график'
    if form is None:
        form = DistributionChartForm()
    return render(request, 'sandbox_distribution_chart.html', {'form': form,
                                                               'root_table_url': root_table_url,
                                                               'chart_type_name': SelectTypeForm.types_dict[
                                                                   chart_type_name],  # noqa
                                                               'error': error})


def constant_chart(request):
    global data
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    if request.session.get('root_table_url', 'n/a') == 'n/a':
        return HttpResponseRedirect('/settings')
    if data is None:
        os.chdir(data_path)
        data = StatementAnalysis(request.session.get('root_table_url', 'n/a'), upd=False)
        os.chdir(current_path)
    error = ''
    form = None
    if request.method == 'POST':
        form = ConstantForm(request.POST)
        if form.is_valid():
            database_table = form.cleaned_data['database_table']
            database_select = form.cleaned_data['database_select']
            database_filters = form.cleaned_data['database_filters']
            aggregation = form.cleaned_data['aggregation']
            sql_command = f"SELECT {database_select} FROM {database_table}"
            if database_filters is not None and not database_filters.isspace() and database_filters != '':
                sql_command += " WHERE "
                for elem in database_filters.split():
                    if elem.lower().replace('_', ' ') in ultimate_fields_text[database_table]:
                        elem = elem.lower().replace('_', ' ')
                    left = int(elem[0] == '(')
                    right = int(elem[-1] == ')')
                    if elem.count(';') == 0:
                        sql_command += ' ' + left * '(' + \
                                       ultimate_text_to_field[database_table].get(elem.lower(), elem) + \
                                       right * ')' + ' '
            sql_command += ';'
            db = data.conn.cursor()
            res = db.execute(sql_command)
            result = np.array(res.fetchall())
            db.close()
            result = result[result != np.array(None)]
            value = aggregation_funcs[aggregation](result)
            return render(request, 'sandbox_constant.html', {'form': form,
                                                             'error': error,
                                                             'value': value})
    if form is None:
        form = ConstantForm()
    return render(request, 'sandbox_constant.html', {'form': form,
                                                     'error': error})
