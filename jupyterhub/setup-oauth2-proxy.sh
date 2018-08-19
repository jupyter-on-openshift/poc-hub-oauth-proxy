#!/bin/bash

set -x
set -eo pipefail

SOURCE=`dirname $0`
TARGET=${1:-/opt/oauth2-proxy}

mkdir -p $TARGET

cp $SOURCE/start-oauth2-proxy.sh $TARGET

SERVER="https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT"
TOKEN=`cat /var/run/secrets/kubernetes.io/serviceaccount/token`
NAMESPACE=`cat /var/run/secrets/kubernetes.io/serviceaccount/namespace`

URL="$SERVER/oapi/v1/namespaces/$NAMESPACE/routes/$JUPYTERHUB_SERVICE_NAME"

JUPYTERHUB_HOSTNAME=`curl -s -k -H "Authorization: Bearer $TOKEN" $URL | \
    python -c "import json, sys; \
               data = json.loads(sys.stdin.read()); \
               print(data['spec']['host'])"`

URL="$SERVER/oapi/v1/namespaces/$NAMESPACE/routes/$KEYCLOAK_SERVICE_NAME"

KEYCLOAK_HOSTNAME=`curl -s -k -H "Authorization: Bearer $TOKEN" $URL | \
    python -c "import json, sys; \
               data = json.loads(sys.stdin.read()); \
               print(data['spec']['host'])"`

cat > $TARGET/oauth2-proxy-envvars.sh << EOF
UPSTREAM_URL=http://$JUPYTERHUB_SERVICE_NAME:8080
REDIRECT_URL=https://$JUPYTERHUB_HOSTNAME/oauth2/callback
OIDC_ISSUER_URL=https://$KEYCLOAK_HOSTNAME/auth/realms/jupyterhub
EOF
