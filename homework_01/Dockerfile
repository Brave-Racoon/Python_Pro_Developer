# docker build -t hw04 .
# docker run -p 8080:8080 hw04

FROM python:3.9-slim

WORKDIR /app

COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run the script when the container launches
CMD ["python", "log_interpreter.py"]