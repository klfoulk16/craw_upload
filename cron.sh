#!/usr/bin/env bash
source /Users/kellyfoulk/Documents/code/craw_upload/venv/bin/activate

# tell cron where to find the chromedriver download
PATH=${PATH}:/usr/local/bin
python /Users/kellyfoulk/Documents/code/craw_upload/crawActivities.py