from django.utils.safestring import mark_safe


root_fields = (
    (mark_safe('"Level"'), "Уровень"),
    (mark_safe('"Program"'), "ОП"),
    (mark_safe('"Year"'), "Курс"),
    (mark_safe('"Module"'), "Модуль"),
    (mark_safe('"Discipline"'), "Предмет"),
    (mark_safe('"Teacher"'), "Преподаватель"),
    (mark_safe('"MeanMark"'), "Средняя оценка"),
    (mark_safe('"MeanPositiveMark"'), "Средняя ненулевая оценка"),
    (mark_safe('"MarkSum"'), "Сумма оценок"),
    (mark_safe('"MarkCount"'), "Количество оценок"),
    (mark_safe('"MarkPositiveCount"'), "Количество ненулевых_оценок"),
    (mark_safe('"10"'), "Количество 10"),
    (mark_safe('"9"'), "Количество 9"),
    (mark_safe('"8"'), "Количество 8"),
    (mark_safe('"7"'), "Количество 7"),
    (mark_safe('"6"'), "Количество 6"),
    (mark_safe('"5"'), "Количество 5"),
    (mark_safe('"4"'), "Количество 4"),
    (mark_safe('"3"'), "Количество 3"),
    (mark_safe('"2"'), "Количество 2"),
    (mark_safe('"1"'), "Количество 1"),
    (mark_safe('"0"'), "Количество 0"),
)
root_field_to_text = dict(root_fields)
root_text_to_field = {b.lower(): a for a, b in root_fields}
root_text_to_field['+'] = '+'
root_text_to_field['-'] = '-'
root_text_to_field['/'] = '/'
root_text_to_field['*'] = '*'
root_text_to_field['И'] = 'AND'
root_text_to_field['ИЛИ'] = 'OR'
root_text_to_field['='] = '='
root_text_to_field['!='] = '!='
root_fields_database = list(root_field_to_text.keys())
root_fields_text = list(root_text_to_field.keys())


students_fields = (
    (mark_safe('"Name"'), "Имя"),
    (mark_safe('"Group"'), "Группа"),
    (mark_safe('"Program"'), "ОП"),
    (mark_safe('"Year"'), "Курс"),
    (mark_safe('"MeanMark"'), "Средняя оценка"),
    (mark_safe('"MeanPositiveMark"'), "Средняя ненулевая оценка"),
    (mark_safe('"MarkSum"'), "Сумма оценок"),
    (mark_safe('"MarkCount"'), "Количество оценок"),
    (mark_safe('"MarkPositiveCount"'), "Количество ненулевых оценок"),
    (mark_safe('"10"'), "Количество 10"),
    (mark_safe('"9"'), "Количество 9"),
    (mark_safe('"8"'), "Количество 8"),
    (mark_safe('"7"'), "Количество 7"),
    (mark_safe('"6"'), "Количество 6"),
    (mark_safe('"5"'), "Количество 5"),
    (mark_safe('"4"'), "Количество 4"),
    (mark_safe('"3"'), "Количество 3"),
    (mark_safe('"2"'), "Количество 2"),
    (mark_safe('"1"'), "Количество 1"),
    (mark_safe('"0"'), "Количество 0"),
)
students_field_to_text = dict(students_fields)
students_text_to_field = {b.lower(): a for a, b in students_fields}
students_text_to_field['+'] = '+'
students_text_to_field['-'] = '-'
students_text_to_field['/'] = '/'
students_text_to_field['*'] = '*'
students_text_to_field['И'] = 'AND'
students_text_to_field['ИЛИ'] = 'OR'
students_text_to_field['='] = '='
students_text_to_field['!='] = '!='
students_fields_database = list(students_field_to_text.keys())
students_fields_text = list(students_text_to_field.keys())

ultimate_text_to_field = {'root': root_text_to_field,
                          'students': students_text_to_field}

ultimate_fields = {'root': root_fields,
                   'students': students_fields}

ultimate_fields_text = {'root': root_fields_text,
                        'students': students_fields_text}

ultimate_fields_database = {'root': root_fields_database,
                            'students': students_fields_database}

ultimate_field_to_text = {'root': root_field_to_text,
                          'students': students_field_to_text}


scale_transform = {
    0: 0,
    1: 0,
    2: 0,
    3: 0,
    4: 1,
    5: 1,
    6: 2,
    7: 2,
    8: 3,
    9: 3,
    10: 3,
}

all_fields = (
    (mark_safe('"Level"'), "Уровень"),
    (mark_safe('"Program"'), "ОП"),
    (mark_safe('"Module"'), "Модуль"),
    (mark_safe('"Discipline"'), "Предмет"),
    (mark_safe('"Teacher"'), "Преподаватель"),
    (mark_safe('"Name"'), "Имя"),
    (mark_safe('"Group"'), "Группа"),
    (mark_safe('"Program"'), "ОП"),
    (mark_safe('"Year"'), "Курс"),
    (mark_safe('"MeanMark"'), "Средняя оценка"),
    (mark_safe('"MeanPositiveMark"'), "Средняя ненулевая оценка"),
    (mark_safe('"MarkSum"'), "Сумма оценок"),
    (mark_safe('"MarkCount"'), "Количество оценок"),
    (mark_safe('"MarkPositiveCount"'), "Количество ненулевых оценок"),
    (mark_safe('"10"'), "Количество 10"),
    (mark_safe('"9"'), "Количество 9"),
    (mark_safe('"8"'), "Количество 8"),
    (mark_safe('"7"'), "Количество 7"),
    (mark_safe('"6"'), "Количество 6"),
    (mark_safe('"5"'), "Количество 5"),
    (mark_safe('"4"'), "Количество 4"),
    (mark_safe('"3"'), "Количество 3"),
    (mark_safe('"2"'), "Количество 2"),
    (mark_safe('"1"'), "Количество 1"),
    (mark_safe('"0"'), "Количество 0"),
)
