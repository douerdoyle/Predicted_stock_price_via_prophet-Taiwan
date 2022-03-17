#! /bin/bash
echo "
client_body_buffer_size     4096M;
client_header_buffer_size   256K;
large_client_header_buffers 8 64K;

## Timeouts
client_body_timeout   3600;
client_header_timeout 3600;
send_timeout          3600;

## General Options
ignore_invalid_headers   on;
keepalive_requests      100;
recursive_error_pages    on;
server_name_in_redirect off;
server_tokens           off;

## TCP options
tcp_nodelay on;
tcp_nopush  on;

## Compression
gzip              on;
gzip_buffers      24 16k;
gzip_comp_level   8;
gzip_http_version 1.0;
gzip_min_length   0;
gzip_types        application/x-javascript application/json text/xml text/plain text/css image/x-icon application/x-perl application/x-httpd-cgi application/xml;
gzip_vary         on;
gzip_proxied      any;

## Cache setings
proxy_max_temp_file_size 4096m;
proxy_buffering off;
proxy_temp_file_write_size 128k;
proxy_intercept_errors     on;
proxy_connect_timeout 3600s;
proxy_read_timeout 3600s;
proxy_send_timeout 3600s;

uwsgi_buffering off;
uwsgi_connect_timeout 3600s;
uwsgi_read_timeout 3600s;
uwsgi_send_timeout 3600s;
fastcgi_send_timeout 3600s;
fastcgi_connect_timeout 3600s;
fastcgi_read_timeout 3600s;

fastcgi_buffers      8 4096M;
fastcgi_buffer_size  4096M;
fastcgi_busy_buffers_size 4096M;
fastcgi_max_temp_file_size 4096M;
" > /etc/nginx/conf.d/nginx_setting.conf

echo "[uwsgi]
module = run_server
callable = app
enable-threads = true
thunder-lock = true
py-autoreload = 1
wsgi-disable-file-wrapper = true
limit-post = 4294967296
processes = 4
threads = 10
" > /app/uwsgi.ini