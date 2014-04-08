import json
import logging
import os

import tornado.ioloop
import tornado.web
import tornado.httpclient

import tweetstream

stream = tweetstream.TweetStream({
    "twitter_consumer_key": os.environ["TWITTER_CONSUMER_KEY"],
    "twitter_consumer_secret": os.environ["TWITTER_CONSUMER_SECRET"],
    "twitter_access_token": os.environ["TWITTER_ACCESS_TOKEN"],
    "twitter_access_token_secret": os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
})

def tweetstream_callback(webhook_url, tweet):
    http_client = tornado.httpclient.AsyncHTTPClient()
    req = tornado.httpclient.HTTPRequest(
        webhook_url,
        method='POST',
        headers={'content-type': 'application/json'},
        body=json.dumps(tweet)
    )
    return http_client.fetch(req)

class FetchHandler(tornado.web.RequestHandler):
    def post(self):
        global webhook_url
        data = json.loads(self.request.body)
        webhook_url = data['webhook_url']

        stream.fetch(
            data['stream_url'],
            callback=lambda tweet: tweetstream_callback(webhook_url, tweet)
        )

application = tornado.web.Application([
    (r"/fetch", FetchHandler),
])

if __name__ == "__main__":
    application.listen(os.environ['PORT'])
    tornado.ioloop.IOLoop.instance().start()