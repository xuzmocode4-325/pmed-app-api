# Use the official Python 3.13 image based on Alpine 3.21 as the base image
FROM python:3.13-alpine3.21

# Set the maintainer label for the image
LABEL maintainer="xuzmonomi.com"

# Set the environment variable to enable buffered output for Python
ENV PYTHONBUFFERED=1

# Copy the requirements files to the temporary directory
COPY ./requirements.txt /tmp/requirments.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Copy the application code to the /app directory
COPY ./app /app

# Set the working directory to /app
WORKDIR /app

# Expose port 8000 for the application
EXPOSE 8000

# Define a build argument to determine if development dependencies should be installed
ARG DEV=false

# Create a virtual environment, install dependencies, and clean up
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirments.txt && \
    # If the DEV argument is true, install development dependencies
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    # Remove temporary files and uninstall build dependencies
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    # Create a non-root user for running the application
    adduser \
        --disabled-password \
        --no-create-home \ 
        app-user

# Update the PATH environment variable to include the virtual environment's bin directory
ENV PATH="/py/bin:$PATH"

# Switch to the non-root user for running the application
USER app-user