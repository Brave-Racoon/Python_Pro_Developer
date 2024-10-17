FROM python:3.11

ENV PYTHONUNBUFFERED=1

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY ./Pipfile* .
RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile
COPY ./mysite .

RUN python manage.py collectstatic --no-input

#ENTRYPOINT [ "python", "manage.py" ]
