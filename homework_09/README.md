### ML model serving
***
Цель:

Реализовать API для взаимодействия с ML моделями


Описание/Пошаговая инструкция выполнения домашнего задания:

В этом домашнем задании предлагается реализовать REST API, занимающегося инференсом некой модели машинного 
обучения, т.е. поступает набор признаков объекта, на выходе возвращается предсказание модели. В качестве основы 
проекта предлагается фреймворк FastAPI.

***

Подключена модель cointegrated/rubert-tiny-toxicity с https://huggingface.co/cointegrated/rubert-tiny-toxicity
Определяет степень "токсичности" текста.

Вход: строка текста

Выход: JSON вида 
{
  "text": "Кто тут котиков не любит?",
  "sentiment_label": "non-toxic",
  "sentiment_score": 0.9998007416725159
}

{
  "text": "За всё ответишь, скотина!",
  "sentiment_label": "insult",
  "sentiment_score": 0.997105062007904
}

Запуск локально: uvicorn app.app:app --host 127.0.0.1 --port 8080
Запуск в Docker: docker build -t hw09 . / docker run -p 80:80 hw09

Проверка API локально: http://127.0.0.1:8080/docs
Проверка API в Docker: http://localhost/docs

***
