#!/usr/bin/env bash
cd $(dirname $(realpath $0))
exec crank render --extra-resources=daemonset.yaml xr.yaml composition.yaml functions.yaml
