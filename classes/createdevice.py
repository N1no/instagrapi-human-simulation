from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword, ReloginAttemptExceeded, ChallengeRequired,
    SelectContactPointRecoveryForm, RecaptchaChallengeForm,
    FeedbackRequired, PleaseWaitFewMinutes, LoginRequired
)
import pathlib
import random
import time
import urllib
import urllib.request
import os
import json

cl = Client()


def newUser(u, p, t):
	if not os.path.exists('conf'):
		os.mkdir('conf')

	confdir="conf/"+u+"/"
	if not os.path.exists(confdir):
		os.mkdir(confdir);

	#### instagrapi file
	file = pathlib.Path(confdir+"login.json");
	if file.exists ():
		cl.load_settings(confdir+"login.json")
	else:
		cl.dump_settings(confdir+"login.json")

	#### bot user config
	file = pathlib.Path(confdir+"conf.json");
	conf = {"username": u, "password": p, "tags": t, "cooldown_day": {"curr": 0, "follows": 0, "likes": 0, "unfollows": 0}, "cooldown_hour": {"curr": 0, "follows": 0, "likes": 0, "unfollows": 0}, "scripts_followers":0, "forced_words":"", "messages": {"active": 1, "texts":{"en": "Hi Thanks for the follow! How are you?", "es": "Gracias por el follow! \nComo estás?", "it": "Piacere, \ngrazie per il follow!"} } }
	with open(confdir+"conf.json", 'w') as fp:
			json.dump(conf, fp, indent=4)

	file = pathlib.Path(confdir+"cool_down_conf.json");
	conf = {"day_max_follows": 30, "day_max_likes": 80, "day_max_unfollows": 50, "hour_max_follows": 6, "hour_max_likes": 15, "hour_max_unfollows": 10 }
	with open(confdir+"cool_down_conf.json", 'w') as fp:
			json.dump(conf, fp, indent=4)

	csv = ["medias.csv", "medias_downloaded.csv", "medias_liked.csv", "medias_seen.csv", "thumbs_downloaded.csv", "followed.csv", "followers.csv", "messages.csv"];
	for f in csv:
		file = pathlib.Path(confdir+f);
		if not file.exists():
			file.touch();

	return

class usersLogin():
    def __init__(self, username, password, tags):
        self.username = username
        self.password = password
        self.tags = tags



