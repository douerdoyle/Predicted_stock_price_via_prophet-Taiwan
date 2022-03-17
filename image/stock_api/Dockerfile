# FROM tiangolo/uwsgi-nginx-flask:python3.7
FROM tiangolo/uwsgi-nginx-flask:python3.7
ENV TZ Asia/Taipei

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update
RUN apt-get install -y supervisor nano tor
RUN apt-get -y autoremove

RUN mkdir -p /var/log/supervisor

COPY supervisord.conf /etc/supervisor/supervisord.conf

COPY first_run.sh /tmp/first_run.sh
COPY requirements.txt /tmp/requirements.txt
RUN chmod a+x /tmp/first_run.sh
RUN chmod a+x /tmp/requirements.txt
RUN /tmp/first_run.sh
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt
RUN rm -rf /tmp/*

WORKDIR /app/

CMD /usr/bin/supervisord -c /etc/supervisor/supervisord.conf