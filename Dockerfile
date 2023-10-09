# Use an official Python image as a base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /usr/app

# Set PYTHONPATH
ENV PYTHONPATH=/usr/app:$PYTHONPATH

# Copy requirements.txt and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code to the container
COPY . .

# Expose port 8001
EXPOSE 8000

# Define the command to run the application
CMD ["python3", "-m", "uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "8000"]