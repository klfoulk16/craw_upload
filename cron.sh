#!/usr/bin/env bash
source /Users/kellyfoulk/Documents/code/crawUpload/venv/bin/activate

python /Users/kellyfoulk/Documents/code/crawUpload/test.py

if [ $? -eq 0 ]
then
  echo "Success: Cron job ran."
  exit 0
else
  echo "Failure: Script failed" >&2
  exit 1
fi
