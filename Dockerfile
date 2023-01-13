FROM python:3.9

WORKDIR /hamr
COPY . /hamr

# apache2
RUN apt-get update && \
    apt-get install -y apache2 sqlite3 && \
    a2enmod cgid rewrite vhost_alias && \
    service apache2 restart

RUN mkdir -p apps && \
    chmod a+rwx apps && \
    chown www-data:www-data apps && \
    ln -s "$(pwd)/deployment/etc/apache2/sites-available/hamr.conf" "/etc/apache2/sites-available/hamr.conf" && \
    a2ensite hamr

EXPOSE 80
CMD python3 -m pip install -r requirements.txt && apachectl -D FOREGROUND
