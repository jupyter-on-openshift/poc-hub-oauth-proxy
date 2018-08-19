import os

# Enable JupyterLab interface if enabled.

c.Spawner.environment = {}

if os.environ.get('JUPYTERHUB_ENABLE_LAB', 'false').lower() in ['true', 'yes', 'y', '1']:
    c.Spawner.environment.update(dict(JUPYTER_ENABLE_LAB='true'))

# Setup location for customised template files.

c.JupyterHub.template_paths = ['/opt/app-root/src/templates']

# Populate admin users and use white list from config maps.

if os.path.exists('/opt/app-root/configs/admin_users.txt'):
    with open('/opt/app-root/configs/admin_users.txt') as fp:
        content = fp.read().strip()
        if content:
            c.Authenticator.admin_users = set(content.split())

if os.path.exists('/opt/app-root/configs/user_whitelist.txt'):
    with open('/opt/app-root/configs/user_whitelist.txt') as fp:
        content = fp.read().strip()
        if content:
            c.Authenticator.whitelist = set(content.split())

# User access. Temporarily trust header sent by the proxy. This
# needs to be replaced to use the access token to lookup Keycloak
# and verify the user identity.

#c.JupyterHub.authenticator_class = 'jhub_remote_user_authenticator.remote_user_auth.RemoteUserAuthenticator'
#c.RemoteUserAuthenticator.header_name = 'X_FORWARDED_USER'

# Provide persistent storage for users notebooks.

c.KubeSpawner.user_storage_pvc_ensure = True

c.KubeSpawner.pvc_name_template = '%s-nb-{username}' % c.KubeSpawner.hub_connect_ip
c.KubeSpawner.user_storage_capacity = os.environ['NOTEBOOK_VOLUME_SIZE']

c.KubeSpawner.volumes = [
    {
        'name': 'data',
        'persistentVolumeClaim': {
            'claimName': c.KubeSpawner.pvc_name_template
        }
    }
]

c.KubeSpawner.volume_mounts = [
    {
        'name': 'data',
        'mountPath': '/opt/app-root/src',
        'subPath': 'notebooks'
    }
]

c.Spawner.environment.update(dict(
    JUPYTER_MASTER_FILES='/opt/app-root/master',
    JUPYTER_WORKSPACE_NAME='workspace'))

# Setup culling of idle notebooks if timeout parameter is supplied.

idle_timeout = os.environ.get('JUPYTERHUB_IDLE_TIMEOUT')

if idle_timeout and int(idle_timeout):
    c.JupyterHub.services = [
        {
            'name': 'cull-idle',
            'admin': True,
            'command': ['cull-idle-servers', '--timeout=%s' % idle_timeout],
        }
    ]


######

import os
from jupyterhub.handlers import BaseHandler
from jupyterhub.auth import Authenticator
from jupyterhub.auth import LocalAuthenticator
from jupyterhub.utils import url_path_join
from tornado import gen, web
from traitlets import Unicode


class RemoteUserLoginHandler(BaseHandler):

    def get(self):
        header_name = self.authenticator.header_name
        print('HEADERS', self.request.headers)
        remote_user = self.request.headers.get(header_name, "")
        if remote_user == "":
            raise web.HTTPError(401)
        else:
            user = self.user_from_username(remote_user)
            self.set_login_cookie(user)
            self.redirect(url_path_join(self.hub.server.base_url, 'home'))


class RemoteUserAuthenticator(Authenticator):
    """
    Accept the authenticated user name from the REMOTE_USER HTTP header.
    """
    header_name = Unicode(
        default_value='X-Forwarded-User',
        config=True,
        help="""HTTP header to inspect for the authenticated username.""")

    def get_handlers(self, app):
        return [
            (r'/login', RemoteUserLoginHandler),
        ]

    @gen.coroutine
    def authenticate(self, *args):
        raise NotImplementedError()


class RemoteUserLocalAuthenticator(LocalAuthenticator):
    """
    Accept the authenticated user name from the REMOTE_USER HTTP header.
    Derived from LocalAuthenticator for use of features such as adding
    local accounts through the admin interface.
    """
    header_name = Unicode(
        default_value='X-Forwarded-User',
        config=True,
        help="""HTTP header to inspect for the authenticated username.""")

    def get_handlers(self, app):
        return [
            (r'/login', RemoteUserLoginHandler),
        ]

    @gen.coroutine
    def authenticate(self, *args):
        raise NotImplementedError()


c.JupyterHub.authenticator_class = RemoteUserAuthenticator
#c.RemoteUserAuthenticator.header_name = 'X_FORWARDED_USER'
