# FindMySteve

This is a stupid little Fly.io app/Python slackbot that let's folks see what city and country i'm in.

The Fly app runs everything in a single machine (pretty much. There's a separate database). Should these all be separate? Yes, probably. 

## How does it work?

The app runs an Owntracks server, specifically https://github.com/hrshadhin/ot-recorder. 
It let's you run any Owntracks clients and stores the results in a database. Postgres in this case. 
The slackbot is a python script that uses the `slack_bolt` library to run a simple slackbot that listens for the phrase "Where is steve?"
Then it queries for the last location in the database, does some google API stuff to take that very precise location, find the city/region.country (whichever is most accurate), and return that with a little map of the area and the current time.

## How do I run it?

You need a bunch of things, and I'll probably forget some of them.

These are the Fly.io secrets that need to be set (or just env vars if you're not running on Fly.io)

*GOOGLE_API_KEY*
> You need some google api keys with the right permissions for the map apis.

*SLACK_APP_TOKEN*
> You need this (again with a bunch of permissions) to do slack communication for the bot

*SLACK_BOT_TOKEN*
> I still haven't quite figured out why you need two slack tokens. They do different things, sure, but it's all a bit confusing and I bet they could have made it more simple. 
> I spent way too long figuring out the buttons i needed to press to get the permissions right.

I'll document this better if anyone is interested...

Copy the `config.yml.example` to `config.yml` and make the database details correct for your setup.
Create an `htpasswd` file with a username and (encrypted) password. This will be your auth for the OwnTracks api.

Deploy to fly.

Once all of this is setup, you need to install OwnTracks on your phone. Should be available in the app store for your device. Configure the app so that the url is your apps url and the user and password are correct. 
You also probably need to edit the python script so that it has a different name from 'steve'. 

I'm sure there are things i'm forgetting. Feel free to harrass me if you really want to make this work for yourself and can't work out the details.
