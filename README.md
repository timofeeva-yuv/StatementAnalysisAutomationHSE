# StatementAnalysisAutomationHSE

**Запуск веб-сервера - см. [webpanel/README.md](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/webpanel/README.md)**

**Порядок действий для взаимодействия с бэкендом:**
1. `pip install -r requirements.txt`
2. Настройте сервисный Google аккаунт, который будет дергать Google API: [инструкция](https://pygsheets.readthedocs.io/en/staging/authorization.html). В параграфе Service Account вы скачаете json с данными сервисного аккаунта. Переименуйте его в `client.json` и положите в папку [client](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/client) (или скопируйте его содержимое в уже существующий пустой файл [client/client.json](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/client/client.json))
3. Запустите программу так `python3 StatementAnalysis.py [URL UPD_FLG RETRY_FLG]`. Например: `python3 StatementAnalysis.py https://docs.google.com/spreadsheets/d/1IyfSPiiR0DUxYuConiYzuokM2hUQbOBpuJAeAlGi7kc/edit#gid=223389382 0 0` (без переданных аргументов).  
`URL` - ссылка на таблицу с ведомостями  
`UPD_FLG` - (1 или 0) нужно ли обновить обработку, даже если таблица была обработана  
`RETRY_FLG` - (1 или 0) нужно ли продолжить обработку, если обработка была начата и прервалась  
Аргументы можно не передавать. Тогда их значения будут взяты из кода  
Версия python, использованная при разработке: 3.8.10
 
### Текущая структура проекта

* [requirements.txt](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/requirements.txt) - список используемых библиотек: `pip install -r requirements.txt`
* [StatementAnalysis.py](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/StatementAnalysis.py) - код бэкенда
* [webpanel](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/webpanel) - папка с кодом фронтенда
* [data](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data)
   * [data.json](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/data.json) - перечисление распарсенных root-таблиц в формате {ссылка}: {путь}. Подробнее - в [data/README.md](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/data/README.md)
* [Analysis.ipynb](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/Analysis.ipynb) - ноутбук с аналитикой парсера
* [config](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/config) - папка с конфигами. Подробнее - в [config/README.md](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/config/README.md)
* [client](https://github.com/timofeeva-yuv/StatementAnalysisAutomationHSE/blob/main/client) - папка с ключами, токенами и т.д. для взаимодействия с API
