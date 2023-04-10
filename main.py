import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from collections import defaultdict
from datetime import datetime
from http.client import responses
import json
import numpy as np
import os
import pandas as pd
import pygsheets
import re
import requests
import sys
from tqdm import tqdm

def remove_special_symbols(s):
    return re.sub('[\n\t\r\v\f]', ' ', s)    

def number_by_col(letters):
    result, cnst = 0, ord('A') - 1
    letters = letters[::-1]
    for i in range(len(letters)):
        result += pow(26, i) * (ord(letters[i]) - cnst)
    return result
    
def col_by_number(number):
    result, cnst = "", ord('A')
    while number > 0:
        number -= 1
        result = chr(number % 26 + cnst) + result
        number //= 26
    return result
    
def from_to_cell(cell1, cell2):
    cell1_col, cell2_col = re.sub(r"([0-9])", '', cell1), re.sub(r"([0-9])", '', cell2)
    cell_row = re.sub(r"([A-Z])", '', cell1)
    return [col_by_number(x) + cell_row for x in range(number_by_col(cell1_col), number_by_col(cell2_col) + 1)]
    
def cells_from_formula(formula):
    if formula == '':
        return None
    # Убираем ссылки на другие страницы
    formula = re.sub(r"('.+'!\$*[A-Z]+\$*[0-9]*:*\$*[A-Z]*\$*[0-9]*)", '', formula)
    cells = re.findall(r"(\$*[A-Z]+\$*[0-9]+:*)", formula)
    cells = [re.sub('\$', '', x) for x in cells]
    result, i = [], 0
    while i < len(cells):
        if cells[i][-1] == ':':
            l = from_to_cell(cells[i][:-1], cells[i + 1])
            result.extend(l)
            i += 2
        else:
            result.append(cells[i])
            i += 1
    return result
    
def is_name(s):
    r1 = re.match(r"^(\s*[a-zA-Zа-яА-Я]+.*\s+[a-zA-Zа-яА-Я]+.*\s+[a-zA-Zа-яА-Я]+.*\s+[a-zA-Zа-яА-Я]+.*\s*)", s)
    r2 = re.match(r"^(\s*[a-zA-Zа-яА-Я]+.*\s+[a-zA-Zа-яА-Я]+.*\s+[a-zA-Zа-яА-Я]+.*\s*)", s)
    r3 = re.match(r"^(\s*[a-zA-Zа-яА-Я]+.*\s+[a-zA-Zа-яА-Я]+.*\s*)", s)
    r4 = re.search(r"([0-9])", s)
    return ((r1 is not None) or (r2 is not None) or (r3 is not None)) and (r4 is None)

def program_prefix(program):
    prefix = ""
    program_lst = program.split()
    for i in range(len(program_lst)):
        if len(program_lst[i]) > 3: # пропускаем предлоги, союзы и т.д.
            prefix += program_lst[i][0].upper()
    return prefix

def is_group_number(s, group_prefs):
    for prefix in group_prefs:
        if re.search(r"{}".format(prefix), s) is not None:
            return True
    return False

def is_mark(s):
    s = re.sub(r",", '.', s)
    try:
        float(s)        
        return True
    except:
        return False

def is_formula(value, title, titles):
    if type(value) != str:
        return False
    if value != '' and value[0] == '=':
        value = re.sub(r"(ВПР|VLOOKUP)\([A-Z]+[0-9]+;", '', value)
        regex = re.compile("('{}'!)".format(re.escape(title)))
        value = re.sub(regex, '', value)
        for t in titles:
            if t != title:
                value = re.sub(r"({0}|'{0}')".format(t), '', value)
        value = re.sub(r"(!\$*[A-Z]+\$*[0-9]*:*\$*[A-Z]*\$*[0-9]*)", '', value)
        cells_to_check = cells_from_formula(value)
        if len(cells_to_check) == 0:
            return False
        return True
    return False

def mark_name(mark):
    if mark < 3.5:
        return "Fail"
    if mark < 5.5:
        return "Satisfactory"
    if mark < 7.5:
        return "Good"
    return "Excellent"

# Нормируем только если нестандартные оценки (макс = 1 или > 10)
def norm_marks(marks):
    mx = max(marks)
    if mx < 5 or mx > 10 or (5 - mx < 0.0000001):
        if mx < 0.000001:
            return [0] * len(marks)
        return [10 * mark / mx for mark in marks]
    return marks

def cnt_positive_values(lst):
    cnt = 0
    for value in lst:
        cnt += int(value > 0)
    return cnt
    
