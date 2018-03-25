#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from requests_oauthlib import OAuth1Session
# from consts import *
# Imports the Google Cloud client library
from google.cloud import translate
import os
import json
import datetime
from time import sleep
import feedparser
from stripHTML import MyHtmlStripper
import pytz
JST = pytz.timezone('Asia/Tokyo')
WORK_FILE_PATH = '/home/ec2-user/workspace/work/'

# RSS取得先、Webhook投稿先
feedServices = {
    "CoinDesk":{"rss":"https://www.coindesk.com/feed/", "icon":"https://media.coindesk.com/uploads/2017/05/cropped-coindesk-new-favicon-192x192.png", "needTranslation": True, "webhook":"https://discordapp.com/api/webhooks/0000000000000000000/hogefuga/slack"},
    "CoinTelegraph":{"rss":"https://cointelegraph.com/rss", "icon":"https://cointelegraph.com/favicon-32x32.png?v1", "needTranslation": True, "webhook":"https://discordapp.com/api/webhooks/0000000000000000000/hogefuga/slack"}
}

def main():
    for feedName in feedServices:
        feedUrl = feedServices[feedName]["rss"]
        webhookUrl = feedServices[feedName]["webhook"]
        needTranslation = feedServices[feedName]["needTranslation"]
        icon = feedServices[feedName]["icon"]

        lastPublished = readLastPublished(feedName)
        lastPublishedDateTime = parsePublished(lastPublished)
        filterDateTime = lastPublishedDateTime

        d = feedparser.parse(feedUrl)

        for entry in d['entries']:
            publishedDateTime = parsePublished(entry.published)
            if filterDateTime < publishedDateTime:
                postToDiscord(webhookUrl, feedName, icon, entry.title, MyHtmlStripper(entry.summary).value, entry.link, entry.published, needTranslation)
                sleep(5)
            if lastPublishedDateTime < publishedDateTime:
                lastPublished = entry.published
                lastPublishedDateTime = publishedDateTime
        
        # 最新の記事投稿日時を保持
        writeLastPublished(feedName, lastPublished)
            
def translateByAPI(text):
    # Instantiates a client
    translate_client = translate.Client()
    
    # The target language
    target = 'ja'
    
    # Translates some text
    translation = translate_client.translate(
        text,
        target_language=target)
    
    return translation['translatedText']


def readLastPublished(feedName):
    filePath = WORK_FILE_PATH + getLastPublishedFileName(feedName)
    if not os.path.exists(filePath):
        return "Mon, 05 Mar 2018 13:00:00 +0000"
    file = open(filePath, 'r')  #ファイルをオープン
    lastPublished = file.read()
    file.close()              #ファイルをクローズ
    return lastPublished
    
def writeLastPublished(feedName, lastPublished):
    filePath = WORK_FILE_PATH + getLastPublishedFileName(feedName)
    file = open(filePath, 'w')  #ファイルをオープン
    print ("write:" + lastPublished)
    file.write(lastPublished)
    file.close()              #ファイルをクローズ
    
def getLastPublishedFileName(feedName):
    return "{name}_since_for_pickup_feed.txt".format(name=feedName)
    
def asLocalize(createdAt):
    return datetime.datetime.strptime(createdAt, "%a, %d %b %Y %H:%M:%S %z").astimezone(JST).strftime('%Y/%m/%d %H:%M:%S')

def parsePublished(published):
    return datetime.datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %z")

def postToDiscord(webhookUrl, feedName, icon, title, summary, link, published, needTranslation):
    originalParam = json.dumps(getOriginalTemplate(link))
    translatedTitle = ""
    translatedSummary = ""
    if needTranslation:
        translatedTitle = translateByAPI(title)
        translatedSummary = translateByAPI(summary)
    param = json.dumps(getJsonTemplate(feedName, icon, title, summary, translatedTitle, translatedSummary, published, link, needTranslation))

    #メンション投稿
    #slack形式だとメンションが効かないのでメンションのみ別途投稿
    response = requests.post(
    webhookUrl[0:-6], # /slack部分を取り除く
    originalParam,
    headers={'Content-Type': 'application/json'})

    #本文投稿
    response = requests.post(
    webhookUrl,
    param,
    headers={'Content-Type': 'application/json'})

def getJsonTemplate(feedName, icon, title, body, translatedTitle, translatedBody, published, link, needTranslation):
    if needTranslation:
        return {
            "attachments": [
                {
                    "color": "#36a64f",
                    "author_name": feedName,
                    "author_icon": icon,
                    "author_link": link,
                    "fields": [
                        # {
                        #     "title": title,
                        #     "value": body,
                        #     "short": "false"
                        # },
        				{
        					"title": translatedTitle,
        					"value": translatedBody,
        					"short": "false"
        				}
                    ],
                    "footer": asLocalize(published)
                }
            ]
        }
    else:
        return {
            "attachments": [
                {
                    "color": "#36a64f",
                    "author_name": feedName,
                    "author_icon": icon,
                    "author_link": link,
                    "fields": [
                        {
                            "title": title,
                            "value": body,
                            "short": "false"
                        }
                    ],
                    "footer": asLocalize(published)
                }
            ]
        }


def getOriginalTemplate(url):
    return {
        "content" : "----------------------------------------------------\n" + url
    }

if __name__== '__main__':
    main()

