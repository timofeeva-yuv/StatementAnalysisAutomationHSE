

def generate_chart_tuple(chart, data):
    labels = chart.chart_labels.split('@')
    values = exec(chart.chart_values)
    loc = locals()
    exec(f"values = {chart.chart_values}", globals(), loc)
    values = list(loc["values"])
    chart_type = chart.chart_type
    chart_id = chart.id
    return chart_type, chart_id, labels, values
