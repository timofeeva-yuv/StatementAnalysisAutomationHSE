root_fields = (
    ("Level", "Уровень"),
    ("Program", "ОП"),
    ("Year", "Курс"),
    ("Module", "Модуль"),
    ("Discipline", "Предмет"),
    ("Teacher", "Преподаватель"),
    ("MeanMark", "Средняя_оценка"),
    ("MeanPositiveMark", "Средняя_ненулевая_оценка"),
    ("MarkSum", "Сумма_оценок"),
    ("MarkCount", "Количество_оценок"),
    ("MarkPositiveCount", "Количество_ненулевых_оценок"),
    ("10", "Количество_10"),
    ("9", "Количество_9"),
    ("8", "Количество_8"),
    ("7", "Количество_7"),
    ("6", "Количество_6"),
    ("5", "Количество_5"),
    ("4", "Количество_4"),
    ("3", "Количество_3"),
    ("2", "Количество_2"),
    ("1", "Количество_1"),
    ("0", "Количество_0"),
)
root_field_to_text = dict(root_fields)
root_text_to_field = {b: a for a, b in root_fields}
root_fields_database = list(root_field_to_text.keys())
root_fields_text = list(root_text_to_field.keys())



students_fields = (
    ("Name", "Имя"),
    ("Group", "Группа"),
    ("Program", "ОП"),
    ("Year", "Курс"),
    ("MeanMark", "Средняя_оценка"),
    ("MeanPositiveMark", "Средняя_ненулевая_оценка"),
    ("MarkSum", "Сумма_оценок"),
    ("MarkCount", "Количество_оценок"),
    ("MarkPositiveCount", "Количество_ненулевых_оценок"),
    ("10", "Количество_10"),
    ("9", "Количество_9"),
    ("8", "Количество_8"),
    ("7", "Количество_7"),
    ("6", "Количество_6"),
    ("5", "Количество_5"),
    ("4", "Количество_4"),
    ("3", "Количество_3"),
    ("2", "Количество_2"),
    ("1", "Количество_1"),
    ("0", "Количество_0"),
)
students_field_to_text = dict(students_fields)
students_text_to_field = {b: a for a, b in students_fields}
students_fields_database = list(students_field_to_text.keys())
students_fields_text = list(students_text_to_field.keys())

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
