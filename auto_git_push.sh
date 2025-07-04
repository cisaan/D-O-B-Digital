#!/bin/bash
# Auto-push script for Python project on Desktop
# Pulls latest changes, commits daily update if needed, and pushes to GitHub

export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

LOGFILE="/Users/zeeshann/Desktop/Pychrm/auto_git_push.log"
ERRORLOG="/Users/zeeshann/Desktop/Pychrm/launchagent_error.log"
OUTPUTLOG="/Users/zeeshann/Desktop/Pychrm/launchagent_output.log"

# Delete log files if larger than 5MB
MAXSIZE=5242880

for file in "$LOGFILE" "$ERRORLOG" "$OUTPUTLOG"; do
  if [ -f "$file" ] && [ $(stat -f%z "$file") -gt $MAXSIZE ]; then
    rm "$file"
    echo "Deleted large log file: $file" >> "$LOGFILE"
  fi
done

echo "Starting Python Project Auto Push..." >> "$LOGFILE" 2>&1
date >> "$LOGFILE" 2>&1

cd /Users/zeeshann/Desktop/Pychrm || {
  echo "Failed to cd to project folder" >> "$LOGFILE"
  exit 1
}

git pull --no-rebase origin main >> "$LOGFILE" 2>&1 || {
  echo "git pull failed" >> "$LOGFILE"
  exit 1
}

echo "Last update: $(date '+%Y-%m-%d %H:%M:%S')" > last_updated.txt

git add . >> "$LOGFILE" 2>&1 || {
  echo "git add failed" >> "$LOGFILE"
  exit 1
}

if git diff-index --quiet HEAD --; then
  echo "No changes to commit" >> "$LOGFILE"
else
  git commit -m "chore: daily python project update - $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOGFILE" 2>&1 || {
    echo "git commit failed" >> "$LOGFILE"
  }
fi

git push origin main >> "$LOGFILE" 2>&1 || {
  echo "git push failed" >> "$LOGFILE"
  exit 1
}

echo "Python project auto push complete ✅" >> "$LOGFILE"
