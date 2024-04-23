# Бот для оценки выступлений

## Задача

Реализовать систему опроса слушателей во время проведения экзамена в кружке ораторского мастерства.
Слушатели будут оценивать выступающих по различным критериям.
Оценки собираются, и в конце экзамена выдается статистика, как общая, так и для всех выступащих по отдельности.

## Реализация

Проект представляет собой телеграм-бота, написанного на языке Python с помощью библиотеки python-telegram-bot.

## Функционал

Приблизительный сценарий работы бота:

![Приблизительный сценарий работы бота](https://raw.githubusercontent.com/doledenok/poll-bot/main/docs/source/_static/scenario.jpg)

## Интерфейса

Бот имеет текстовый интерфейс и взаимодействует с пользователем через Telegram.

### Примеры интерфейса:

Стартовый выбор сценария:

![](https://raw.githubusercontent.com/doledenok/poll-bot/main/docs/source/_static/start.jpg)
-----

Организатор. Проведение экзамена

![](https://raw.githubusercontent.com/doledenok/poll-bot/main/docs/source/_static/exam_managing.jpg)
----

Организатор. Просмотр результатов экзамена

![](https://raw.githubusercontent.com/doledenok/poll-bot/main/docs/source/_static/review_exam_results.jpg)
----

Студент. Регистрация на экзамен

![](https://raw.githubusercontent.com/doledenok/poll-bot/main/docs/source/_static/user_exam_joining.jpg)
----

Студент. Оценка выступающих

![](https://raw.githubusercontent.com/doledenok/poll-bot/main/docs/source/_static/user_rating.jpg)
