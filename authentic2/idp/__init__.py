import logging

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from signals import auth_login
from signals import auth_logout
from signals import auth_oidlogin
from django.conf import settings
from authentic2.admin_log_view.models import info
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

logging.basicConfig()

def load_backend(path):
    '''Load an IdP backend by its module path'''
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing idp backend %s: "%s"' % (module, e))
    except ValueError, e:
        raise ImproperlyConfigured('Error importing idp backends. Is IDP_BACKENDS a correctly defined list or tuple?')
    try:
        cls = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" idp backend' % (module, attr))
    return cls()

def get_backends():
    '''Return the list of IdP backends'''
    backends = []
    for backend_path in settings.IDP_BACKENDS:
        backends.append(load_backend(backend_path))
    return backends

def LogRegistered(sender, user, **kwargs):
    msg = user.username + ' is now registered'
    info(msg)

def LogActivated(sender, user, **kwargs):
    msg = user.username + ' has activated his account'
    info(msg)

def LogRegisteredOI(sender, openid, **kwargs):
    msg = openid 
    msg = str(msg) + ' is now registered'
    info(msg)

def LogAssociatedOI(sender, user, openid, **kwargs):
    msg = user.username + ' has associated his user with ' + openid
    info(msg)

def LogAuthLogin(sender, user, successful, **kwargs):
    if successful:
        msg = user.username + ' has logged in with success'
    else:    
        msg = user + ' has tried to login without success'
    info(msg)

def LogAuthLogout(sender, user, **kwargs):
    msg = str(user) 
    msg += ' has logged out'
    info(msg)

def LogAuthLoginOI(sender, openid_url, state, **kwargs):
    msg = str(openid_url)
    if state is 'success':
        msg += ' has login with success with OpenID'
    elif state is 'invalid':
        msg += ' is invalid'
    elif state is 'not_supported':
        msg += ' did not support i-names'
    elif state is 'cancel':
        msg += ' has cancel'
    elif state is 'failure':
        msg += ' has failed'
    elif state is 'setup_needed':
        msg += ' setup_needed'
    info(msg)

class AdminBackend(object):
    def service_list(self, request):
        if request.user.is_staff:
            return (('/admin', _('Authentic administration')),)
        return []

auth_login.connect(LogAuthLogin, dispatch_uid = "authentic2.idp")
auth_logout.connect(LogAuthLogout, dispatch_uid = "authentic2.idp")
auth_oidlogin.connect(LogAuthLoginOI, dispatch_uid ="authentic2.idp")

if settings.AUTH_OPENID:
    from django_authopenid.signals import oid_register
    from django_authopenid.signals import oid_associate
    oid_register.connect(LogRegisteredOI, dispatch_uid = "authentic2.idp")
    oid_associate.connect(LogAssociatedOI, dispatch_uid = "authentic2.idp")
