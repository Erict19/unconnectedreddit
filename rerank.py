import os, time
from celery import Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unconnectedreddit.settings")
from links.models import Link

app = Celery('rerank', broker='amqp://guest@localhost//')

@app.task
def rank_all():
    for link in Link.with_votes.all():
        link.set_rank()
