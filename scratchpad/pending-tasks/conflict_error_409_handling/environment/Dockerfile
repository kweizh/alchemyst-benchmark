FROM node:20-alpine

# Create a non-root user
RUN adduser -D -s /bin/sh user

WORKDIR /home/user/myproject

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install @alchemystai/sdk

# Set ownership
RUN chown -R user:user /home/user/myproject

USER user
