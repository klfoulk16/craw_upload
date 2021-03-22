#!/usr/bin/env bash
source /Users/kellyfoulk/Documents/code/crawUpload/venv/bin/activate

# tell cron where to find the chromedriver download
PATH=${PATH}:/usr/local/bin
python /Users/kellyfoulk/Documents/code/crawUpload/crawActivities.py