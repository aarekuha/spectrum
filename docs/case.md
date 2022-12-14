# Тестовое задание для python-разработчика

### Задача

Реализовать парсер произвольных сайтов и HTTP API для просмотра результатов парсинга. 

#### Требования к парсеру

- должен принимать на вход адрес сайта, максимальную глубину обхода и количество одновременно загружаемых страниц
- на глубине 0, нужно сохранить только данные с переданной в параметрах страницы
- на глубине n+1, нужно сохранить данные страниц, на которые есть ссылки на странице глубины n
- под данными страницы понимается её `html`, `url` и `title`
- каждая страница должна сохраняться не больше одного раза

#### Требования к HTTP API

- нужны два метода
  - получение списка страниц с их адресами и заголовками (с возможностью поиска по обоим полям)
  - получение html конкртеной страницы
- спецификация в машиночитаемом формате (Open api, etc.)

#### Общие требования к решению

- язык реализации `python3.7+`
- весь ввод-вывод асинхронный (asyncio или trio)
- запуск в docker
- оформление в виде git-репозитория 
- требований кроме описанных выше нет, что в частности означает, что можно использовать любые БД/фреймворк/библиотеки

#### Будет большим плюсом

- наличие аннотаций типов с автоматизированной проверкой mypy
- наличие тестов