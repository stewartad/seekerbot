#!/bin/sh

echo "Waiting for API"

STATUS=-1
SECONDS=0

while [ $STATUS -ne 200 ]; do
    STATUS=`curl http://api:8000/seekerbot/ -s -o /dev/null -w "%{http_code}"`
    RC=`echo $?`
    if [[ $RC -ne 0 && $SECONDS -ge 60 ]]; then
      echo "Connection Failed, Status Code: $STATUS"
      return 1
    fi
done

echo "Connection Succeeded, Status Code: $STATUS"
exec "$@"