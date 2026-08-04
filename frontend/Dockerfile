# Extending image
FROM node:21-alpine3.18

# Create app directory
RUN mkdir -p /app
WORKDIR /app


ARG VITE_PERSISTOR_KEY
ARG VITE_TOKEN_KEY

ENV VITE_PERSISTOR_KEY=$VITE_PERSISTOR_KEY
ENV VITE_TOKEN_KEY=$VITE_TOKEN_KEY

ENV PUBLIC_PATH "/"

COPY . .

# Install app dependencies
COPY package.json .
COPY package-lock.json .

RUN npm install --legacy-peer-deps

# Bundle app source
COPY . .
# RUN npm run build
# RUN npm install -g serve

# Port to listener
EXPOSE 7007

# Environment variables



# Main command
CMD [ "npm", "run", "dev" ]