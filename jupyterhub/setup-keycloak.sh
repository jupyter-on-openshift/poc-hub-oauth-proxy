#!/bin/bash

set -x
set -eo pipefail

SOURCE=`dirname $0`
TARGET=${1:-/opt/keycloak}

mkdir -p $TARGET

cp $SOURCE/keycloak-realm.json $TARGET 
cp $SOURCE/start-keycloak.sh $TARGET
