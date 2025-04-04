# Use the official Node.js image for building the app
FROM node:18 as build-stage

# Set working directory
WORKDIR /app

# Expose port 3000
EXPOSE 5173

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
