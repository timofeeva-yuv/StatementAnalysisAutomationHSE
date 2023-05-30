### Структура папки
* [data.json](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/data.json) - служебный файл, хранит информацию об обработанных root-таблицах
* Папки формата **YYYY-MM-DD_hh:mm:ss** - папки с обработанными root-таблицами, их ведомостями и списками студентов. Пример папки - [2023-05-21_18:39:29](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/2023-05-21_18:39:29)
    * [root.csv](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/2023-05-21_18:39:29/root.csv) - обработанная root-таблица в формате csv
    * [students.csv](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/2023-05-21_18:39:29/students.csv) - обработанные списки студентов в формате одного csv файла
    * [students_src](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/2023-05-21_18:39:29/students_src) - папка с Excel-файлами списков студентов (перемещается из tmp)
    * [statements](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/2023-05-21_18:39:29/statements) - папка с обработанными ведомостями в формате csv
        * [Пример распарсенной ведомости](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/2023-05-21_18:39:29/statements/БПИ_1курс_1,2,3,4модуль_Дискретная_математика_Дашков.csv). Все ведомости парсятся в таком формате:
            * Student - имя студента
            * Group - группа студента
            * MarksDict - (str) словарь ненормированных (в исходном виде) оценок - "{за что оценка} ({колонка})": {оценка}. Например: 'ЛР 2 оценка (K)': 8.0
            * MarksNorm - (str) массив нормированных оценок
            * MeanMark - (float) средняя оценка студента по MarksNorm
            * MeanPositiveMark - (float) средняя неотрицательная оценка студента по MarksNorm
            * MarkSum - (float) сумма оценок в MarksNorm (техническая информация, необязательная для пользователя)
            * MarkCount - (float) число оценок в MarksNorm (техническая информация, необязательная для пользователя)
            * MarkPositiveCount - (float) число неотрицательных оценок в MarksNorm (техническая информация, необязательная для пользователя)
            * "10" - число "десяток" (оценок 10)
            * "9" - число "девяток"
            * "8" - число "восьмёрок"
            * "7" - число "семёрок"
            * "6" - число "шестёрок"
            * "5" - число "пятёрок"
            * "4" - число "четвёрок"
            * "3" - число "троек"
            * "2" - число "двоек"
            * "1" - число "единиц"
            * "0" - число "нулей"
            
