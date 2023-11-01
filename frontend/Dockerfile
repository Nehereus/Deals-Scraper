# Use the latest official node alpine image as the base image
FROM node:alpine

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json into the container
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code into the container
COPY . .

# Create a shared volume
VOLUME /usr/src/app/shared

# Specify the command to run on container start
CMD ["npm", "run", "start"]
