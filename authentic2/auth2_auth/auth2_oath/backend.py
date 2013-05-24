import logging

from django.db import transaction
from django.conf import settings

from authentic2.compat import get_user_model
import authentic2.vendor.oath.hotp as hotp
from authentic2.nonce import accept_nonce
import models
logger = logging.getLogger('authentic.auth.auth2_oath')

NONCE_TIMEOUT = getattr(settings, 'OATH_NONCE_TIMEOUT',
        getattr(settings, 'NONCE_TIMEOUT', 3600))

class OATHTOTPBackend:
    supports_object_permissions = False
    supports_anonymous_user = False

    @transaction.commit_on_success()
    def authenticate(self, username, oath_otp, format='dec6'):
        '''Lookup the TOTP or HOTP secret for the user and try to authenticate
           the proposed OTP using it.
        '''
        User = get_user_model()
        try:
            secret = models.OATHTOTPSecret.objects.get(user__username=username)
        except models.OATHTOTPSecret.DoesNotExist:
            return None
        try:
            accepted, drift = hotp.accept_totp(secret.key, oath_otp, format=format)
        except Exception, e:
            logger.exception('hotp.accept_totp raised', e)
            raise

        if accepted:
            if not accept_nonce(oath_otp, 'OATH_OTP', NONCE_TIMEOUT):
                logger.error('already used OTP %r', oath_otp)
                return None

            secret.drift = drift
            return User.objects.get(username=username)
        else:
            return None

    def get_user(self, user_id):
        """
        simply return the user object. That way, we only need top look-up the 
        certificate once, when loggin in
        """
        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def setup_totp(self, user):
        '''Create a model containing a TOTP secret for the given user and the
           current time drift which initially is zero
        '''
        pass
