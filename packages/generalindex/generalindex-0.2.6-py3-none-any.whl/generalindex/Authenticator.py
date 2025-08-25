import base64
import os
import re

from .utils import log


class Authenticator:
    def __init__(self):
        self.token = os.getenv('NG_API_AUTHTOKEN')
        self.login = os.getenv('LOGIN')
        self.password = os.getenv('PASSWORD')

    def get_token(self):
        if self.token is not None:
            log.debug('Authentication with Web Token ...')
            if bool(re.match('Bearer', self.token, re.I)) or bool(re.match('Basic', self.token, re.I)) or bool(
                    re.match('ApiKey', self.token, re.I)):
                return {'Authorization': f'{self.token}'}
            elif self.token.startswith("NG_"):
                return {'Authorization': f'ApiKey {self.token}'}
            elif len(self.token) < 70:
                return {'Authorization': f'Basic {self.token}'}
            else:
                return {'Authorization': f'Bearer {self.token}'}
        else:
            if self.login is not None and self.password is not None:
                log.debug('Authentication with Credentials ...')
                credentials = self.login + ":" + self.password
                message_bytes = credentials.encode('ascii')
                base64_enc = base64.b64encode(message_bytes).decode('UTF-8')

                d = {'Authorization': f"Basic {base64_enc}"}
                return d

            else:
                log.error('No login or password provided, neither token can be read from environment variable.')
                raise Exception('Authentication issue : no credentials found')
