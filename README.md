# StatementAnalysisAutomationHSE

**Порядок действий для взаимодействия с программой:**
1. `pip install -r requirements.txt`
2. Настройте сервисный Google аккаунт, который будет дергать Google API: [инструкция](https://pygsheets.readthedocs.io/en/staging/authorization.html). В параграфе Service Account вы скачаете json с данными сервисного аккаунта. Переименуйте его в `client.json` и положите в папку [client](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/client) (или скопируйте его содержимое в уже существующий пустой файл [client/client.json](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/client/client.json))
3. `python3 main.py https://docs.google.com/spreadsheets/d/1IyfSPiiR0DUxYuConiYzuokM2hUQbOBpuJAeAlGi7kc/edit#gid=223389382` (в аргументе можно передать ссылку на другую root-таблицу). Моя версия python: 3.8.10

**Какие данные можно использовать для тестирования фронтенда?**  
Все, что есть в [data/2023-04-10_15:58:57](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/2023-04-10_15:58:57). В [Tutorial.ipynb](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/Tutorial.ipynb) описала, как можно анализировать эти данные
 
### Текущая структура проекта

* [requirements.txt](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/requirements.txt) - список используемых библиотек: `pip install -r requirements.txt`
* [main.py](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/main.py) - код, парсящий root-таблицу и записывающий распарсенное в .csv и .json файлы в папку [data](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data). Запускать так: `python3 main.py url`, где `url` - это ссылка на root-таблицу. Например: `https://docs.google.com/spreadsheets/d/1IyfSPiiR0DUxYuConiYzuokM2hUQbOBpuJAeAlGi7kc/edit#gid=223389382`
* [data](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data)
   * [data.json](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/data.json) - перечисление распарсенных root-таблиц в формате {ссылка}: {путь}. Подробнее - в [data/README.md](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/README.md)
* [Analysis.ipynb](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/Analysis.ipynb) - ноутбук с аналитикой
* [config](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/config) - папка с конфигами. Подробнее - в [config/README.md](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/config/README.md)
* [client](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/client) - папка со всякими ключами, токенами и т.д. для взаимодействия с API
