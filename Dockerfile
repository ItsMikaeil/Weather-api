# Use the official Python image as the base image
FROM python:3.12-slim

# Prevent Python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Make Python output appear immediately in Docker logs
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy dependency definitions first
# This allows Docker to reuse the dependency layer when code changes
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -i https://mirror.sjtu.edu.cn/pypi/web/simple -r requirements.txt


# Copy the application source code
COPY app ./app

# Expose the port used by FastAPI
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]