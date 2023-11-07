from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword, ReloginAttemptExceeded, ChallengeRequired,
    SelectContactPointRecoveryForm, RecaptchaChallengeForm,
    FeedbackRequired, PleaseWaitFewMinutes, LoginRequired
)
from datetime import datetime, tzinfo, date, timezone
import time
#import calendar
import pytz

import random
import os
import pathlib
import urllib
import urllib.request

import json

### my classes
import classes.errors

from classes.botconf import botConf
from classes.botconf import loadConf
from classes.botconf import loadCoolDownValues
from classes.init import initDirs
from classes.init import cleanFiles
from classes.stats import printStats
from classes.feed import gefFromFeed
from classes.getfromhashtag import getFromHashtag
from classes.cooldown import coolDownCheck
from classes.cooldown import coolDownCheckDay
from classes.cooldown import coolDownCheckHour
from classes.createdevice import newUser
from classes.unfollowusers import unfollowUsers
from classes.newfollowers import getNewFollowers

import argparse

# Arguments and help
parser = argparse.ArgumentParser(description="Human Being simulator using Instagram, to get follows back")
subparsers = parser.add_subparsers(dest='command')
createUser = subparsers.add_parser('new', help="Create new user dir and config files")
noInput = subparsers.add_parser('user', help="To run application without the need of providing input. Provide direcly the username",)
noInput.add_argument("user", help="provide the desired username", type=str)
args = parser.parse_args()

if args.command == "new":
	print()
	print("++ A new directory will be created under ./conf/$(USERNAME)/ with ")
	print("++ all the needed configurations for new user")
	print()
	u = str(input(">> New Username: "))
	p = str(input(">> New Password: "))
	print ()
	print ()
	print ("++ Insert all tags of interest, separated by a ';'. Ie, ")
	print ("++ dog;puppy;puppies;dogs;dogslover;puppylover;puppy35")
	print ("++ Just alfanumeric chars are accepted ")
	t = str(input(">> Tags: "))
	newUser(u, p, t) #create new user, in classes/createdevice
	quit()

# Intro
print("##########################################################################")
print("########################                          ########################")
print("########################       Instabot.py        ########################")
print("########################  by Daniele Rugginenti   ########################")
print("########################                          ########################")
print("########################         v 0.0.2          ########################")
print("########################         2023/11          ########################")
print("########################                          ########################")
print("##########################################################################")

# launch the client for instagrapi 
cl=Client() 
user = None

# Select user
if args.command == "user" and getattr(args, 'user', None):
	user = args.user
else:

	try:
		users=next(os.walk("conf"))[1] # check conf dirs
	except: 
		print()
		print(">>> Conf dir does not exists, read the help")
		print(">>> exec: python instabot --help")
		quit()


	i=1
	for user in users:
		print (str(i)+" > "+user)
		i+=1

	position = -1
	while position<=0 or position>len(users):
		position = int(input("Chose user: "))

	### GLOBAL VARS
	user = users[position-1]	

conf = loadConf(user, cl)
botConf = botConf(conf)
coolDownMaxValues = loadCoolDownValues(conf)

username = conf["username"]
password = conf["password"]
tags = conf["tags"].split(";")
confdir = conf["confdir"]

#### INIT
initDirs()
cleanFiles(conf)

### check instagrapi conf file 
f=pathlib.Path(confdir+"login.json")
if not f.exists():
	print("File login not found")
	quit()

# LOGIN
cl.load_settings(confdir+"login.json")

print (" >>>>>> Login <<<<<< ")

print (botConf.getConf())

cl.login(username, password)
print(" Logged in.. saving settings");
cl.dump_settings(confdir+"login.json")

printStats(conf)

print(" >>>>>> Begin <<<<<< ")

execution_counter=1


while 1:
	# Today in UTC
	cooldown_day_ts=conf["cooldown_day"]["curr"]
	today_ts=time.mktime(time.strptime(str(datetime.now(timezone.utc)).split(" ")[0], '%Y-%m-%d'))
	if (today_ts > cooldown_day_ts):
		## Reset daily counters
		print("Resetting Daily counters ")
		botConf.resetTodayConf(today_ts)

	### This hour in UTC
	hour_ts=time.mktime(time.strptime(str(datetime.now(timezone.utc)).split(":")[0], '%Y-%m-%d %H'))
	cooldown_hour_ts=conf["cooldown_hour"]["curr"]
	if (hour_ts > cooldown_hour_ts):
		botConf.resetHourConf(hour_ts)

	print("****************************************** ")
	print("#### Execution # "+str(execution_counter))
	
	if not coolDownCheckDay(conf, coolDownMaxValues):
		print("Cool Down Values Reached for the day, no go, sleep 4 hours")
		time.sleep(7200)
		continue

	if not coolDownCheckHour(conf, coolDownMaxValues):
		print("Cool Down Values Reached for the Hour, no go, sleep 10 minutes")
		time.sleep(600)
		continue


	getNewFollowers(conf)

	#########
	# FEED
	# print(" Getting my feed")

	r1=random.randint(0,10)
	# if r1<6:
	# 	print(" ++ Getting my feed")
	# 	gefFromFeed(conf)
	# 	s=random.uniform(.5,5)
	# 	time.sleep(s)

	if r1<3:
		unfollowUsers(conf)

	#########
	# HASTAGS
	getFromHashtag(conf)

	
	
	printStats(conf)
	
	#########
	# SLEEP
	r1=random.randint(0,100)
	if r1<10:
		r=random.randint(3600,14400) #night every ~10 exec
	elif r1<20:
		r=random.randint(600, 3600)
	elif r1<50:
		r=random.randint(60,360)
	else:
		r=random.randint(10,60)

	print("#### End Execution # "+str(execution_counter))
	execution_counter += 1
	print("Sleeping "+str(r)+" seconds")
	print("****************************************** ")
	time.sleep(r)
