#!/bin/bash

IP_ADDRESS=$1
echo "[SCANNER] start ..."

for port in $(nmap $IP_ADDRESS/32); do
    PORT=$(echo $port|grep tcp|cut -d '/' -f1)
    if [ "$PORT" != "" ]; then
      echo " checking server response on port : " $PORT
      wget -q -S -t 2 --no-check-certificate --timeout=2 -O - "http://"$IP_ADDRESS":"$PORT >> tmp
      if [$(cat tmp | grep "connected") != ""];then
        echo "[SCANNER] HTTP server response on port " $PORT
      fi
      rm -f tmp
      wget -q -S -t 2 --no-check-certificate  --timeout=2 -O - "https://"$IP_ADDRESS":"$PORT >> tmp
      if [$(cat tmp | grep "connected") != ""];then
        echo "[SCANNER] HTTPS server response on port " $PORT
      fi
      rm -f tmp
    fi
done
