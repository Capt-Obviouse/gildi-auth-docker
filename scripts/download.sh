#!/bin/bash
git clone https://gitlab.com/allianceauth/allianceauth.git aa-git
cp -R aa-git/docker ./aa-docker
chmod +x aa-docker/conf/memory_check.sh
chmod +x aa-docker/conf/redis_healthcheck.sh
rm -rf aa-git
