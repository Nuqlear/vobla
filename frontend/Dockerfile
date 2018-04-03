FROM node:9
RUN apt-get update && apt-get install -y apt-transport-https
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt-get update && apt-get install yarn
COPY src/ /src/
COPY dist/ /dist/
COPY index.hbs /
COPY package.json /
COPY postcss.config.js /
COPY webpack.config.js /
COPY webpack.config.production.js /
COPY yarn.lock /
WORKDIR .
RUN yarn
CMD yarn start
