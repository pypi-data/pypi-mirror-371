import signal
import traceback

from walker.app_session import AppSession
from walker.apps import Apps
from walker.sso.idp import Idp
from walker.sso.idp_login import IdpLogin
from walker.commands.command import Command
from walker.repl_state import ReplState
from walker.utils import log, log2

class Login(Command):
    COMMAND = 'login'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Login, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Login.COMMAND

    def run(self, cmd: str, state: ReplState):
        def custom_handler(signum, frame):
            AppSession.ctrl_c_entered = True

        signal.signal(signal.SIGINT, custom_handler)

        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)

        username: str = None
        if len(args) > 0:
            username = args[0]

        login: IdpLogin = None
        try:
            if not(host := Apps.app_host('c3', 'c3', state.namespace)):
                log2('Cannot locate ingress for app.')
                return state

            if not (login := Idp.login(host, username=username, use_token_from_env=False)):
                log2('Invalid username/password. Please try again.')
        except:
            log2(traceback.format_exc())

        log(f'IDP_TOKEN={login.ser() if login else ""}')

        return state

    def completion(self, _: ReplState):
        return {}

    def help(self, _: ReplState):
        return f'{Login.COMMAND}\t SSO login'