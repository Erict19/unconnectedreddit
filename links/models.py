from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.core.urlresolvers import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from math import log
from django.utils.translation import ugettext as _

CATEGS = (
('1',_('Funny')),
('2',_('Songs')),
('3',_('Gupshup')),
('4',_('Videos')),
('5',_('Cricket')),
('6',_('Photos')),
('7',_('Ajeeb')),
('8',_('Dosti')),
('9',_('Khareedna Baichna'))
    )

class LinkVoteCountManager(models.Manager): #this class is derived from model manager
    def get_query_set(self): #all we're doing here is over-riding get_query_set. 
        return super(LinkVoteCountManager, self).get_query_set().annotate(votes=Sum('vote__value')).order_by('-rank_score', '-votes')
             #using a parent-class function here, over-riding query_set to include count field
# annotate allows annotating the results of any query_set with some aggregate function like sum, count, average
class Link(models.Model):
    description = models.TextField(_("Kuch likho"))#, max_length=500)
    submitter = models.ForeignKey(User) # link.submitter is a user!
    submitted_on = models.DateTimeField(auto_now_add=True)
    rank_score = models.FloatField(default=0.0)
    url = models.URLField(_("Link (agar hai)"), max_length=250, blank=True)
    cagtegory = models.CharField(choices=CATEGS, default=1, max_length=25)
    
    with_votes = LinkVoteCountManager() #change this to set_rank()
    objects = models.Manager() #default, in-built manager
    
    def __unicode__(self): # built-in function
        return self.description
        #return self.upvote+self.downvote

    def get_absolute_url(self): #this function tells your browser where to redirect to once a link has been created.
        return reverse("link_detail", kwargs={"pk": str(self.id)})

    def set_rank(self): # it seems this is run ONLY when validating models is called (pressing ctrl S after changin code)
        # Based on reddit ranking algo at http://amix.dk/blog/post/19588
        epoch = datetime(1970, 1, 1)
        netvotes = self.votes # 'NONE' votes are messing up netvotes amount.
        if netvotes == None:
            netvotes = 0
        order = log(max(abs(netvotes), 1), 10) #0.041392685 for zero votes, log 1 = 0
        sign = 1 if netvotes > 0 else -1 if netvotes < 0 else 0
        unaware_submission = self.submitted_on.replace(tzinfo=None)
        td = unaware_submission - epoch 
        epoch_submission = td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000) #number of seconds from epoch till date of submission
        secs = epoch_submission - 1432201843 #a recent date, coverted to epoch time
        self.rank_score = round(sign * order + secs / 45000, 8)
        self.save() # this persists the rank_score in the database
        # the score doesn't decay as time goes by, but newer stories get a higher score over time. 

class Vote(models.Model):
    voter = models.ForeignKey(User) #what user.id voted
    link = models.ForeignKey(Link) #which link did the user vote on
    value = models.IntegerField(default=0)

    def __unicode__(self):
        return "%s upvoted %s" % (self.voter.username, self.link.description)

class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True)
    bio = models.TextField(_("Apney baarey mein kuch khaas baat batao"), default=_("Main apni favorite hoon..."), null=True)
    mobilenumber = models.CharField(_("Mobile number "), blank=True, max_length=50) #added mobile number to model, form and __init__
    gender = models.BooleanField(_("Mahila ya purush?"), default=True)
    age = models.PositiveIntegerField(_("Kitni umar hai?"), null=True)
    shadi_shuda = models.BooleanField(_("Shaadi kar li hai?"), default=False)
    previous_retort = models.CharField(blank=True, max_length=500)

    def __unicode__(self):
        return "%s's profile" % self.user

def create_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)

# Signal, while saving user
from django.db.models.signals import post_save
post_save.connect(create_profile, sender=User)

