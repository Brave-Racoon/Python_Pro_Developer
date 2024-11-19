# docker-compose build
# docker-compose up

FROM python:3.9-slim

WORKDIR /app
ADD crawler.py /app/
ADD requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

# Run the script when the container launches
CMD ["python", "crawler.py"]
