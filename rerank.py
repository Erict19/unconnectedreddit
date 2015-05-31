#!/usr/bin/env python
import os, time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unconnectedreddit.settings")
from links.models import Link

def rank_all():
    for link in Link.with_votes.all():
        link.set_rank()

def show_all():
    print "\n".join("%10s %0.2f" % (l.description, l.rank_score,
                         ) for l in Link.with_votes.all())
    print "----\n\n\n"

if __name__=="__main__":
    while 1:
        print "---"
        rank_all()
        show_all()
        time.sleep(5)
