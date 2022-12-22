from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
import pandas as pd

# Create your views here.


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    df = pd.read_csv('../data/2022-12-22_02:31:57/root.csv', sep=';')

    df['Type'] = df['Type'].fillna('Other')
    df['ErrorName'] = df['ErrorName'].fillna('Other')
    df['IsParsed'] = df['IsParsed'].fillna(True)

    doughnut_labels = ["Parsed", "Not parsed"]
    doughnut_colors = ['#23C552', '#F84F31']
    doughnut_values = [df[df['IsParsed'] == True]['IsParsed'].size,
                       df[df['IsParsed'] == False]['IsParsed'].size]

    double_bar_data_labels = ['Parsed', 'Not parsed']
    double_bar_labels = list(df['Type'].unique())
    double_bar_colors = ['#23C552', '#F84F31']
    double_bar_values = [[], []]
    helper = [True, False]
    for i in range(2):
        for label in double_bar_labels:
            double_bar_values[i].append(df.loc[(df['IsParsed'] == helper[i]) &
                                               (df['Type'] == label), 'Type'].size)

    bar_labels = list(df.loc[df['IsParsed'] == False, 'ErrorName'].unique())
    bar_color = '#F84F31'
    bar_values = []
    for label in bar_labels:
        bar_values.append(df.loc[(df['IsParsed'] == False) &
                                 (df['ErrorName'] == label), 'ErrorName'].size)

    params = {'doughnut_labels': doughnut_labels,
              'doughnut_colors': doughnut_colors,
              'doughnut_values': doughnut_values,
              'double_bar_data_labels0': double_bar_data_labels[0],
              'double_bar_data_labels1': double_bar_data_labels[1],
              'double_bar_labels': double_bar_labels,
              'double_bar_colors0': double_bar_colors[0],
              'double_bar_colors1': double_bar_colors[1],
              'double_bar_values0': double_bar_values[0],
              'double_bar_values1': double_bar_values[1],
              'bar_labels': bar_labels,
              'bar_values': bar_values,
              'bar_color': bar_color,
              'df': df.drop(columns=['URL', 'Text', 'ID']).to_html()}
    return render(request, 'dashboard.html', params)
