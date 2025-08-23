import getpass
import os
from pathlib import Path
import traceback
from dotenv import load_dotenv
from urllib.parse import urlparse

from walker.sso import authn_okta
from walker.sso.authenticator import Authenticator
from walker.sso.authn_ad import AdAuthenticator
from walker.sso.sso_config import SsoConfig
from .idp_login import IdpLogin
from walker.config import Config
from walker.k8s_utils.kube_context import KubeContext
from walker.utils import log, log2

class IdpSession:
    def __init__(self, idp_uri: str, authenticator: Authenticator):
        self.idp_uri = idp_uri
        self.authenticator = authenticator

    def create(email: str, client_id: str, app_host: str, idp_uri: str = None) -> 'IdpSession':
        if not idp_uri:
            idp_uri = SsoConfig().find_idp_uri(email, client_id, app_host)

        authn = IdpSession._authenticator(idp_uri)
        if not authn:
            return None

        return IdpSession(idp_uri, authn)

    def idp_host(self):
        return urlparse(self.idp_uri).hostname

    def _authenticator(idp_uri) -> Authenticator:
        idp = urlparse(idp_uri).hostname

        if 'okta' in idp.lower():
            return authn_okta.OktaAuthenticator()
        elif 'microsoftonline' in idp.lower():
            return AdAuthenticator()
        else:
            log2(f'{idp} is not supported; only okta and ad are supported.')

            return None

    def login_from_env_var(self) -> IdpLogin:
        if idp_token := os.getenv('IDP_TOKEN'):
            l0: IdpLogin = IdpLogin.deser(idp_token)
            l1: IdpLogin = self.get_idp_login()
            # if l0.app_login_url == l1.app_login_url:
            if l0.state != 'EMPTY':
                return l0

            l0.state = l1.state

            return l0

        return None

    def get_idp_login(self) -> IdpLogin:
        return IdpLogin.create_from_idp_uri(self.idp_uri)

class CredCache:
    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(CredCache, cls).__new__(cls)

        return cls.instance

    def __init__(self):
        if not hasattr(self, 'env_f'):
            self.dir = f'{Path.home()}/.kaqing'
            self.env_f = f'{self.dir}/.credentials'
            load_dotenv(dotenv_path=self.env_f)

    def get_username(self):
        return self.get('IDP_USERNAME')

    def get_password(self):
        return self.get('IDP_PASSWORD')

    def get(self, key: str) -> str:
        return os.getenv(key)

    def cache(self, username: str, password: str = None):
        if os.path.exists(self.env_f):
            with open(self.env_f, 'w') as file:
                try:
                    file.truncate()
                except:
                    if Config().get('debug.show-out', False):
                        log2(traceback.format_exc())
                    pass

        updated = []
        updated.append(f'IDP_USERNAME={username}')
        if not KubeContext.in_cluster() and password:
            # do not store password to the .credentials file when in Kubernetes pod
            updated.append(f'IDP_PASSWORD={password}')

        if updated:
            if not os.path.exists(self.env_f):
                os.makedirs(self.dir, exist_ok=True)
            with open(self.env_f, 'w') as file:
                file.write('\n'.join(updated))

class Idp:
    ctrl_c_entered = False

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Idp, cls).__new__(cls)

        return cls.instance

    def login(app_host: str, username: str = None, idp_uri: str = None, forced = False, use_token_from_env = True, use_cached = True) -> IdpLogin:
        session: IdpSession = IdpSession.create(username, app_host, app_host, idp_uri=idp_uri)
        if not session:
            return None

        if use_token_from_env:
            if l0 := session.login_from_env_var():
                return l0

        r: IdpLogin = None
        try:
            if username:
                log(f'{session.idp_host()} login: {username}')

            while not username or Idp.ctrl_c_entered:
                if Idp.ctrl_c_entered:
                    Idp.ctrl_c_entered = False

                default_user = CredCache().get_username() if use_cached else None
                if default_user and default_user != username:
                    session = IdpSession.create(default_user, app_host, app_host)
                    if not session:
                        return None

                    if forced:
                        username = default_user
                    else:
                        username = input(f'{session.idp_host()} login(default {default_user}): ') or default_user
                else:
                    username = input(f'{session.idp_host()} login: ')

            session2: IdpSession = IdpSession.create(username, app_host, app_host)
            if not session2:
                return None

            if session.idp_host() != session2.idp_host():
                session = session2

                log(f'Switching to {session.idp_host()}...')
                log()
                log(f'{session.idp_host()} login: {username}')

            password = None
            while password == None or Idp.ctrl_c_entered: # exit the while loop even if password is empty string
                if Idp.ctrl_c_entered:
                    Idp.ctrl_c_entered = False

                default_pass = CredCache().get_password() if use_cached else None
                if default_pass:
                    if forced:
                        password = default_pass
                    else:
                        password = getpass.getpass(f'Password(default ********): ') or default_pass
                else:
                    password = getpass.getpass(f'Password: ')

            if username and password:
                r = session.authenticator.authenticate(session.idp_uri, app_host, username, password)

                return r
        finally:
            if r and Config().get('app.login.cache-creds', True):
                CredCache().cache(username, password)
            elif username and Config().get('app.login.cache-username', True):
                CredCache().cache(username)

        return None