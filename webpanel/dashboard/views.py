import pandas as pd
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from .models import Chart, Dashboard
from .utils import generate_chart_tuple

# Create your views here.


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')
    data = pd.read_csv('../data/2023-04-10_20:31:34/root.csv', sep=';')
    dashboard, _ = Dashboard.objects.get_or_create(
        author_id=request.user.id,
        main=True,
        defaults={"name": "General information"}
    )

    scores_distrib_chart, _ = Chart.objects.get_or_create(
        dashboard_id=dashboard.id,
        defaults={"name": "Scores distribution",
                 "chart_type": "bar-chart.html",
                 "chart_labels": "Fail@Satisfactory@Good@Excellent",
                 "chart_values": "data.groupby(labels)[labels].sum().sum().values"}
    )
    response = dict()
    response['charts'] = [generate_chart_tuple(scores_distrib_chart, data)]
    print(response['charts'])
    return render(request, 'dashboard.html', response)
