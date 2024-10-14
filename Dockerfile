# # Use an official Python runtime as a parent image
# FROM python:3.12-alpine

# # Set the working directory in the container
# WORKDIR /app

# # Install system dependencies using apk (Alpine's package manager)
# RUN apk update && apk add --no-cache \
#     gcc \
#     musl-dev \
#     mariadb-connector-c-dev \
#     build-base \
#     linux-headers \
#     pkgconfig

# # Copy the current directory contents into the container
# COPY . .

# # Install any required packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# # Make port 5000 available to the outside world
# EXPOSE 5000

# # Define environment variable
# ENV NAME="World"

# # Run the application
# CMD ["python", "app.py"]


# First Stage: Build Stage
FROM python:3.12-alpine AS build-stage

# Set the working directory in the build stage
WORKDIR /app

# Install system dependencies using apk (Alpine's package manager)
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    mariadb-connector-c-dev \
    build-base \
    linux-headers \
    pkgconfig

# Copy only the requirements.txt to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code to the image
COPY . .

# Second Stage: Runtime Stage
FROM python:3.12-alpine AS runtime-stage

# Set the working directory in the runtime stage
WORKDIR /app

# Copy only the necessary files from the build-stage
COPY --from=build-stage /app /app
COPY --from=build-stage /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Install any lightweight system dependencies if needed
RUN apk add --no-cache \
    mariadb-connector-c

# Expose port 5000
EXPOSE 5000

# Define environment variable
ENV NAME="World"

# Run the application
CMD ["python", "app.py"]
