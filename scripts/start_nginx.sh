# with logs
openresty -p (pwd)/nginx -c nginx.conf -g "daemon off;"

#without logs 
# openresty -p $(pwd)/nginx -c nginx.conf 

#kill nginx
# openresty -p (pwd)/nginx -c nginx.conf -s stop