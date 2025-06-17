FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
COPY .env.local .env
RUN npm run build

EXPOSE 80
CMD ["npm", "run", "dev", "--", "--host"]