if __name__ == "__main__":

    gc = pygsheets.authorize(service_file='client/client.json')

    with open("config/config.json", "r") as f:
        config = json.load(f)
    
    url_root_sheet = "https://docs.google.com/spreadsheets/d/1IyfSPiiR0DUxYuConiYzuokM2hUQbOBpuJAeAlGi7kc/edit#gid=223389382"
    url_root_sheet = re.sub(r"/edit(.*)", '', url_root_sheet)

    URL_COLUMN_NAME = config["URL_COLUMN"] # колонка ссылок на ведомости
    START_ROW = config["START_ROW"] # строка, с которой начинается вписывание данных
    URL_COL_IND = ord(URL_COLUMN_NAME.upper()) + 1 - ord('A') # номер колонки ссылок на ведомости

    root_sheet = gc.open_by_url(url_root_sheet)

    root_ws = root_sheet[0] # TODO

    values = root_ws.get_values(start="A1", end=(root_ws.rows, URL_COL_IND), include_tailing_empty_rows=False)

    upd_flg = config["UPDATE"]

    with open("data/data.json", "r") as f:
        existing_data = json.load(f)

    if (url_root_sheet in existing_data) and not upd_flg:
        print("Таблица с ведомостями уже обработана")
        path = existing_data[url_root_sheet]
        df_root = pd.read_csv(path + "/root.csv", sep=";")
    else:
        print("Начинается обработка...")
        path = "data/" + "_".join(str(datetime.now()).split(".")[0].split(" "))
        os.mkdir(path)
        os.mkdir(path + "/statements")
        os.mkdir(path + "/students_src")
        with open("data/data.json", "w") as f:
            existing_data[url_root_sheet] = path
            json.dump(existing_data, f)
        df_root = pd.DataFrame(columns=config["ROOT_TABLE_ATTRS"])

        # Заполняем root-таблицу
        for i in tqdm(range(START_ROW - 1, len(values))):
            col = config["ATTR_COLUMNS"]

            level = remove_special_symbols(values[i][col["LEVEL"]])
            program = remove_special_symbols(values[i][col["PROGRAM"]])
            year = int(values[i][col["YEAR"]])
            module = remove_special_symbols(values[i][col["MODULE"]])
            discipline = remove_special_symbols(values[i][col["DISCIPLINE"]])
            teacher = remove_special_symbols(values[i][col["TEACHER"]])
            text = remove_special_symbols(values[i][col["URL"]])

            data = {"Level": level, "Program": program, "Year": year, "Module": module, "Discipline": discipline, "Teacher": teacher, "Row": i + 1, "Text": text}
            url_found = False
            unparsed_urls = text.split()

            # Парсим адреса ссылок
            for word in unparsed_urls:
                try:
                    response = requests.get(word)
                    url_found = True

                    if response.status_code != 200:
                        data["ErrorName"] = responses[response.status_code]
                    else:
                        data["ErrorName"] = np.nan
                except:
                    continue  

                # Если это валидная ссылка 
                data["ID"], data["URL"], data["Type"] = len(df_root) + 1, word, np.nan
                data["IsParsed"] = np.nan if pd.isna(data["ErrorName"]) else False
                for url_prefix, url_type in config["URL_TYPE"].items():
                    if url_prefix in word:
                        data["Type"] = url_type
                        if data["Type"] == "Google Sheet":
                            data["URL"] =  re.sub(r"/edit(.*)", '', data["URL"])
                        break
                df_root = df_root.append(data, ignore_index=True)        

            # Если валидных ссылок не было
            if not url_found:
                data["ID"], data["URL"], data["Type"], data["IsParsed"], data["ErrorName"] = len(df_root) + 1, np.nan, np.nan, False, "URL invalid"
                df_root = df_root.append(data, ignore_index=True)
   
        df_root.to_csv(path + "/root.csv", sep=";", header=config["ROOT_TABLE_ATTRS"], index=False)
        print("Обработка завершена. Данные лежат в", path + "/root.csv")
  
    # Excel-таблицы со студентами кладем в students_src
    if os.path.isfile(path + "/students.csv"):
        df_students = pd.read_csv(path + "/students.csv", sep=";")
    else:
        print("Парсим списки студентов...")
        students_df_original = pd.DataFrame()
        for file in os.listdir(path + "/students_src/"):
            students_df_original_ = pd.read_excel(path + "/students_src/" + file)
            students_df_original = students_df_original.append(students_df_original_, ignore_index=True)

        df_students = pd.DataFrame(columns=config["STUDENT_TABLE_ATTRS"])
        for i in tqdm(range(len(students_df_original))):
            data = students_df_original.iloc[i]
            if re.match(r"^(М[0-9]{3,4}[А-Я]{2,}[0-9][0-9][0-9]$)", data[0]) is not None:
                id_card, first_name, second_name, third_name  = data[0], data[1], data[2], data[3]
                year, group, program, email = int(data[4][0]), data[5], data[6], data[7]
                if pd.isna(group):
                    continue
                name = first_name + " " + second_name + " " + third_name
                row = {"ID": i, "Name": name, "Year": year, "Group": group, "Program":program, "Email": email, "IDCard":id_card, "MarkSum":0, "MarkCount":0, "Mean":0, "Excellent":0, "Good":0, "Satisfactory":0, "Fail":0,}
                df_students = df_students.append(row, ignore_index=True)
        df_students.to_csv(path + "/students.csv", sep=";", header=config["STUDENT_TABLE_ATTRS"], index=False)
        print("Списки студентов обработаны")
                     
    group_names = set()
    for group in df_students.Group.unique():
        group_names.add(group)

    # Начинаем парсить валидные ссылки
    valid_links = df_root[pd.isna(df_root.ErrorName) & (df_root.Type == "Google Sheet")]
    for sh_ind in range(len(valid_links)):
        sh = df_root[pd.isna(df_root.ErrorName) & (df_root.Type == "Google Sheet")].iloc[sh_ind]
        id_sheet, url_sheet = sh.ID, sh.URL
        if len(df_root[(df_root.URL == url_sheet) & (df_root.IsParsed == True)]) > 0:
            tmp = df_root[(df_root.URL == url_sheet) & (df_root.IsParsed == True)]
            row, ind = tmp.iloc[0], [tmp.index[0]]
            new_row = df_root.loc[ind]
            new_row.IsParsed = row.IsParsed
            new_row.ErrorName = row.ErrorName
            new_row.Path = row.Path
            new_row.MeanMark = row.MeanMark
            new_row.MeanPositiveMark = row.MeanPositiveMark
            new_row.MeanMeanMark = row.MeanMeanMark
            new_row.Excellent = row.Excellent
            new_row.Good = row.Good
            new_row.Satisfactory = row.Satisfactory
            new_row.Fail = row.Fail
            df_root.loc[ind] = new_row
            df_root.to_csv(path + "/root.csv", sep=";", header=config["ROOT_TABLE_ATTRS"], index=False)		
            print("Ведомость уже обработана и выгружена сюда ", row.Path)
            continue
        try:
            sheet = gc.open_by_url(url_sheet)
        except Exception as e:
            err = str(e)
            if re.search(r"This operation is not supported for this document", err) is not None:
                err = "Wrong format"	    
            ind = df_root[df_root.ID == id_sheet].index
            row = df_root.loc[ind]
            row.IsParsed = False
            row.ErrorName = err
            df_root.loc[ind] = row
            df_root.to_csv(path + "/root.csv", sep=";", header=config["ROOT_TABLE_ATTRS"], index=False)
            continue

        print("\n\nПарсим {}".format(sheet.title))
        df_marks = pd.DataFrame(columns=config["MARK_TABLE_ATTRS"])
        ws_to_parse = []
        for ws in sheet:
            title_original = ws.title
            title = ws.title.upper()
            if re.search(r"(ГР|ГРУП|ГРУПП|ГРУППА|GROUP|GR)", title) is not None:
                ws_to_parse.append(title_original)
            else:
                title = re.sub(r"([^A-ZА-Я0-9])", '', title)
            for group in group_names:
                if title in group:
                    ws_to_parse.append(title_original)
                    break
        ws_to_parse = ws_to_parse if len(ws_to_parse) > 0 else [w.title for w in sheet]

        # Парсим страницы внутри одного Google Sheet
        ind_stopped = 0
        l, p, y, m, d, t = sh.Level[0], program_prefix(sh.Program), str(sh.Year), sh.Module, sh.Discipline, sh.Teacher.split(' ')[0]
        ws_path = path + '/statements/' + l + p + '_' + y + "курс" + '_' + m + 'модуль_' + "_".join(d.split(' ')) + '_' + t + ".csv"

        for title in ws_to_parse:
            try:
                work_sheet = sheet.worksheet_by_title(title)
                print("\nПарсим страницу {}".format(title))

                cells_array = work_sheet.get_values(start="A1", end=(work_sheet.rows, work_sheet.cols), include_tailing_empty_rows=False, value_render=pygsheets.custom_types.ValueRenderOption.FORMULA)
                rows, cols = len(cells_array), len(cells_array[0])

                # TODO различать индексные колонки и колонки, где прописаны варианты
                # В предположении, что слева от текстовых столбцов стоят индексы и др. незначимые числа
                start_ind, cnt_all, cnt_numbers = 1, 0, 0
                while True:
                    v = work_sheet.get_col(start_ind)
                    for j in range(rows):
                        try:
                            int(v[j])
                            cnt_numbers += 1
                        except:
                            pass
                        cnt_all += 1  
                    if (cnt_numbers / cnt_all) < 0.4:
                        break
                    start_ind += 1
                    if start_ind >= cols:
                        raise Exception("Text columns are not found")
                    cnt_all, cnt_numbers = 0, 0

                # Разметка колонок
                df_root_row = df_root[df_root.ID == id_sheet]
                level, program = df_root_row.Level.iloc[0], df_root_row.Program.iloc[0]
                name_cols, group_cols, mark_cols = [], [], []
                group_prefs = set()
                for group in df_students.Group.unique():
                    group_prefs.add(group)

                title = work_sheet.title
                titles = [ws.title for ws in sheet]

                for j in range(start_ind, cols + 1):
                    v = work_sheet.get_col(j)
                    name_cnt, group_cnt, mark_cnt, cnt = 0, 0, 0, 0
                    neg_flg = False
                    for i in range(rows):
                        name_cnt += is_name(v[i])
                        group_cnt += is_group_number(v[i], group_names)
                        mark_cnt += is_mark(v[i]) and not is_formula(cells_array[i][j - 1], title, titles)
                        neg_flg = True if not neg_flg and is_mark(v[i]) and float(re.sub(r",", '.', v[i])) < 0 else neg_flg
                        cnt += 1
                    name_flg = name_cnt / cnt > config["NAME_COLUMN_THRESHOLD"]
                    group_flg = group_cnt / cnt > config["GROUP_COLUMN_THRESHOLD"]
                    mark_flg = mark_cnt / cnt > config["MARK_COLUMN_THRESHOLD"]
                    if name_flg:
                        name_cols.append(j)
                    if group_flg:
                        group_cols.append(j)
                    if mark_flg:
                        mark_cols.append(j)
                    if (name_flg and group_flg) or (name_flg and mark_flg) or (group_flg and mark_flg):
                        if (name_flg and group_flg):
                            raise Exception("Single column is parsed to be name and group column")	
                        elif (name_flg and mark_flg):   
                            raise Exception("Single column is parsed to be name and mark column")
                        else:
                            raise Exception("Single column is parsed to be group and mark column")

                if len(name_cols) == 0 or (len(mark_cols) < config["MARK_COUNT_THRESHOLD"]):
                    print("Парсить нечего")	
                    continue

                # Ищем шапку оценок
                col = work_sheet.get_col(name_cols[0])
                for mark_name_row in range(len(col)):
                    if is_name(col[mark_name_row]):
                        break
                mark_name_row -= 1

                mark_names = []
                for i in mark_cols:
                    mark_names.append((str(cells_array[mark_name_row][i - 1]) + " (" + col_by_number(i) + ")"))

                ambiguous_students = []
                not_found_students = []
                values = work_sheet.get_values(start="A1", end=(work_sheet.rows, work_sheet.cols), include_tailing_empty_rows=False)
                marks_norm = np.array([0] * len(mark_cols))
                students_inds = []

                for i in range(rows):
                    student_name = cells_array[i][name_cols[0] - 1]
                    if student_name == '':
                        continue
                    group_name = cells_array[i][group_cols[0] - 1] if len(group_cols) != 0 else np.nan

                    name_lst = re.sub('([^A-Za-zА-Яа-я])', ' ', student_name).split()
                    tmp = df_students[:]
                    for j in name_lst:
                        tmp = tmp[tmp.Name.str.contains(j)]
                        tmp.Name = tmp.Name.str.replace(j, "")
                    if len(tmp) == 0:
                        not_found_students.append(student_name)
                        continue
                    elif len(tmp) > 1 and pd.notna(group_name):
                        # Нашли несколько студентов - ищем по группе
                        if len(tmp[tmp.Group.str.contains(group_name)]) == 1:
                            tmp = tmp[tmp.Name.str.contains(group_name)]
                        else:
                            found_ind = []
                            for j in range(len(tmp)):
                                if tmp.iloc[j].Group in group_name:
                                    found_ind.append(tmp.iloc[j].ID)
                            if len(found_ind) == 0:
                                not_found_students.append((student_name, found_ind))
                                continue
                            elif len(found_ind) == 1:
                                tmp = tmp[tmp.ID == found_ind[0]]
                            else:
                                ambiguous_students.append((student_name, found_ind))
                    elif len(tmp) > 1:
                        ambiguous_students.append((student_name, tmp.ID.tolist()))
                        continue

                    # Если нашли студента
                    marks, sm, dct = [], 0, defaultdict(int)
                    for ind in mark_cols:
                        try:            
                            mark = float(re.sub(r",", '.', values[i][ind - 1]))
                        except:
                            mark = 0
                        marks.append(mark)
                    marks_dct = dict(zip(mark_names, marks))    

                    ind = df_students[df_students.ID == tmp.iloc[0].ID].index[0]
                    students_inds.append(ind)
                    marks_norm = np.vstack([marks_norm, marks])

                    data = {"ID": i, "Student": student_name, "Group": group_name, "MarksDict": marks_dct}
                    df_marks = df_marks.append(data, ignore_index=True)

                print("Не удалось найти ", len(not_found_students), " студентов (скорее всего отчислены)")
                print(len(ambiguous_students), " студентов именами похожи на других студентов")

                marks_norm = np.delete(marks_norm, (0), axis=0)
                # Нормируем
                for j in range(len(marks_norm[0])):
                    marks_norm[:, j] = norm_marks(marks_norm[:, j])

                for i in range(ind_stopped, len(df_marks)):
                    marks = marks_norm[i - ind_stopped, :]
                    dct = defaultdict(int)
                    for mark in marks:
                        dct[mark_name(mark)] += 1 

                    ind = [students_inds[i - ind_stopped]]
                    row = df_students.loc[ind]
                    row.MarkSum += sum(marks)
                    row.MarkCount += len(marks)
                    row.Mean = row.MarkSum / row.MarkCount if row.MarkCount.iloc[0] > 0 else 0.0
                    row.Excellent += dct["Excellent"]
                    row.Good += dct["Good"]
                    row.Satisfactory += dct["Satisfactory"]
                    row.Fail += dct["Fail"]
                    df_students.loc[ind] = row

                    row = df_marks.loc[i]
                    row.MarksNorm = marks.tolist()
                    row.Excellent = dct["Excellent"]
                    row.Good = dct["Good"]
                    row.Satisfactory = dct["Satisfactory"]
                    row.Fail = dct["Fail"]
                    row.Mean = sum(marks) / len(marks) if len(marks) > 0 else 0.0
                    df_marks.loc[i] = row

                ind_stopped = len(df_marks)

            except Exception as e:
                print(str(e))
                continue
        
        # Сохраняем csv ведомости
