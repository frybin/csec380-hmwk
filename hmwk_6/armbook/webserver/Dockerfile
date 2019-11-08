FROM linuxconfig/lemp

# Full send armbook
COPY ./armbook /var/www/html

# Copy nginx config
COPY ./default.conf /etc/nginx/sites-enabled/default

# Copy certs over
COPY ./nginx.crt /etc/nginx/
COPY ./nginx.key /etc/nginx/

# Turn on mysql
COPY ./init_mysql.sh /
RUN chmod +x /init_mysql.sh
RUN ./init_mysql.sh

# Exposed
EXPOSE 80 443