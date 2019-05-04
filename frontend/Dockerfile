FROM node:9
RUN printf "deb http://archive.debian.org/debian/ jessie main\ndeb-src http://archive.debian.org/debian/ jessie main\ndeb http://security.debian.org jessie/updates main\ndeb-src http://security.debian.org jessie/updates main" > /etc/apt/sources.list
RUN apt-get update && apt-get install -y apt-transport-https
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt-get update && apt-get install -y yarn
RUN npm install -g cross-env
WORKDIR .
COPY src/ /src/
COPY dist/ /dist/
COPY index.hbs /
COPY package.json /
COPY postcss.config.js /
COPY webpack.config.js /
COPY webpack.config.production.js /
COPY yarn.lock /
RUN yarn
CMD yarn start
