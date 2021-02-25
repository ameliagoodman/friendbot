import os
from datetime import date
import time
import json
import requests
import random
import schedule
import time
import redis
from flask import Flask, request
app = Flask(__name__)

@app.route('/make-friends', methods=['GET', 'POST'])
def monday():
    if date.today().weekday() == 0:
        r = redis.from_url(os.getenv("REDIS_URL"))
        r.delete('enrolled')
        print("it's game time!!!")
        slack_payload = { "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Hi @channel friends! Do you have time for a 30 minute chat with a friend this week? Let me know soon, matches will be made in 1 hour :time:"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Sure do! 🥰",
                                "emoji": True
                            },
                            "value": "yes",
                            "style": "primary",
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Too busy ❌",
                                "emoji": True
                            },
                            "style": "danger",
                            "value": "no"
                        }
                    ]
                }
            ]
        }
        FRIENDBOT_CHANNEL =  os.getenv("FRIENDBOT_CHANNEL")
        resp = requests.post(FRIENDBOT_CHANNEL, json=slack_payload)
        print("send init msg response: %s" % resp.status_code)
    return 'Hello, Bot!'

@app.route('/enroll', methods=['GET', 'POST'])
def enroll():
    r = redis.from_url(os.getenv("REDIS_URL"))
    form = request.form.to_dict()['payload']
    data = json.loads(form)
    username = data['user']['username']

    if data['actions'][0]['value'] == 'yes':
        r.sadd('enrolled', username)
        send_back = {"text": "Great! You'll be matched shortly."}
        print("confirmed: " + username)
    else:
        r.srem('enrolled', username)
        send_back = {"text": "No worries. I'll check back in next week 🥰"}
        print("rejected: " + data['user']['username'])

    send_back['response_type'] = "ephemeral"
    send_back['replace_original'] = False
    resp = requests.post(data['response_url'], json=send_back)
    
    print("send ack response code: %s" % resp.status_code)
    return 'enrolled'

emojis = [":star_cat: :sunglassesdog:", ":starspin: :rainbow2:", ":heart_face: :heart_eyes_cat:", ":cow: :cowboy:",":garfield_sunglasses: :odie:", ":leftshark-401: :dancingpenguin:"]

@app.route('/make-matches', methods=['GET', 'POST'])
def matchmaker():
    r = redis.from_url(os.getenv("REDIS_URL"))
    match_bbs = r.smembers('enrolled')
    print("Make matches for:")
    print(match_bbs)
    random_match_bbs = list(match_bbs)
    print("randomized list:")
    print(random_match_bbs)
    random.shuffle(random_match_bbs)
    random.shuffle(emojis)
    matches = []
    new_match = set()
    
    for bb in random_match_bbs:
        new_match.add(bb)
        if len(new_match) == 2:
            matches.append(new_match)
            new_match = set()
    else:
        if len(new_match) > 0 and len(matches) > 0:
            matches[0] = matches[0].union(new_match)
    
    match_msg = ""
    count = 0
    for match in matches:
        if len(match) > 2 :
            match_str = ":partygritty: :partytanuki: :partycat:"
        else:
            match_str = emojis[count]
        for username in match:
            match_str = match_str + "@" + username.decode("utf-8") + " +  "
        match_msg = match_msg + match_str[:len(match_str) - 3] + "\n"
        count += 1

    print("Matches made!\n" + match_msg)
    gif = get_gif()
    send_matches = { "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "This week's matches 🥳 🥰",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": match_msg,
                },
                "accessory": {
                    "type": "image",
                    "image_url": gif,
                    "alt_text": "friendship gif"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "Lucky you! A new friend! Please reach out to coordinate a time that works for you both by the end of the week. Next week you'll get a new friend",
                    "emoji": True
                }
            }
        ]
    }

    FRIENDBOT_CHANNEL =  os.getenv("FRIENDBOT_CHANNEL")
    resp = requests.post(FRIENDBOT_CHANNEL, json=send_matches)
    print("response code: %s" % resp.status_code)
    return "matches made"     


def get_gif():
    API_KEY =  os.getenv("GIPHY")
    giphy_payload = {'api_key': API_KEY, 'q': 'friendship', 'limit': 1, 'rating': 'g'}
    giphy_request = requests.get('http://api.giphy.com/v1/gifs/search', params=giphy_payload)
    giphy_response = giphy_request.json()
    default_friends = "https://media3.giphy.com/media/VduFvPwm3gfGO8duNN/giphy.gif?cid=5a8f66bf52o5um5m3qd90itix0abmmeuhi6fobomohduslx3&rid=giphy.gif"
    try:
        gif_URL = giphy_response.get('data', default_friends)[0].get('images', default_friends).get('downsized', default_friends).get('url', default_friends)
    except AttributeError:
        gif_URL = default_friends
    return gif_URL  


@app.route('/')
def main():
    return "Hello, friendbot!"

if __name__ == "__main__":
    main()