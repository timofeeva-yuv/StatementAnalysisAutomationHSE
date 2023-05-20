from django.urls import reverse
import pandas as pd
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
import sys
import os
from .forms import DatabaseRequestForm
from .utils import root_fields, students_fields, ultimate_text_to_field, ultimate_field_to_text, ultimate_fields_text
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
    if request.session.get('root_table_url', 'n/a') == 'n/a':
        return HttpResponseRedirect('/settings')
    if data is None:
        os.chdir(data_path)
        data = StatementAnalysis(request.session.get('root_table_url', 'n/a'), upd=False)
        os.chdir(current_path)
    error = ''
    form = None
    if request.method == 'POST':
        form = DatabaseRequestForm(request.POST)
        if form.is_valid():
            database_table = form.cleaned_data['database_table']
            database_select = form.cleaned_data['database_select']
            database_filters = form.cleaned_data['database_filters']
            sql_command = "SELECT "
            for elem in database_select:
                sql_command += elem + ', '
            sql_command = sql_command.strip(', ')
            sql_command += f" FROM {database_table}"
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
            cols = []
            for elem in database_select:
                cols.append(ultimate_field_to_text[database_table].get(elem, elem))
            df = pd.DataFrame(result, columns=cols)
            for i in range(len(df)):
                df.iloc[i]['Имя'] = f"Студент {i + 1}"
                df.iloc[i]['Группа'] = f"Группа студента {i + 1}"
            return render(request, 'view_database.html', {'form': form,
                                                          'error': error,
                                                          'root_fields': root_fields,
                                                          'students_fields': students_fields,
                                                          'table': df.to_html()})
    if form is None:
        form = DatabaseRequestForm()
    return render(request, 'view_database.html', {'form': form,
                                                  'error': error,
                                                  'root_fields': root_fields,
                                                  'students_fields': students_fields})
