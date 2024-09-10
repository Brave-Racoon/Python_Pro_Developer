FROM python:3.11

ENV PYTHONUNBUFFERED=1

RUN mkdir -p /usr/src/homework_09
WORKDIR /usr/src/homework_09

# COPY ./Pipfile* .
COPY requirements.txt ./requirements.txt
#RUN pip install pipenv
#RUN pipenv install --system --deploy --ignore-pipfile
RUN pip install -r requirements.txt
COPY ./app ./app
COPY ./model ./model


# Run application
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "80"]

# docker build -t hw09 .
# docker run -p 80:80 hw09
