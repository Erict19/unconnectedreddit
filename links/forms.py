from django import forms
from .models import UserProfile, Link, Vote
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class UserProfileForm(forms.ModelForm):
    MardAurat = (
    	(1,_('Mahila')),
    	(0,_('Purush')),
    	)
    MaritalStatus = (
    	(1,_('Yes')),
    	(0,_('No')),
    	)
    gender = forms.TypedChoiceField(choices=MardAurat, widget=forms.RadioSelect, coerce=int)
    shadi_shuda = forms.TypedChoiceField(choices=MaritalStatus, widget=forms.RadioSelect, coerce=int)
    class Meta:
        model = UserProfile
        exclude = ('user','previous_retort') #so user and previous_retort doesn't show, but the extended attributes of bio and mobile number do show    
        fields=('bio', 'mobilenumber', 'age', 'gender', 'shadi_shuda')

class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        exclude = ("submitter", "rank_score", "category")
        fields = ("description", "url")

class VoteForm(forms.ModelForm): #creates a form for Vote
    class Meta:
        model = Vote

#####################################################################################################