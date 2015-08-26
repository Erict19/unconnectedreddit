from django.conf.urls import patterns, include, url
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin
from links.models import UserProfile, Vote
from django.views.generic.base import TemplateView
from links.views import LinkListView, UserProfileDetailView, UserProfileEditView, LinkCreateView, LinkDetailView, LinkUpdateView, LinkDeleteView, VoteFormView, ScoreHelpView #MyRegistrationView
#from django.conf.urls.i18n import i18n_patterns

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', LinkListView.as_view(), name='home'),
	url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name="login"),
	url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name="logout"),
	#url(r'^register/$', MyRegistrationView.as_view(), name='registration_register'),
	#url(r'^register/closed/$', TemplateView.as_view(template_name='registration/registration_closed.html'),
    #                      name='registration_disallowed'),
    #(r'', include('registration.auth_urls')),
	url(r'^accounts/', include('registration.backends.simple.urls')),
	url(r'^users/(?P<slug>\w+)/$', UserProfileDetailView.as_view(), name="profile"),
	url(r'^edit_profile/$', auth(UserProfileEditView.as_view()), name="edit_profile"),
	url(r'^link/create/$', LinkCreateView.as_view(), name='link_create'),
	url(r'^link/(?P<pk>\d+)/$', LinkDetailView.as_view(), name='link_detail'),
	url(r'^score/$', auth(ScoreHelpView.as_view()), name='score_help'),
	url(r'^link/update/(?P<pk>\d+)/$', auth(LinkUpdateView.as_view()), name='link_update'),
    url(r'^link/delete/(?P<pk>\d+)/$', auth(LinkDeleteView.as_view()), name='link_delete'),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^vote/$', auth(VoteFormView.as_view()), name="vote"),
    #url(r'^i18n/', include('django.conf.urls.i18n')),
    url('^i18n/setlang/', 'django.views.i18n.set_language', name='set_language'),

)