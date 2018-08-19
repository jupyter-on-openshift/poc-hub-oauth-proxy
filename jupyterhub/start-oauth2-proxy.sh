#!/bin/bash

set -x

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

exec oauth2_proxy \
  --upstream=http://$JUPYTERHUB_SERVICE_NAME:8080/ \
  --http-address=0.0.0.0:8080 \
  --email-domain=* \
  -provider=oidc \
  -skip-provider-button \
  -redirect-url=https://$JUPYTERHUB_HOSTNAME/oauth2/callback \
  -oidc-issuer-url=https://$KEYCLOAK_HOSTNAME/auth/realms/jupyterhub \
  -ssl-insecure-skip-verify \
  -cookie-secure=false
