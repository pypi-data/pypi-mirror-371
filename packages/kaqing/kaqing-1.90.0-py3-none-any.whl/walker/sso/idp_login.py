import base64
import json
from urllib.parse import parse_qs, urlparse
import requests

class IdpLogin:
    def __init__(self, app_login_url: str, id_token: str, state: str, user: str = None, session: requests.Session = None):
        self.app_login_url = app_login_url
        self.id_token = id_token
        self.state = state
        self.user = user
        self.session = session

    def deser(idp_token: str):
        j = json.loads(base64.b64decode(idp_token.encode('utf-8')))

        return IdpLogin(j['r'], j['id'], j['state'])

    def ser(self):
        return base64.b64encode(json.dumps({
            'r': self.app_login_url,
            'id': self.id_token,
            'state': self.state
        }).encode('utf-8')).decode('utf-8')

    def create_from_idp_uri(idp_uri: str):
        parsed_url = urlparse(idp_uri)
        query_string = parsed_url.query
        params = parse_qs(query_string)
        state_token = params.get('state', [''])[0]
        redirect_url = params.get('redirect_uri', [''])[0]

        return IdpLogin(app_login_url=redirect_url, id_token=None, state=state_token)

    def shell_user(self):
        if not self.user:
            return None

        return self.user.split('@')[0].replace('.', '')