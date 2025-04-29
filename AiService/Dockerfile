# Use the official Python 3.11 image as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /python

# Copy the current directory contents into the container
COPY . /python

RUN python -m pip install --upgrade pip


# Install any necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the application
CMD ["uvicorn", "main:app", "--reload", "--port", "8089"]