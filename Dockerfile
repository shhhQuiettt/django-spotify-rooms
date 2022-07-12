FROM node:18-alpine3.16 as development

ENV NODE_ENV development

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .

EXPOSE 3000

ENV WDS_SOCKER_PORT 0
CMD ["npm", "start"]