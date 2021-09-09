from datetime import datetime, time
import os
import boto3
from django.core.files.storage import default_storage

def date_diff_in_seconds(dt2, dt1):
  timedelta = dt2 - dt1
  return timedelta.days * 24 * 3600 + timedelta.seconds

def dhms_from_seconds(seconds):
	minutes, seconds = divmod(seconds, 60)
	hours, minutes = divmod(minutes, 60)
	days, hours = divmod(hours, 24)
	return (days, hours, minutes)

def handle_file(new_f, old_f, delete):
    picture = new_f
    if new_f != old_f:
        if old_f and default_storage.exists(str(old_f)):
            default_storage.delete(str(old_f))
            old_f = None
    if delete and old_f and default_storage.exists(str(old_f)):
        picture = None
        default_storage.delete(str(old_f))
    return picture