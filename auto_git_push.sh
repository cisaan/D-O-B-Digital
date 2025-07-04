#!/bin/bash

echo "Starting Python Project Auto Push..."

# Delete old logs if larger than 5 MB
if [ -f /Users/zeeshann/Desktop/Pychrm/auto_git_push.log ]; then
  if [ $(stat -f%z /Users/zeeshann/Desktop/Pychrm/auto_git_push.log) -gt 5242880 ]; then
    rm /Users/zeeshann/Desktop/Pychrm/auto_git_push.log
    echo "Log file was too big. Deleted and reset." > /Users/zeeshann/Desktop/Pychrm/auto_git_push.log
  fi
fi

cd /Users/zeeshann/Desktop/Pychrm

git pull --no-rebase origin main

echo "Last update: $(date '+%Y-%m-%d %H:%M:%S')" > last_updated.txt

git add .

git commit -m "chore: daily python project update - $(date '+%Y-%m-%d %H:%M:%S')"

git push origin main

echo "Python project auto push complete ✅"
