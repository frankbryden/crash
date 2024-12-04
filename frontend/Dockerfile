
FROM node:18-alpine AS builder
# ENV NODE_ENV production
# Add a work directory
WORKDIR /app
# Cache and Install dependencies
COPY package.json .
COPY package-lock.json .
RUN npm install

# Install Vite as a global package
# RUN npm install -g vite

ENV BACKEND=$BACKEND

# Copy app files
COPY . .
# Build the app
RUN npm run build

CMD ["watch", "ls"]

# Bundle static assets with nginx
FROM nginx:1.23.4-alpine as production
ENV NODE_ENV production

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html
COPY ./public /user/share/share/nginx/html/public

# Add your nginx.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Expose port
EXPOSE 80
# Start nginx
CMD ["nginx", "-g", "daemon off;"]