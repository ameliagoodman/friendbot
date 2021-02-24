import os
from datetime import date
import time
import json
import requests
import random
import schedule
import time
from flask import Flask, request
app = Flask(__name__)

match_bbs = set()

@app.route('/make-friends', methods=['GET', 'POST'])
def monday():
    match_bbs.clear()
    slack_payload = { "blocks": [
		    {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hi friends! Do you have time for a 30 minute chat with a friend this week? Let me know soon, matches will be made in 1 hour :time:"
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
    # requests.post(FRIENDBOT_CHANNEL, json=slack_payload)
    return 'Hello, Bot!'

@app.route('/enroll', methods=['GET', 'POST'])
def enroll():
    form = request.form.to_dict()['payload']
    data = json.loads(form)
    if data['actions'][0]['value'] == 'yes':
        match_bbs.add(data['user']['username'])
        send_back = {"text": "Great! You'll be matched shortly."}
        print("confirmed: " + data['user']['username'])
    else:
        if data['user']['username'] in match_bbs:
            match_bbs.remove(data['user']['username'])
        print("rejected: " + data['user']['username'])
        send_back = {"text": "No worries. I'll check back in next week 🥰"}
    send_back['response_type'] = "ephemeral"
    r = requests.post(data['response_url'], json=send_back)
    print(r.status_code)
    return 'enrolled'

emojis = [":star_cat: :sunglassesdog:", ":starspin: :rainbow2:", ":heart_face: :heart_eyes_cat:", ":cow: :cowboy:",":garfield_sunglasses: :odie:", ":leftshark-401: :dancingpenguin:"]

@app.route('/make-matches', methods=['GET', 'POST'])
def matchmaker():
    random_match_bbs = list(match_bbs)
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
            match_str = match_str + "@" + username + " +  "
        match_msg = match_msg + match_str[:len(match_str) - 3] + "\n"
        count += 1

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
    # requests.post(FRIENDBOT_CHANNEL, json=send_matches)
    return "matches made"     


def get_gif():
    API_KEY =  os.getenv("GIPHY")
    giphy_payload = {'api_key': API_KEY, 'q': 'friendship', 'limit': 1, 'rating': 'g'}
    giphy_request = requests.get('http://api.giphy.com/v1/gifs/search', params=giphy_payload)
    giphy_response = giphy_request.json()
    gif_URL = giphy_response.get('data', ['https://giphy.com/gifs/pokemon-friendship-high-five-10LKovKon8DENq'])[0].get('images', 'https://giphy.com/gifs/pokemon-friendship-high-five-10LKovKon8DENq').get('downsized', 'https://giphy.com/gifs/pokemon-friendship-high-five-10LKovKon8DENq').get('url', 'https://giphy.com/gifs/pokemon-friendship-high-five-10LKovKon8DENq')
    return gif_URL


@app.route('/')
def main():
    print("IN MAIN")
    if date.today().weekday() == 1:
        print('its tues!!!')
        monday()
        print('boutta sleep')
        time.sleep(5)
        print('nah jk im up')
        matchmaker()
    
    return "Hello, friendbot!"