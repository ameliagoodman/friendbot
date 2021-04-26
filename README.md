# friendbot
bots ❤️ friends

Friendbot will ask every monday if you have time for a 30 min coffee chat with a random friend. On tuesday, friendbot will send out matches! 

Feel free to add this bot to your slack workspace! i used a heroku server, heroku redis free add-on, and set the heroku scheduler free add-on to run `curl https://friendbot1000.herokuapp.com/make-friends` and `curl https://friendbot1000.herokuapp.com/make-matches` every day at 5pm utc (9am pst).
You can see in the /make-friends and /make-matches handlers, they'll only run on monday and tuesday respectively.

### you'll need to set some environment variables:
- giphy api key, set as `GIPHY` 
- a friendbot channel in your slack workspace, set as `FRIENDBOT_CHANNEL`
- your free heroku redis add-on, set as `REDIS_TLS_URL` and `REDIS_URL`
