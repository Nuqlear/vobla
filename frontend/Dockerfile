FROM node:16.3.0
RUN npm install -g cross-env

WORKDIR /vobla
COPY src/ /vobla/src/
COPY dist/ /vobla/dist/
COPY index.hbs /vobla
COPY package.json /vobla
COPY package-lock.json /vobla
COPY postcss.config.js /vobla
COPY webpack.config.js /vobla
COPY webpack.config.production.js /vobla
RUN npm i
CMD npm start
