Docker Commands:

## Start all containers
docker compose --env-file=.env up -d

## Start single service
docker compose up -d service_name

## Stop all containers
docker compose down

## Upgrading AA
Change the version number in the .env
docker compose pull
docker compose --env-file=.env up -d
docker compose exec allianceauth_gunicorn bash
allianceauth update myauth
auth migrate
auth collectstatic

## Updating packages
