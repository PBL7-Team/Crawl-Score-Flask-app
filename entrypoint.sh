#!/bin/bash

# Start Gunicorn server
gunicorn -w 4 -b 0.0.0.0:8000 app:app &

# Thêm một dòng lệnh vào crontab để chạy mỗi phút
echo "* * * * * /usr/bin/python3 /path/to/cron_task.py >> /path/to/cron_output.log 2>&1" > /etc/cron.d/my_cron_job

# Apply permissions
chmod 0644 /etc/cron.d/my_cron_job

# Start cron service
cron

# Keep the container running
tail -f /dev/null
