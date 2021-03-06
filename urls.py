from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
from main.views_add import test


admin.autodiscover()
#handler404 = 'main.views.page_not_found2'
urlpatterns = patterns('main.views',
    url(r'^adm475/', include(admin.site.urls)),
    url(r'^$', 'check_code'),
    url(r'^coming_soon/$', 'coming_soon'),
#    url(r'^closed/$', 'registration_closed'),
    url(r'^check_code/$', 'check_code'),
    url(r'^attendance/(?P<code>\d{5})/$', 'attendance'),
    url(r'^attendance/(?P<code>\d{5})/(?P<status>\w{1})/$', 'status'),
#    url(r'^attendance/newdate/$', 'new_date'),
#    url(r'^attendance/celeb/$', 'celeb'),
    url(r'^attendance/guest/$', 'others'),
#    url(r'^attendance/prizers/$', 'prizers'),
    url(r'^send_mail/(?P<show>\w+)/$', 'send_mail'),
    url(r'^test/$', test),
    url(r'^test.txt/$', test),
#    url(r'^attendance/tguest/$', 'taras'),
#    url(r'^attendance/tguest/addr/$', 'taras_addr'),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
