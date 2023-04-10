### Структура папки
* [data.json](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/data.json) - служебный файл, хранит информацию об обработанных root-таблицах
* Папки формата **YYYY-MM-DD_hh:mm:ss** - папки с обработанными root-таблицами, их ведомостями и списками студентов. Пример папки - [2023-04-10_15:58:57](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/2023-04-10_15:58:57)
    * [root.csv](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/2023-04-10_15:58:57/root.csv) - обработанная root-таблица в формате csv
    * [students.csv](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/2023-04-10_15:58:57/students.csv) - обработанные списки студентов в формате одного csv файла
    * [students_src](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/2023-04-10_15:58:57/students_src) - сюда кладем эксельки со списками студентов (экселек может быть несколько)
    * [statements](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/2023-04-10_15:58:57/statements) - папка с обработанными ведомостями в формате csv
        * [Пример распарсенной ведомости](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/2023-04-10_15:58:57/statements/БПИ_1курс_2,3модуль_Компьютерный_практикум_по_матанализу_на_Python_Шайхелисламов.csv). Все ведомости парсятся в таком формате:
            * Student - имя студента
            * Group - группа студента
            * MarksDict - (str) словарь ненормированных (в исходном виде) оценок - "{за что оценка} ({колонка})": {оценка}. Например: 'ЛР 2 оценка (K)': 8.0
            * MarksNorm - (str) массив нормированных оценок
            * Excellent - число "отлов"
            * Good - число "хоров"
            * Satisfactory - число "удов"
            * Fail - число "неудов"