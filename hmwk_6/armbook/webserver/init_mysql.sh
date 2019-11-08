#!/bin/bash
# Run my bash script to start SQL and make the armbook database
service mysql start
mysql -uadmin -ppass -e "CREATE DATABASE IF NOT EXISTS armbook;"
mysql -uadmin -ppass armbook < /var/www/html/armbook.sql