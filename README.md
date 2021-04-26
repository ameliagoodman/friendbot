# friendbot
bots ❤️ friends

Friendbot will ask every monday if you have time for a 30 min coffee chat with a random friend. On tuesday, friendbot will send out matches! 
Feel free to add this bot to your slack workspace! i used a heroku server, and set the free heroku scheduler add-on to run `curl https://friendbot1000.herokuapp.com/make-friends` and `curl https://friendbot1000.herokuapp.com/make-matches` every day at 5pm utc (9am pst).
You can see in the /make-friends and /make-matches handlers, they'll only run on monday and tuesday respectively.

