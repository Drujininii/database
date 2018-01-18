FROM ubuntu:16.04

MAINTAINER Drujinin Igor

RUN apt-get -y update

RUN apt-get install -y python3 \
&& apt-get install -y python3-pip nginx \
&& pip3 install --upgrade pip


ENV PGVER 9.5

RUN apt-get install -y postgresql-$PGVER

ENV WORK /opt/src
ADD app/ $WORK/app
ADD flask_db_1.sql/ $WORK/
ADD run.py/ $WORK/
ADD nginx.conf/ $WORK/
ADD wsgi.py/ $WORK/
ADD requirements.txt/ $WORK/
#ADD tech_db_forum/ $WORK/
WORKDIR $WORK/

RUN pip3 install -r requirements.txt
RUN nginx -t && cat nginx.conf >> /etc/nginx/sites-available/db \
&& ln -s /etc/nginx/sites-available/db /etc/nginx/sites-enabled \
&& nginx -t \
&& service nginx restart

USER postgres

RUN /etc/init.d/postgresql start && \
    psql --command "CREATE USER igor WITH SUPERUSER PASSWORD 'qwerty';" && \
    psql --command "CREATE DATABASE flask_db_1 OWNER igor ENCODING 'UTF-8' LC_COLLATE 'C.UTF-8' LC_CTYPE 'C.UTF-8' TEMPLATE template0;" &&\
    psql flask_db_1 < flask_db_1.sql && \
    /etc/init.d/postgresql stop;

RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/$PGVER/main/pg_hba.conf \
&& echo "listen_addresses='*'" >> /etc/postgresql/$PGVER/main/postgresql.conf \
&& echo "synchronous_commit='off'" >> /etc/postgresql/$PGVER/main/postgresql.conf \
&& echo "fsync = 'off'" >> /etc/postgresql/$PGVER/main/postgresql.conf \
&& echo "max_wal_size = 300MB" >> /etc/postgresql/$PGVER/main/postgresql.conf \
&& echo "shared_buffers = 128MB" >> /etc/postgresql/$PGVER/main/postgresql.conf \
&& echo "effective_cache_size = 256MB" >> /etc/postgresql/$PGVER/main/postgresql.conf \
&& echo "work_mem = 16MB" >> /etc/postgresql/$PGVER/main/postgresql.conf

EXPOSE 5432

VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]

USER root

EXPOSE 5000

CMD service postgresql start && gunicorn -w 8 -k sync --worker-connections 12 -b 0.0.0.0:5000 wsgi:app