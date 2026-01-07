# Stage 1: Build the React application
FROM node:20-alpine as build

# Set the working directory
WORKDIR /app

# Copy package.json
COPY package.json ./

# Install dependencies
RUN npm install && npm install typescript@4.9.5

# Copy the rest of the application source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Serve the application with Nginx
FROM nginx:stable-alpine

# Copy the built static files from the build stage to the Nginx server
COPY --from=build /app/build /usr/share/nginx/html

# Copy a custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
