# Use the official lightweight Python image.
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
WORKDIR /app

# Install system dependencies required for mysqlclient
RUN apt-get update && apt-get install -y \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    # Needed to wait for database/redis to be ready
    netcat \ 
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the Django project code into the container
COPY . /app/

# Make the entrypoint/wait script executable (if we use one)
# We will use a simple inline command in docker-compose for waiting, 
# but if you add a script later: RUN chmod +x /app/entrypoint.sh
