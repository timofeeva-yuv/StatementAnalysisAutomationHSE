# StatementAnalysisAutomationHSE

**Порядок действий для взаимодействия с программой:**
1. `pip install -r requirements.txt`
2. Настройте сервисный Google аккаунт, который будет дергать Google API: [инструкция](https://pygsheets.readthedocs.io/en/staging/authorization.html). В параграфе Service Account вы скачаете json с данными сервисного аккаунта. Переименуйте его в `client.json` и положите в папку [client](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/client) (или скопируйте его содержимое в уже существующий пустой файл [client/client.json](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/client/client.json))
3. `python3 main.py https://docs.google.com/spreadsheets/d/1IyfSPiiR0DUxYuConiYzuokM2hUQbOBpuJAeAlGi7kc/edit#gid=223389382` (в аргументе можно передать ссылку на другую root-таблицу). Моя версия python: 3.8.10

**Какие данные можно использовать для тестирования фронтенда?**  
Сейчас только [data/2022-12-22_02:31:57/root.csv](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/2022-12-22_02:31:57/root.csv). В [Tutorial.ipynb](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/Tutorial.ipynb) описала, как можно анализировать эту таблицу
 
### Текущая структура проекта

* [requirements.txt](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/requirements.txt) - список используемых библиотек: `pip install -r requirements.txt`
* [main.py](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/main.py) - код, парсящий root-таблицу и записывающий распарсенное в .csv и .json файлы в папку [data](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data). Запускать так: `python3 main.py url`, где `url` - это ссылка на root-таблицу. Например: `https://docs.google.com/spreadsheets/d/1IyfSPiiR0DUxYuConiYzuokM2hUQbOBpuJAeAlGi7kc/edit#gid=223389382`. **Не укорачивайте ссылки (~~tinyURL~~)! Сохраните их первоначальные длину, формат и содержание!**
* [data](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data)
   * [data.json](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/data.json) - перечисление распарсенных root-таблиц в формате "url": "data/*parseDate*\_*parseTime*" (т.е. в какой подпапке папки data находится информация по root-таблице с таким url-ом)
   * папки формата *parseDate*\_*parseTime* - информация по root-таблице, которая была распарсена в дату *parseDate* во время *parseTime*. Сейчас есть только одна папка в таком формате - [2022-12-22_02:31:57](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/2022-12-22_02:31:57). Там лежат распарсенные данные по текущей [root-таблице](https://docs.google.com/spreadsheets/d/1IyfSPiiR0DUxYuConiYzuokM2hUQbOBpuJAeAlGi7kc/edit#gid=223389382), точнее пока только она сама в формате .csv. В дальнейшем там будут csv-шники распарсенных ведомостей и json, который будет связывать csv конкретной ведомости с ее ID в root-таблице
       * [root.csv](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/.../root.csv) - csv-шник с root-таблицей
* [Tutorial.ipynb](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/Tutorial.ipynb) - ноутбук со всякой аналитикой (сейчас там только аналитика root-таблицы)
* [config](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/config) - папка с конфигами
   * [config.json](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/config/config.json) - информация, помогающая в парсинге. Например, `URL_TYPE` - префиксы ссылок на ведомости и их типы
* [client](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/client) - папка со всякими ключами, токенами и т.д. для взаимодействия с API
   * [client.json](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/client/client.json) - файл с данными сервисного аккаунта, взаимодействущего с Google API