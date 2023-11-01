# Use the latest official python image as the base image
FROM python:3

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the requirements.txt into the container
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the scraper code into the container
COPY . .

VOLUME /usr/src/app/shared
# Specify the command to run on container start
CMD ["python3", "main.py"]


