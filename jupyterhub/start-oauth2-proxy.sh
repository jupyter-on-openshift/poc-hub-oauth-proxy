#!/bin/bash

set -x

. `dirname $0`/oauth2-proxy-envvars.sh

exec oauth2_proxy \
  --upstream=$UPSTREAM_URL \
  --http-address=0.0.0.0:8080 \
  --email-domain=* \
  -provider=oidc \
  -skip-provider-button \
  -redirect-url=$REDIRECT_URL \
  -oidc-issuer-url=$OIDC_ISSUER_URL \
  -ssl-insecure-skip-verify \
  -cookie-secure=false
