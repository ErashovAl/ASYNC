##### Порядок запуска:
    (для запуска требуется компьютер с установненным python, docker)
* скачиваем проект из репозитория в выбранный каталог. Устанавливаем при необходимости виртуальное окружение. 
* устанавливаем зависимости: 
    
        pip install -r requirements.txt


* запускаем с помощью докера базу данныхЖ
    
        docker-compose up
    
* теперь в другой вкладке терминала, находясь в том же каталоге, набираем: 

        python main.py

---
Программа выполнит подключение к API сайта swapi.dev и скачает выбранные заранее поля всех персонажей и выгрузит их в нашу базу данных.

В программе можно настроить количество скачиваемых персонажей и сколько параллельных потоков быдет использовано с помощью переменных PERSON_COUNT  и  CHUNK_SIZE соответственно.

'' _порядок запуска указан для ПК с операционной системой Linux. Запуск под другими ОС может немного отличаться._