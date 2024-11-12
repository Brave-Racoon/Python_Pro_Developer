# docker build -t hw01 .
# docker run hw01

FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Run the script when the container launches
CMD ["python", "log_interpreter.py"]