from flask import Flask, render_template
import feedparser



app = Flask(__name__)

RSS_FEEDS = {'google': 'https://news.google.com/rss?gl=US&ned=us&hl=en',
             'cnn': 'http://rss.cnn.com/rss/cnn_topstories.rss',
             'bbc': 'http://feeds.bbci.co.uk/news/rss.xml'}


@app.route('/')
@app.route('/<publication>')
def get_news(publication='bbc') -> 'html':
    feed = feedparser.parse(RSS_FEEDS[publication])
    return render_template("home.html",articles=feed['entries'])


if __name__ == '__main__':
    app.run()
