from django import forms


class InputUrlForm(forms.Form):
    root_table_url = forms.CharField(label='Адрес таблицы с ведомостями', max_length=256,
                                     initial="https://docs.google.com/spreadsheets/d/1IyfSPiiR0DUxYuConiYzuokM2hUQbOBpuJAeAlGi7kc") # noqa