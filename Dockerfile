
FROM ubuntu:20.04
RUN apt update && apt upgrade -y
RUN apt install python3 -y
RUN apt install python3-pip -y
RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app
COPY ./django_backend/ /usr/src/app
RUN pip install -r requirements.txt
RUN playwright install

RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
RUN apt-get install libgtk-3-0 -y
RUN apt-get install libasound2 -y
RUN apt-get install libx11-6 -y
RUN apt-get install libxcomposite1 -y
RUN apt-get install libxdamage1 -y
RUN apt-get install libxext6 -y
RUN apt-get install libxfixes3 -y
RUN apt-get install libxrandr2 -y
RUN apt-get install libxrender1 -y
RUN apt-get install libxtst6 -y
RUN apt-get install libfreetype6 -y
RUN apt-get install libfontconfig1 -y
RUN apt-get install libpangocairo-1.0-0 -y
RUN apt-get install libpango-1.0-0 -y
RUN apt-get install libatk1.0-0 -y
RUN apt-get install libcairo-gobject2 -y
RUN apt-get install libcairo2 -y
RUN apt-get install libgdk-pixbuf2.0-0 -y
RUN apt-get install libglib2.0-0 -y
RUN apt-get install libdbus-glib-1-2 -y
RUN apt-get install libdbus-1-3 -y
RUN apt-get install libxcb-shm0 -y
RUN apt-get install libx11-xcb1 -y
RUN apt-get install libxcb1 -y
RUN apt-get install libxcursor1 -y
RUN apt-get install libxi6 -y
RUN apt-get install -y gstreamer1.0-libav libnss3-tools libatk-bridge2.0-0 libcups2-dev libxkbcommon-x11-0 libxcomposite-dev libxrandr2 libgbm-dev libgtk-3-0

COPY ./utils/ /usr/src/utils
EXPOSE 80
CMD sh /usr/src/utils/run.sh