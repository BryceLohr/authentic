from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
import authentic2.idp.views
import settings

from forms import AuthenticRegistrationForm

admin.autodiscover()
handler500 = 'authentic2.views.server_error'


urlpatterns = patterns('',
    (r'^', include('authentic2.auth.urls')),
    (r'^redirect/(.*)', 'authentic2.views.redirect'),
    url(r'^accounts/register',
       'registration.views.register',
       { 'form_class': AuthenticRegistrationForm },
       name='registration_register',
       ),
    (r'^accounts/', include('registration.urls')),
    url(r'^logout$', 'authentic2.idp.views.logout', name='auth_logout'),
    (r'^admin/admin_log_view/log/', 'authentic2.admin_log_view.views.admin_view'),
    (r'^admin/', include(admin.site.urls)),
    (r'^idp/', include('authentic2.idp.urls')),
    (r'^logout$', 'authentic2.idp.views.logout'),
    (r'^$', login_required(authentic2.idp.views.homepage), {}, 'index'),
    (r'^profile$', login_required(authentic2.idp.views.profile), {}, 'account_management'),
)

urlpatterns += patterns('',
    (r'^authsaml2/', include('authentic2.authsaml2.urls')),
)

if settings.AUTH_SSL:
    urlpatterns += patterns('',
        url(r'^sslauth/$',
            'authentic2.sslauth.login_ssl.process_request',
            name='user_signin_ssl'),
        url(r'^sslauth/register/$',
            'authentic2.sslauth.views.register'),
        url(r'^error_ssl/$', direct_to_template,
            {'template': 'error_ssl.html'}, 'error_ssl'),
    )

if settings.STATIC_SERVE:
    urlpatterns += patterns('',
        url(
            regex = r'^media/(?P<path>.*)$',
            view = 'django.views.static.serve',
            kwargs = {'document_root': settings.MEDIA_ROOT}),
    )

if settings.IDP_OPENID:
    import authentic2.django_openid_provider.views
    import openid_provider.views
    urlpatterns += patterns('',
            (r'^openid/$',authentic2.django_openid_provider.views.openid_server, {},'openid-provider-root'),
            (r'^openid/decide/$',authentic2.django_openid_provider.views.openid_decide, {},'openid-provider-decide'),
            (r'^openid/manage/',authentic2.django_openid_provider.views.manage_trustroot, {},'manage_trustroot'),
            (r'^openid/manageid/',authentic2.django_openid_provider.views.manage_id, {},'manage_id' ),
            (r'^openid/manageid_confirm/',authentic2.django_openid_provider.views.manage_id_confirm, {}, 'manage_id_confirm'),
            (r'^openid/addopenid/',authentic2.django_openid_provider.views.addopenid, {}, 'add_openid'),
            (r'^openid/',include('openid_provider.urls')),
            url(r'^o8/(?P<id>[a-zA-Z0-9,_,]*/?)/$', openid_provider.views.openid_xrds, {'identity': True}, name='openid-provider-identity'),
    )

if 'authentic2.auth.oath' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
            (r'^oath/', include('authentic2.auth.oath.urls')))
