#!/usr/bin/env python
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unconnectedreddit.settings")
from links.models import Link

def rank_all():
    for link in Link.with_votes.all():
        link.set_rank()

import time

def show_all():
    print "\n".join("%10s %0.2f" % (l.submitter, l.rank_score,
                         ) for l in Link.with_votes.all())
    print "----\n\n\n"

if __name__=="__main__":
        print "---"
        rank_all()
        show_all()