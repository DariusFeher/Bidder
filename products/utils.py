from datetime import datetime, time
import os

def date_diff_in_seconds(dt2, dt1):
  timedelta = dt2 - dt1
  return timedelta.days * 24 * 3600 + timedelta.seconds

def dhms_from_seconds(seconds):
	minutes, seconds = divmod(seconds, 60)
	hours, minutes = divmod(minutes, 60)
	days, hours = divmod(hours, 24)
	return (days, hours, minutes)


def handle_uploaded_file(f):
    if f is not None:
        with open('static/img/' + str(f), 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)


def handle_file(new_f, old_f, delete):
    picture = new_f
    if new_f != old_f:
        if old_f and os.path.exists('static/img/' + str(old_f)):
            os.remove('static/img/' + str(old_f))
            old_f = None
        handle_uploaded_file(new_f)
    if delete and old_f and os.path.exists('static/img/' + str(old_f)):
        picture = None
        os.remove('static/img/' + str(old_f))
    return picture