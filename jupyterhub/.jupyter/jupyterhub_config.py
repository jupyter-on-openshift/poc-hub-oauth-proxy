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

# User access. Trust header sent by the proxy. This along isn't
# safe, however oauth2_proxy with Keycloak generates cookies which
# are too large when passing of access token is enabled.

c.JupyterHub.authenticator_class = 'jhub_remote_user_authenticator.remote_user_auth.RemoteUserAuthenticator'
c.RemoteUserAuthenticator.header_name = 'X-Forwarded-User'

# Configure KeyCloak as authentication provider.

from openshift import client, config

with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace') as fp:
    namespace = fp.read().strip()

config.load_incluster_config()
oapi = client.OapiApi()

routes = oapi.list_namespaced_route(namespace)

def extract_hostname(routes, name):
    for route in routes.items:
        if route.metadata.name == name:
            return route.spec.host

jupyterhub_name = os.environ.get('JUPYTERHUB_SERVICE_NAME')
jupyterhub_hostname = extract_hostname(routes, jupyterhub_name)
print('jupyterhub_hostname', jupyterhub_hostname)

keycloak_name = os.environ.get('KEYCLOAK_SERVICE_NAME')
keycloak_hostname = extract_hostname(routes, keycloak_name)
print('keycloak_hostname', keycloak_hostname)

keycloak_realm = os.environ.get('KEYCLOAK_REALM')

keycloak_account_url = 'https://%s/auth/realms/%s/account' % (
	keycloak_hostname, keycloak_realm)

with open('templates/vars.html', 'w') as fp:
    fp.write('{%% set keycloak_account_url = "%s" %%}' % keycloak_account_url)

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
