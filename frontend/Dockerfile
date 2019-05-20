FROM node:9
RUN printf "deb http://archive.debian.org/debian/ jessie main\ndeb-src http://archive.debian.org/debian/ jessie main\ndeb http://security.debian.org jessie/updates main\ndeb-src http://security.debian.org jessie/updates main" > /etc/apt/sources.list
RUN apt-get update && apt-get install -y apt-transport-https automake autoconf libtool pkg-config nasm build-essential libgl1-mesa-glx libxi6
RUN npm install -g cross-env
WORKDIR .
COPY src/ /src/
COPY dist/ /dist/
COPY index.hbs /
COPY package.json /
COPY postcss.config.js /
COPY webpack.config.js /
COPY webpack.config.production.js /
RUN npm i
CMD npm start
