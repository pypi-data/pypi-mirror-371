#!/usr/bin/env bash
cd $(dirname $(realpath $0))
exec crossplane render --extra-resources extra.yaml xr.yaml composition.yaml functions.yaml
