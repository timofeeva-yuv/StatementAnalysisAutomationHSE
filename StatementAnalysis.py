import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from collections import Counter
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
from sqlite3 import connect
import sys
from tqdm import tqdm


class StatementAnalysis(object):
    '''Анализатор ведомостей факультета компьютерных наук НИУ ВШЭ'''
    
    def __init__(self, url, upd=False, student_files=[]):
        '''Принимает по порядку:
                url (str) - ссылка на google-таблицу с ведомостями
                upd (bool) - True, если нужно обновить обработку ранее обработанных ведомостей. По умолчанию - False
                student_files (list) - список названий excel-файлов со списками студентов. По умолчанию - пустой список
        '''
        with open("config/config.json", "r") as f:
            self.config = json.load(f)
            
        self.path = ""
        self.student_files = student_files[:]
        self.root_db_attrs = self.__make_db_attrs("ROOT_TABLE_ATTRS")
        self.students_db_attrs = self.__make_db_attrs("STUDENT_TABLE_ATTRS")
        self.marks_db_attrs = self.__make_db_attrs("MARK_TABLE_ATTRS")
        
        self.df_root = self.__parse_root(url, upd)
        self.df_students = self.__parse_students_lists()
        self.group_names = self.__get_group_names()
        
        self.__create_db()

        if upd:
            self.__parse_statements()

    def __call__(self, url, upd=False, student_files=[]):
        '''Принимает по порядку:
                url (str) - ссылка на google-таблицу с ведомостями
                upd (bool) - True, если нужно обновить обработку ранее обработанных ведомостей. По умолчанию - False
                student_files (list) - список названий excel-файлов со списками студентов. По умолчанию - пустой список
        '''
        self.student_files = student_files[:]
        
        self.root_df = self.__parse_root(url, upd)
        self.df_students = self.__parse_students_lists()      
        
        self.__create_db()
        
        self.__parse_statements()
    
    def get(self, cmd):
        ''' Принимает cmd (str) - название запроса. Например, "Неуспевающие" или "Завышение".
            Возвращает результат запроса, который вернула база данных
        '''
        result = []
        db = self.conn.cursor()
        if cmd == "Неуспевающие":
            res = db.execute('SELECT ID, Name, CAST(SUM("0" + "1" + "2" + "3") AS real) / CAST(MarkCount AS real) AS "Доля неудов" FROM students GROUP BY ID, Name ORDER BY "Доля неудов" DESC')
            result = res.fetchall()
            result = result[:int(self.config["FAIL_STUDENTS_TOP"] * len(result))] # 5% по доле неудов
        elif cmd == "Завышение":
            res = db.execute('SELECT * FROM root WHERE (("10" + "9" + "8") / MarkCount >= {}) AND ("10" / MarkCount >= {})'.format(self.config["OVERESTIMATION_GREAT_PERCENT"], self.config["OVERESTIMATION_10_PERCENT"]))
            result = res.fetchall()
        db.close()
        return result
    
    def __del__(self):
        try:
            self.conn.close()
        except:
            pass
        
    def __parse_statements(self):
        '''Запускает обработку разных видов ведомостей'''
        self.__parse_gsheets()    
    
    def __create_db(self):    
        '''Создает внутреннюю базу данных с таблицами root и students'''
        self.conn = connect('{}/database'.format(self.path), check_same_thread=False)
        db = self.conn.cursor()
        
        db.execute('CREATE TABLE IF NOT EXISTS {} {}'.format("root", self.root_db_attrs))
        self.conn.commit()
        self.df_root.to_sql('root', self.conn, if_exists='replace', index = False)
        
        db.execute('CREATE TABLE IF NOT EXISTS {} {}'.format("students", self.students_db_attrs))
        self.conn.commit()
        self.df_students.to_sql('students', self.conn, if_exists='replace', index = False)
        
        db.close()
        
    def __parse_root(self, url_root_sheet, upd_flg):
        '''Обрабатывает google-таблицу со списком ведомостей.
           Принимает по порядку:
               url_root_sheet (str) - ссылка на google-таблицу с ведомостями
               upd_flg (bool) - True, если нужно обновить обработку ранее обработанных ведомостей. По умолчанию - False
           Возвращает pandas.DataFrame с обработанными данными таблицы
        '''
        gc = pygsheets.authorize(service_file="client/client.json")
        
        url_root_sheet = re.sub(r"/edit(.*)", '', url_root_sheet)

        URL_COLUMN_NAME = self.config["URL_COLUMN"] # колонка ссылок на ведомости
        START_ROW = self.config["START_ROW"] # строка, с которой начинается вписывание данных
        URL_COL_IND = ord(URL_COLUMN_NAME.upper()) + 1 - ord('A') # номер колонки ссылок на ведомости

        root_sheet = gc.open_by_url(url_root_sheet)

        root_ws = root_sheet[0] # TODO

        values = root_ws.get_values(start="A1", end=(root_ws.rows, URL_COL_IND), include_tailing_empty_rows=False)

        with open("data/data.json", "r") as f:
            existing_data = json.load(f)

        if (url_root_sheet in existing_data) and not upd_flg:
            print("{} Таблица с ведомостями уже обработана".format(datetime.now()))
            self.path = existing_data[url_root_sheet]
            df_root = pd.read_csv(self.path + "/root.csv", sep=";")
        else:
            print("{} Начинается обработка...".format(datetime.now()))
            self.path = "data/" + "_".join(str(datetime.now()).split(".")[0].split(" "))
            os.mkdir(self.path)
            os.mkdir(self.path + "/statements")
            os.mkdir(self.path + "/students_src")        
            with open("data/data.json", "w") as f:
                existing_data[url_root_sheet] = self.path
                json.dump(existing_data, f)
            df_root = pd.DataFrame(columns=self.config["ROOT_TABLE_ATTRS"])

            # Заполняем root-таблицу
            for i in tqdm(range(START_ROW - 1, len(values))):
                col = self.config["ATTR_COLUMNS"]

                level = self.remove_special_symbols(values[i][col["LEVEL"]])
                program = self.remove_special_symbols(values[i][col["PROGRAM"]])
                year = int(values[i][col["YEAR"]])
                module = self.remove_special_symbols(values[i][col["MODULE"]])
                discipline = self.remove_special_symbols(values[i][col["DISCIPLINE"]])
                teacher = self.remove_special_symbols(values[i][col["TEACHER"]])
                text = self.remove_special_symbols(values[i][col["URL"]])

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
                    for url_prefix, url_type in self.config["URL_TYPE"].items():
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

            df_root.to_csv(self.path + "/root.csv", sep=";", header=self.config["ROOT_TABLE_ATTRS"], index=False)
            print("{} Обработка завершена. Данные лежат в ".format(datetime.now()) + self.path + "/root.csv")
            
        return df_root[:]
    
    def __parse_students_lists(self):
        ''' Обрабатывает Excel-файлы со списками студентов, размещенные в специальной директории (см. STUDENT_LISTS_INITIAL_PATH в config.json). По умолчанию - в tmp
            Возвращает pandas.DataFrame с обработанными данными таблицы
        '''
        if os.path.isfile(self.path + "/students.csv"):
            df_students = pd.read_csv(self.path + "/students.csv", sep=";")
        else:
            old_path, new_path = self.config["STUDENT_LISTS_INITIAL_PATH"], self.path + "/students_src/"
            for file in self.student_files:    
                os.rename("{}/{}".format(old_path, file), "{}/{}".format(new_path, file))
            
            print("{} Парсим списки студентов...".format(datetime.now()))
            students_df_original = pd.DataFrame()
            for file in os.listdir(self.path + "/students_src/"):
                students_df_original_ = pd.read_excel(self.path + "/students_src/" + file)
                students_df_original = students_df_original.append(students_df_original_, ignore_index=True)

            df_students = pd.DataFrame(columns=self.config["STUDENT_TABLE_ATTRS"])
            for i in tqdm(range(len(students_df_original))):
                data = students_df_original.iloc[i]
                if re.match(r"^(М[0-9]{3,4}[А-Я]{2,}[0-9][0-9][0-9]$)", data[0]) is not None:
                    first_name, second_name, third_name  = data[1], data[2], data[3]
                    year, group, program = int(data[4][0]), data[5], data[6]
                    if pd.isna(group):
                        continue
                    name = first_name + " " + second_name + " " + third_name
                    row = {"ID": i, "Name": name, "Year": year, "Group": group, "Program":program, "MeanMark":0, "MeanPositiveMark":0, "MarkSum":0, "MarkCount":0, "MarkPositiveCount":0, "10":0, "9":0, "8":0, "7":0, "6":0, "5":0, "4":0, "3":0, "2":0, "1":0, "0":0}
                    df_students = df_students.append(row, ignore_index=True)
            df_students.to_csv(self.path + "/students.csv", sep=";", header=self.config["STUDENT_TABLE_ATTRS"], index=False)
            print("{} Списки студентов обработаны".format(datetime.now()))
            
        return df_students[:]
    
    def __parse_gsheets(self):
        '''Обрабатывает ведомости в формате Google-таблиц'''
        gc = pygsheets.authorize(service_file="client/client.json")
        
        # Начинаем парсить валидные ссылки
        gsh = self.df_root[self.df_root.Type == "Google Sheet"]
        inds = set(gsh[pd.isna(gsh.ErrorName)].index)
        inds |= set(gsh[gsh.ErrorName.str.len() > 12].index)
        gsh = gsh.loc[list(inds)]
        for sh_ind in gsh.index:
            sh = gsh.loc[sh_ind]
            id_sheet, url_sheet = sh.ID, sh.URL
            if len(self.df_root[(self.df_root.URL == url_sheet) & (self.df_root.IsParsed == True)]) > 0:
                tmp = self.df_root[(self.df_root.URL == url_sheet) & pd.notna(self.df_root.IsParsed)]
                row, ind = tmp.iloc[0], [tmp.index[0]]
                new_row = self.df_root.loc[ind]
                new_row.IsParsed = row.IsParsed
                new_row.ErrorName = row.ErrorName
                new_row.Path = row.Path
                new_row.MeanMark = row.MeanMark
                new_row.MeanPositiveMark = row.MeanPositiveMark
                new_row.MarkCount = row.MarkCount
                new_row.MarkSum = row.MarkSum
                new_row.MarkPositiveCount = row.MarkPositiveCount
                for j in range(11):
                    new_row[str(j)] = row[str(j)]
                self.df_root.loc[ind] = new_row
                self.df_root.to_csv(self.path + "/root.csv", sep=";", header=self.config["ROOT_TABLE_ATTRS"], index=False)
                if row.IsParsed:
                    print("{} Ведомость по {} уже обработана и выгружена сюда".format(datetime.now(), new_row.Discipline), row.Path)
                else:
                    print("{} Ведомость по {} уже пытались обработать, но завершились с ошибкой".format(datetime.now(), new_row.Discipline), row.ErrorName)
                continue
            try:
                sheet = gc.open_by_url(url_sheet)
            except Exception as e:
                err = str(e)
                if re.search(r"This operation is not supported for this document", err) is not None:
                    err = "Wrong format"    
                ind = self.df_root[self.df_root.ID == id_sheet].index
                row = self.df_root.loc[ind]
                row.IsParsed = False
                row.ErrorName = err
                self.df_root.loc[ind] = row
                self.df_root.to_csv(self.path + "/root.csv", sep=";", header=self.config["ROOT_TABLE_ATTRS"], index=False)
                continue

            print("\n\n{0} Парсим {1}".format(datetime.now(), sheet.title))

            df_marks = pd.DataFrame(columns=self.config["MARK_TABLE_ATTRS"])
            ws_to_parse, ws_by_url = [ws.title for ws in sheet], None
            l, p, y, m, d, t = sh.Level[0], self.program_prefix(sh.Program), str(sh.Year), sh.Module, sh.Discipline, sh.Teacher.split(' ')[0]
            ws_path = self.path + '/statements/' + l + p + '_' + y + "курс" + '_' + m + 'модуль_' + "_".join(d.split(' ')) + '_' + t + ".csv"

            # Парсим страницы внутри одного Google Sheet
            ind_stopped = 0

            for title in ws_to_parse:
                try:
                    work_sheet = sheet.worksheet_by_title(title)
                    print("\n{0} Парсим страницу {1}".format(datetime.now(), title))

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
                    df_root_row = self.df_root[self.df_root.ID == id_sheet]
                    level, program = df_root_row.Level.iloc[0], df_root_row.Program.iloc[0]
                    name_cols, group_cols, mark_cols = [], [], []
                    group_prefs = set()
                    for group in self.df_students.Group.unique():
                        group_prefs.add(group)

                    title = work_sheet.title
                    titles = [ws.title for ws in sheet]

                    for j in range(start_ind, cols + 1):
                        v = work_sheet.get_col(j)
                        name_cnt, group_cnt, mark_cnt, cnt = 0, 0, 0, 0
                        for i in range(rows):
                            name_cnt += self.__is_name(v[i])
                            group_cnt += self.__is_group_number(v[i], self.group_names)

                            formula_data = self.__is_formula(cells_array[i][j - 1], titles)
                            mark_cnt += self.__is_mark(v[i]) and not formula_data[0]
                            cnt += 1
                            
                        name_flg = name_cnt / cnt > self.config["NAME_COLUMN_THRESHOLD"]
                        group_flg = group_cnt / cnt > self.config["GROUP_COLUMN_THRESHOLD"]
                        mark_flg = mark_cnt / cnt > self.config["MARK_COLUMN_THRESHOLD"]
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

                    if len(name_cols) == 0 or (len(mark_cols) < self.config["MARK_COUNT_THRESHOLD"]):
                        if len(name_cols) == 0:
                            print("{} Парсить нечего (числящиеся студенты не найдены)".format(datetime.now()))
                        else:
                            print("{} Парсить нечего (мало оценок)".format(datetime.now()))
                        continue

                    # Ищем шапку оценок
                    col = work_sheet.get_col(name_cols[0])
                    for mark_name_row in range(len(col)):
                        if self.__is_name(col[mark_name_row]):
                            break
                    mark_name_row -= 1

                    mark_names = []
                    for i in mark_cols:
                        mark_names.append((str(cells_array[mark_name_row][i - 1]) + " (" + self.col_by_number(i) + ")"))

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
                        tmp = self.df_students[:]
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

                        ind = self.df_students[self.df_students.ID == tmp.iloc[0].ID].index[0]
                        students_inds.append(ind)
                        marks_norm = np.vstack([marks_norm, marks])

                        data = {"ID": i, "Student": student_name, "Group": group_name, "MarksDict": marks_dct}
                        df_marks = df_marks.append(data, ignore_index=True)

                    print("{} Не удалось найти".format(datetime.now()), len(not_found_students), " студентов (скорее всего отчислены)")
                    print(datetime.now(), len(ambiguous_students), "студентов именами похожи на других студентов")

                    marks_norm = np.delete(marks_norm, (0), axis=0)
                    # Нормируем
                    for j in range(len(marks_norm[0])):
                        marks_norm[:, j] = self.__norm_marks(marks_norm[:, j])

                    for i in range(ind_stopped, len(df_marks)):
                        marks = marks_norm[i - ind_stopped, :]
                        positive_cnt = self.cnt_positive_values(marks)

                        dct = Counter([round(mark) for mark in marks])
                        ind = [students_inds[i - ind_stopped]]
                        row = self.df_students.loc[ind]
                        row.MarkSum += sum(marks)
                        row.MarkCount += len(marks)
                        row.MarkPositiveCount += positive_cnt
                        row.MeanMark = row.MarkSum / row.MarkCount if row.MarkCount.iloc[0] > 0 else 0.0
                        row.MeanPositiveMark = row.MarkSum / row.MarkPositiveCount if row.MarkPositiveCount.iloc[0] > 0 else 0.0 
                        for j in range(11):
                            row[str(j)] += dct[j]                      
                        self.df_students.loc[ind] = row

                        row = df_marks.loc[i]
                        row.MarksNorm = marks.tolist()
                        row.MarkSum = sum(marks)
                        row.MarkCount = len(marks)
                        row.MarkPositiveCount = positive_cnt
                        row.MeanMark = row.MarkSum / len(marks) if len(marks) > 0 else 0.0
                        row.MeanPositiveMark = row.MarkSum / positive_cnt if positive_cnt > 0 else 0.0
                        for j in range(11):
                            row[str(j)] = dct[j]
                        df_marks.loc[i] = row

                    ind_stopped = len(df_marks)

                except Exception as e:
                    print(datetime.now(), str(e))
                    continue

            # Сохраняем csv ведомости
            ind_to_check = self.df_root[self.df_root.ID == id_sheet].index[0] - 1
            row_to_check = self.df_root.loc[ind_to_check]
            flg_lvl = (row_to_check.Level == sh.Level)
            flg_pr = row_to_check.Program == sh.Program
            flg_yr = row_to_check.Year == sh.Year
            flg_md = row_to_check.Module == sh.Module
            flg_dcpl = row_to_check.Discipline == sh.Discipline
            flg_tchr = row_to_check.Teacher == sh.Teacher
            if flg_lvl and flg_pr and flg_yr and flg_md and flg_dcpl and flg_tchr:
                ws_path = self.__make_new_path(ws_path)

            try:
                df_marks.to_csv(ws_path, sep=";", header=self.config["MARK_TABLE_ATTRS"], index=False)
            except:
                ws_path = self.path + "/statements/" + l + p + "_" + y + "курс" + "_" + m + "модуль_" + t + "_{}_row".format(sh.Row) + ".csv"
                if flg_lvl and flg_pr and flg_yr and flg_md and flg_dcpl and flg_tchr:
                    ws_path = self.__make_new_path(ws_path)
                df_marks.to_csv(ws_path, sep=";", header=self.config["MARK_TABLE_ATTRS"], index=False)

            # Обновляем root-таблицу и таблицу студентов
            ind = [self.df_root[self.df_root.ID == id_sheet].index[0]]
            row = self.df_root.loc[ind]
            row.IsParsed = True
            row.Path = ws_path
            sm = sum([sum(x) for x in df_marks.MarksNorm])
            cnt = sum([len(x) for x in df_marks.MarksNorm])
            row.MarkSum = sm
            row.MarkCount = cnt
            row.MeanMark = sm / cnt if cnt > 0 else 0.0
            cnt_pos = sum([self.cnt_positive_values(row) for row in df_marks.MarksNorm])
            row.MarkPositiveCount = cnt_pos
            row.MeanPositiveMark = sm / cnt_pos if cnt_pos > 0 else 0.0
            for j in range(11):
                row[str(j)] = df_marks[str(j)].sum()
            self.df_root.loc[ind] = row
            self.df_root.to_csv(self.path + "/root.csv", sep=";", header=self.config["ROOT_TABLE_ATTRS"], index=False)
            self.df_students.to_csv(self.path + "/students.csv", sep=";", header=self.config["STUDENT_TABLE_ATTRS"], index=False)
            
            # Заносим данные во внутреннюю базу
            self.df_root.to_sql('root', self.conn , if_exists='replace', index = False)
            self.df_students.to_sql('students', self.conn, if_exists='replace', index = False)
            self.conn.commit()

        print("{} Парсинг завершен успешно".format(datetime.now()))
        
    # В SQL-базе вместо поля Group будет GroupNumber (Group - служебное слово)
    def __make_db_attrs(self, table_name):
        '''Принимает table_name (str) - название ключа в config.json, описывающее поля определенной таблицы. Например, если нужно передать поля таблицы студентов, table_name="STUDENT_TABLE_ATTRS".
           Возвращает перечисление полей с их типами в специальном формате (для создания таблицы в БД через SQL-запрос)
        '''
        result = []
        for x in self.config[table_name]:
            if x in ("ID", "Year", "Row", "IsParsed"):
                result.append(x + " integer")
            elif x in ("10", "9", "8", "7", "6", "5", "4", "3", "2", "1", "0"):
                result.append("\"{}\" real".format(x))
            elif x in ("MarkCount", "MarkPositiveCount", "MeanMark", "MeanPositiveMark", "MarkSum"):
                result.append(x + " real")
            elif x == "Group":
                result.append(x + "Number text")
            else:
                result.append(x + " text")
        return "(" + ", ".join(result) + ")"    

    def __get_group_names(self):
        '''Возвращает множество названий групп (извлекается из списков студентов)'''
        group_names = set()
        for group in self.df_students.Group.unique():
            group_names.add(group)
        return group_names    
        
    def __is_name(self, s):
        '''Принимает s (str) - строка. Возвращает True или False в зависимости от того, "похожа" ли строка на имя'''
        r1 = re.match(r"^(\s*[a-zA-Zа-яА-Я]+.*\s+[a-zA-Zа-яА-Я]+.*\s+[a-zA-Zа-яА-Я]+.*\s+[a-zA-Zа-яА-Я]+.*\s*)", s)
        r2 = re.match(r"^(\s*[a-zA-Zа-яА-Я]+.*\s+[a-zA-Zа-яА-Я]+.*\s+[a-zA-Zа-яА-Я]+.*\s*)", s)
        r3 = re.match(r"^(\s*[a-zA-Zа-яА-Я]+.*\s+[a-zA-Zа-яА-Я]+.*\s*)", s)
        r4 = re.search(r"([0-9])", s)
        return ((r1 is not None) or (r2 is not None) or (r3 is not None)) and (r4 is None)

    def __is_group_number(self, s, group_prefs):
        '''Принимает:
               s (str) - строка
               group_prefs (list) - множество названий групп
               Возвращает True или False в зависимости от того, является ли строка названием группы
        '''
        for prefix in group_prefs:
            if re.search(r"{}".format(prefix), s) is not None:
                return True
        return False

    def __is_mark(self, s):
        '''Принимает s (str) - строка. Возвращает True или False в зависимости от того, является ли строка числом'''
        s = re.sub(r",", '.', s)
        try:
            float(s)        
            return True
        except:
            return False

    def __is_formula(self, value, titles):
        '''Применяется в обработке ведомостей в формате google-таблиц. 
           Принимает:
               value - значение ячейки (может быть числового формата или строкового)
               titles (list) - список названий страниц в таблице
           Возвращает пару (True/False, [...]):
           True - если значение ячейки вычисляется на основе других ячеек. 
           [...] - содержит названия страниц таблицы, которые упоминаются в значении ячейки
        '''
        if type(value) != str:
            return (False, [])
        if value != '' and value[0] == '=':
            regex = re.compile("(" + "|".join([t for t in titles]) + ")")
            found_titles = re.findall(regex, value)
            if len(found_titles) != 0:
                return (True, found_titles)
            if len(self.cells_from_formula(value)) == 0:
                return (False, [])
            return (True, [])
        return (False, [])

    # Нормируем только если нестандартные оценки (макс = 1 или > 10)
    def __norm_marks(self, marks):
        '''Принимает marks (list) - список оценок.
           Возвращает список оценок, приведенный к 10-балльной шкале
        '''
        mx = max(marks)
        if mx < 5 or mx > 10 or (5 - mx < 0.0000001):
            if mx < 0.000001:
                return [0] * len(marks)
            return [10 * mark / mx for mark in marks]
        return marks

    def __make_new_path(self, path):
        '''Принимает path (str) - путь. Возвращает путь с тем же названием следующего порядкового номера'''
        suff = 1
        while os.path.isfile(path):
            path = re.sub(r"(_*[0-9]*\.csv)$", "_{}.csv".format(suff), path)
            suff += 1
        return path

    @staticmethod
    def mark_name(mark):
        '''Принимает mark (float/int) - оценку. Возвращает название оценки по 5-балльной шкале'''
        if mark < 3.5:
            return "Fail"
        if mark < 5.5:
            return "Satisfactory"
        if mark < 7.5:
            return "Good"
        return "Excellent"

    @staticmethod
    def col_by_number(number):
        '''Принимает number (int) - номер колонки в google-таблице. Возвращает буквенное название колонки'''
        result, cnst = "", ord('A')
        while number > 0:
            number -= 1
            result = chr(number % 26 + cnst) + result
            number //= 26
        return result
    
    @staticmethod
    def number_by_col(letters):
        '''Принимает letters (str) - буквенное название колонки в google-таблице. Возвращает ее порядковый номер'''
        result, cnst = 0, ord('A') - 1
        letters = letters[::-1]
        for i in range(len(letters)):
            result += pow(26, i) * (ord(letters[i]) - cnst)
        return result

    @staticmethod
    def from_to_cell(cell1, cell2):
        '''Принимает диапазон ячеек:
               cell1 (str) - начиная с какой ячейки (адрес ячейки)
               cell2 (str) - заканчивая какой ячейкой (адрес ячейки)
           Возвращает список адресов ячеек в данном диапазоне
        '''
        cell1_col, cell2_col = re.sub(r"([0-9])", '', cell1), re.sub(r"([0-9])", '', cell2)
        cell_row = re.sub(r"([A-Z])", '', cell1)
        return [StatementAnalysis.col_by_number(x) + cell_row for x in range(StatementAnalysis.number_by_col(cell1_col), StatementAnalysis.number_by_col(cell2_col) + 1)]

    @staticmethod
    def cells_from_formula(formula):
        '''Принимает formula (str) - строку. Возвращает адреса ячеек, встречающихся в данной формуле'''
        if formula == '':
            return None
        # Убираем ссылки на другие страницы
        formula = re.sub(r"('.+'!\$*[A-Z]+\$*[0-9]*:*\$*[A-Z]*\$*[0-9]*)", '', formula)
        cells = re.findall(r"(\$*[A-Z]+\$*[0-9]+:*)", formula)
        cells = [re.sub('\$', '', x) for x in cells]
        result, i = [], 0
        while i < len(cells):
            if cells[i][-1] == ':':
                l = StatementAnalysis.from_to_cell(cells[i][:-1], cells[i + 1])
                result.extend(l)
                i += 2
            else:
                result.append(cells[i])
                i += 1
        return result
    
    @staticmethod
    def cnt_positive_values(lst):
        '''Принимает lst (list) - список чисел. Возвращает количество его положительных значений'''
        cnt = 0
        for value in lst:
            cnt += int(value > 0)
        return cnt
    
    @staticmethod
    def remove_special_symbols(s):
        '''Принимает s (str) - строку. Возвращает данную строку без пробельных символов'''
        return re.sub('[\n\t\r\v\f]', ' ', s)    
    
    @staticmethod
    def program_prefix(program):
        '''Принимает program (str) - название образовательной программы. Возвращает ее аббревиатуру'''
        prefix = ""
        program_lst = program.split()
        for i in range(len(program_lst)):
            if len(program_lst[i]) > 3: # пропускаем предлоги, союзы и т.д.
                prefix += program_lst[i][0].upper()
        return prefix    
    
if __name__ == "__main__":
    url = "https://docs.google.com/spreadsheets/d/1IyfSPiiR0DUxYuConiYzuokM2hUQbOBpuJAeAlGi7kc/edit#gid=223389382"
    upd = False # обработать ли ведомости заново?
    s = StatementAnalysis(url, upd, ["students_bachelor.xlsx", "students_master.xlsx"])
    print(s.get("Завышение"))
    print("\n")
    print(s.get("Неуспевающие"))