from django import forms
from .models import UserProfile, Link, Vote
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class UserProfileForm(forms.ModelForm): #this controls the userprofile edit form
    MardAurat = (
    	(1,_('Mahila')),
    	(0,_('Purush')),
    	)
    MaritalStatus = (
    	(1,_('Yes')),
    	(0,_('No')),
    	)
    RATING = (
        (0,_('Ekdum kadak yaar')),
        (1,_('Itni burri bhi nahi')),
        (2,_('Shakal pe mat ja')),
    )
    gender = forms.TypedChoiceField(choices=MardAurat, widget=forms.RadioSelect, coerce=int)
    shadi_shuda = forms.TypedChoiceField(choices=MaritalStatus, widget=forms.RadioSelect, coerce=int)
    attractiveness = forms.TypedChoiceField(choices=RATING, widget=forms.RadioSelect, coerce=int)
    class Meta:
        model = UserProfile
        exclude = ('user','previous_retort') #so user and previous_retort doesn't show, but the extended attributes of bio and mobile number do show
        fields=('mobilenumber', 'bio', 'gender', 'age', 'shadi_shuda', 'attractiveness')

class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        exclude = ("submitter", "rank_score", "category")
        fields = ("description", "url")

class VoteForm(forms.ModelForm): #creates a form for Vote
    class Meta:
        model = Vote

class ScoreHelpForm(forms.Form):
    class Meta:
        pass