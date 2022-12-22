import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

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

# вспомогательная функция, убирающая лишние символы (табуляции, выравнивания, переноса строки и т.д.) из строки
def remove_special_symbols(s):
    return re.sub('[\n\t\r\v\f]', ' ', s)    
    
if __name__ == "__main__":
    
    gc = pygsheets.authorize(service_file='client/client.json')

    with open("config/config.json", "r") as f:
        config = json.load(f)

    url_root_sheet = sys.argv[1] # ссылка на root-таблицу, передаем через аргумент командной строки
    URL_COLUMN_NAME = config["URL_COLUMN"] # название колонки ссылок на ведомости
    START_ROW = config["START_ROW"] # строка, с которой начинается вписывание данных в root-таблицу
    URL_COL_IND = ord(URL_COLUMN_NAME.upper()) + 1 - ord('A') # номер колонки ссылок на ведомости

    root_sheet = gc.open_by_url(url_root_sheet)
    root_ws = root_sheet[0] # пока парсим только первый лист root-таблицы

    values = root_ws.get_values(start="A1", end=(root_ws.rows, URL_COL_IND), include_tailing_empty_rows=False)

    # проверяем, не парсили ли мы уже root-таблицу по данной ссылке
    with open("data/data.json", "r") as f:
        existing_data = json.load(f)

    if url_root_sheet in existing_data:
        print("Корневая ведомость уже обработана")
        df_root = pd.read_csv(existing_data[url_root_sheet] + "/root.csv", sep=";")
    else:
        print("Корневая ведомость еще не обработана. Начинается обработка")
        path = "data/" + "_".join(str(datetime.now()).split(".")[0].split(" "))
        os.mkdir(path)
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

            data = {"Level": level, "Program": program, "Year": year, "Module": module, 
                    "Discipline": discipline, "Teacher": teacher, "Row": i + 1, "Text": text}
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
                        break
                df_root = df_root.append(data, ignore_index=True)        

            # Если валидных ссылок не было
            if not url_found:
                data["ID"], data["URL"], data["Type"], data["IsParsed"], data["ErrorName"] = len(df_root) + 1, np.nan, np.nan, False, "URL invalid"
                df_root = df_root.append(data, ignore_index=True)

        df_root.to_csv(path + "/root.csv", sep=";", header=config["ROOT_TABLE_ATTRS"], index=False)
        print("Обработка завершена. Данные лежат в", path + "/root.csv")        