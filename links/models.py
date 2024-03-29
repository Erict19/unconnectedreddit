from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.core.urlresolvers import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from math import log
from django.core.validators import MaxLengthValidator
from django.utils.translation import ugettext_lazy as _
import os
import uuid

def upload_to_location(instance, filename):
    try:
        blocks = filename.split('.') 
        ext = blocks[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        instance.title = blocks[0]
        return os.path.join('uploads/', filename)
    except Exception as e:
        print '%s (%s)' % (e.message, type(e))
        return 0

def upload_avatar_to_location(instance, filename):
    try:
        blocks = filename.split('.') 
        ext = blocks[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        instance.title = blocks[0]
        return os.path.join('uploads/', filename)
    except Exception as e:
        print '%s (%s)' % (e.message, type(e))
        return 0

CATEGS = (
('1',_('Gupshup')),
('2',_('Songs')),
('3',_('Funny')),
('4',_('Videos')),
('5',_('Cricket')),
('6',_('Photos')),
('7',_('Ajeeb')),
('8',_('Dosti')),
('9',_('Khareedna Baichna'))
	)

class LinkVoteCountManager(models.Manager): #this class is derived from model manager
	def get_query_set(self): #all we're doing here is over-riding get_query_set. 
		#query_set = super(LinkVoteCountManager, self).get_query_set()
		#query_set_annotated = query_set.annotate(votes=Sum('vote__value'))
		#query_set_ordered = query_set_annotated.order_by('-rank_score', '-votes') #-rank_score and -votes means descending order
		#return query_set_ordered
		return super(LinkVoteCountManager, self).get_query_set().annotate(votes=Sum('vote__value')).order_by('-rank_score', '-votes') #-rank_score and -votes means descending order

			 #using a parent-class function here, over-riding query_set to include Sum field
# annotate allows annotating the results of any query_set with some aggregate function like sum, count, average
class Link(models.Model):
	description = models.TextField(_("Kuch likho:"), validators=[MaxLengthValidator(500)])#, max_length=500)
	submitter = models.ForeignKey(User) # link.submitter is a user!
	submitted_on = models.DateTimeField(auto_now_add=True)
	rank_score = models.FloatField(default=0.0)
	url = models.URLField(_("Link (agar hai):"), max_length=250, blank=True)
	category = models.CharField(_("Category"),choices=CATEGS, default=1, max_length=25)
	image_file = models.ImageField(upload_to=upload_to_location, null=True, blank=True)
	
	with_votes = LinkVoteCountManager() 
	objects = models.Manager() #default, in-built manager
	
	def __unicode__(self): # built-in function
		return self.description
		#return self.upvote+self.downvote

	def get_absolute_url(self): #this function tells your browser where to redirect to once a link has been created.
		return reverse("link_detail", kwargs={"pk": str(self.id)})

	def set_rank(self): # it seems this is run ONLY when validating models is called (pressing ctrl S after changin code)
		# Based on reddit ranking algo at http://amix.dk/blog/post/19588
		epoch = datetime(1970, 1, 1).replace(tzinfo=None)
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
	value = models.IntegerField(null=True, blank=True, default=0)

	def __unicode__(self):
		#return self.value
		return "%s gave %s to %s" % (self.voter.username, self.value, self.link.description)

class UserProfile(models.Model):
	user = models.OneToOneField(User, unique=True)
	bio = models.TextField(_("Apney baarey mein kuch khaas baat batao"), default=_("Main apni favorite hoon..."), null=True)
	gender = models.CharField(_("Mahila ya purush?"), max_length=10, default=1)
	age = models.PositiveIntegerField(_("Kitni umar hai?"), null=True)
	shadi_shuda = models.CharField(_("Shaadi kar li hai?"), max_length=10, default=0)
	previous_retort = models.CharField(blank=True, max_length=500)
	attractiveness = models.CharField(_("Shakal soorat"), max_length=50, default=1)
	mobilenumber = models.CharField(_("Mobile number"), max_length=15)
	score = models.IntegerField(_("Score"), default=0)
	avatar = models.ImageField(_("Apni photo dalo"), upload_to=upload_avatar_to_location, null=True, blank=True )

	def __unicode__(self):
		return "%s's profile" % self.user

def create_profile(sender, instance, created, **kwargs):
	if created:
		profile, created = UserProfile.objects.get_or_create(user=instance)

class UserSettings(models.Model):
	user = models.OneToOneField(User, unique=True)
	score_setting = models.CharField(_("Sab ka score dikhao"), max_length=20, default=0)
	setting2 = models.CharField(_("Setting2"), max_length=20, default=0)
	setting3 = models.CharField(_("Setting3"), max_length=20, default=0)
	setting4 = models.CharField(_("Setting4"), max_length=20, default=0)
	setting5 = models.CharField(_("Setting5"), max_length=20, default=0)

	def __unicode__(self):
		return "%s's settings" % self.user


# Signal, while saving user
from django.db.models.signals import post_save
post_save.connect(create_profile, sender=User)

