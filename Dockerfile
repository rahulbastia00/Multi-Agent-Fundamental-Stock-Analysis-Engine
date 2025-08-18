# Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if any are needed
# RUN apt-get update && apt-get install -y ...

# Copy the dependencies file to the working directory
COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy the rest of your app's source code from your host to your image filesystem.
COPY ./src /app/src

# Command to run the application using a production-ready server (Gunicorn)
# Gunicorn manages Uvicorn workers for performance and resilience.
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "src.main:app"]