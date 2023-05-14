from .utils import root_fields_text, students_fields_text
from django.http import JsonResponse


def get_hints(request):
    input_text = request.GET.get('input_text', '')
    table = request.GET.get('table', '')
    if table == '':
        return JsonResponse([], safe=False)
    if table == 'root':
        all_values = root_fields_text
    else:
        all_values = students_fields_text

    hints = get_field_suggestions(all_values, '')

    if input_text.strip():
        last_word = input_text.split()[-1]
        if last_word != '(' and last_word != ')':
            last_word = last_word.strip('(').strip(')')
        if input_text[-1] == ' ' and last_word in all_values:
            hints = get_operator_suggestions()
        elif input_text[-1] == ' ' and last_word in get_operator_suggestions():
            hints = get_field_suggestions(all_values, '')
        elif input_text[-1] == ' ':
            hints = get_operator_suggestions()
        elif not last_word:
            hints = get_field_suggestions(all_values, '')
        elif last_word in get_operator_combinations():
            if last_word == '(':
                hints = get_field_suggestions(all_values, '')
            else:
                hints = get_operator_suggestions()
        else:
            hints = get_field_suggestions(all_values, last_word)

    return JsonResponse(hints, safe=False)


def get_field_suggestions(all_values, last_word):
    return [value for value in all_values if value.lower().startswith(last_word.lower())]


def get_operator_suggestions():
    return ["+", "-", "/", "*", "=", "!=", "И", "ИЛИ", "(", ")", '>', '>=', '<', '<=']


def get_operator_combinations():
    return ["+", "-", "/", "*", "=", "!", "И", "ИЛ", "ИЛИ", "(", ")", "!=", '>', '>=', '<', '<=']
