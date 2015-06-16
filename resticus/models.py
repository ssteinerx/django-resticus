import binascii
import os

from django.conf import settings
from django.db import models

from .compat import AUTH_USER_MODEL
from .settings import api_settings


class BaseToken(models.Model):
    key = models.CharField(max_length=40, primary_key=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
            return self.key

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(BaseToken, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def get_user(self):
        raise NotImplementedError

    class Meta:
        abstract = True

if api_settings.TOKEN_MODEL == 'resticus.Token':
    class Token(BaseToken):
        user = models.OneToOneField(AUTH_USER_MODEL, related_name='api_token')

        def get_user(self):
            return self.user
