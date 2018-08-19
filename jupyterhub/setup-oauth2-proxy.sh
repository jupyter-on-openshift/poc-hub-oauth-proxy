#!/bin/bash

set -x
set -eo pipefail

SOURCE=`dirname $0`
TARGET=${1:-/opt/oauth2-proxy}

mkdir -p $TARGET

cp $SOURCE/start-oauth2-proxy.sh $TARGET
