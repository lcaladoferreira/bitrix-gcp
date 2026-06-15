# Use the official Python image
FROM python:3.11-slim

# Allow statements and errors to be immediately logged to Cloud Logging
ENV PYTHONUNBUFFERED True

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy local code to the container image
COPY . .

# Command to run the pipeline
CMD ["python", "main.py"]
