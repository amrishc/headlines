from flask import Flask, render_template, request, make_response
import json, urllib.request, urllib.error
import feedparser
import datetime

DEFAULTS = {'publication': 'iol',
            'city': 'London,UK',
            'currency_from': 'GBP',
            'current_to': 'USD'
            }

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=fc21e6c8692dc2065add7cb7b4b414de"
CURRENCY_URL = "https://openexchangerates.org/api/latest.json?app_id=461dd3f3715c43b785dffc47832216cd"
app = Flask(__name__)

RSS_FEEDS = {'google': 'https://news.google.com/rss?gl=US&ned=us&hl=en',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
             'iol': 'http://www.iol.co.za/cmlink/1.640'}


@app.route('/')
def home():
    # Get Customized headlines, based on user input or default
    publication = request.args.get('publication')
    publication = get_value_with_fallback('publication')
    articles = get_news(publication)

    city = get_value_with_fallback('city')

    weather = get_weather(city)

    currency_from = get_value_with_fallback('currency_from')
    currency_to = get_value_with_fallback('currency_to')

    (rate, currencies) = get_rate(currency_from, currency_to)

    response = make_response(render_template('home.html',
                                             articles=articles,
                                             weather=weather,
                                             currency_from=currency_from,
                                             currency_to=currency_to,
                                             rate=rate,
                                             currencies=sorted(currencies)
                                             ))

    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)

    return response


def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]


def get_news(publication):
    if not publication or publication.lower() not in RSS_FEEDS:
        publication = DEFAULTS['publication']
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']


def get_weather(city):
    url = WEATHER_URL.format(city)
    data = urllib.request.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {"description": parsed["weather"][0]["description"],
                   'temperature': parsed["main"]["temp"],
                   'city': parsed["name"],
                   'country': parsed['sys']['country']
                   }
    return weather


def get_rate(frm, to):
    all_currency = urllib.request.urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return to_rate / frm_rate, parsed.keys()


if __name__ == '__main__':
    app.run()
