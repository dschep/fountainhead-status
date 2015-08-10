# Fountainhead MTB Trail Status
This uses Twilio to call the status hotline and transcribe the message and then
host a page showing the result!

## Required Environment Variables
 * TWILIO_ACCOUNT_SID - your twilio account sid
 * TWILIO_AUTH_TOKEN - your twilio auth token
 * TWILIO_FROM - the from phone number, should be a number belonging to your twilio account
 * SERVER_URL - the root of where this server lives for the purposes of twilio callbacks
 * SQLALCHEMY_DATABASE_URI - the database url (for SqlAlchemy)
 * FACEBOOK_ACCESS_TOKEN - Facebook access token

## Run locally (REQUIRES DOCKER)
Run `docker-compose up`

## Deploy to server (ansible, docker/nginx on server)
Edit the vars in `ansible/deploy.yml` to your liking and deploy with
`ansible-playbook deploy.yml -i yourserver.com, -K`
