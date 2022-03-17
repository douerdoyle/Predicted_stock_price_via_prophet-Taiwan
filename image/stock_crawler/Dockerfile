# FROM tiangolo/uwsgi-nginx-flask:python3.7
FROM python:3.7
ENV TZ Asia/Taipei

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update
RUN apt-get install -y supervisor cron nano tor
RUN apt-get -y autoremove

RUN mkdir -p /var/log/supervisor

COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY crontab /etc/cron.d/crontab
RUN chmod a+x /etc/cron.d/crontab
RUN touch /var/log/cron.log
RUN crontab /etc/cron.d/crontab

RUN mkdir /container_init/
COPY first_run.sh /container_init/first_run.sh
COPY requirements.txt /container_init/requirements.txt
RUN chmod a+x /container_init/first_run.sh
RUN chmod a+x /container_init/requirements.txt
RUN  /container_init/first_run.sh
RUN rm -rf /container_init/

WORKDIR /app/

CMD /usr/bin/supervisord -c /etc/supervisor/supervisord.conf