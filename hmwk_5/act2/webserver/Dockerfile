FROM linuxconfig/lemp

# Full send armbook
COPY ./armbook /var/www/html

# Copy nginx config
COPY ./default.conf /etc/nginx/sites-enabled/default

# Copy certs over
COPY ./nginx.crt /etc/nginx/
COPY ./nginx.key /etc/nginx/

EXPOSE 80 443