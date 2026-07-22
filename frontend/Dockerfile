# Use Node.js 18 alpine image for a small footprint
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json ./
RUN npm install

# Copy all other frontend source code
COPY . .

# Build the React app for production
RUN npm run build

# Use Nginx to serve the static built files
FROM nginx:alpine

# Copy built files from the 'build' stage to Nginx's web folder
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