#         tmp = df_root[df_root.ID == id_sheet].iloc[0]
        ind_to_check = df_root[df_root.ID == id_sheet].index[0] - 1
        row_to_check = df_root.loc[ind_to_check]
        flg_lvl = (row_to_check.Level == sh.Level)
        flg_pr = row_to_check.Program == sh.Program
        flg_yr = row_to_check.Year == sh.Year
        flg_md = row_to_check.Module == sh.Module
        flg_dcpl = row_to_check.Discipline == sh.Discipline
        flg_tchr = row_to_check.Teacher == sh.Teacher
        if flg_lvl and flg_pr and flg_yr and flg_md and flg_dcpl and flg_tchr:
            suff = 1
            while os.path.isfile(ws_path):
                ws_path = re.sub(r"(_*[0-9]*\.csv)$", "_{}.csv".format(suff), ws_path)
                suff += 1
        df_marks.to_csv(ws_path, sep=";", header=config["MARK_TABLE_ATTRS"], index=False)

        # Обновляем root-таблицу
        ind = [df_root[df_root.ID == id_sheet].index[0]]
        row = df_root.loc[ind]
        row.IsParsed = True
        row.Path = ws_path
        sm = sum([sum(x) for x in df_marks.MarksNorm])
        cnt = sum([len(x) for x in df_marks.MarksNorm])
        row.MeanMark = sm / cnt if cnt > 0 else 0.0
        row.MeanMeanMark = df_marks.Mean.mean()
        sm_pos = sum([cnt_positive_values(row) for row in df_marks.MarksNorm])
        row.MeanPositiveMark = sm / sm_pos if sm_pos > 0 else 0.0
        row.Excellent = df_marks.Excellent.sum()
        row.Good = df_marks.Good.sum()
        row.Satisfactory = df_marks.Satisfactory.sum()
        row.Fail = df_marks.Fail.sum()
        df_root.loc[ind] = row
        df_root.to_csv(path + "/root.csv", sep=";", header=config["ROOT_TABLE_ATTRS"], index=False)

    print("Парсинг завершен успешно")