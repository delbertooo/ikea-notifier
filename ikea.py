import scrapy
import smtplib, ssl
import os
import re
import datetime as dt
import pickle

known_file = os.getenv('KNOWN_FILE', 'known.pkl')

def item_url(item):
    return f'https://www.ikea.com/de/de/p/{item}/'

def set_known(item):
    known = {}
    now = dt.datetime.now()
    if os.path.exists(known_file):
        with open(known_file, 'rb') as f:
            known = pickle.load(f)
            known = {k:v for (k,v) in known.items() if (now-v).total_seconds() <= int(os.getenv('IGNORE_FOR_SECONDS', 60))}
    already_known = item in known
    if not already_known:
        known[item] = now
    with open(known_file, 'wb+') as f:
        pickle.dump(known, f)
    return already_known

def send_mail(item, availability):
    message = """
From: {from_address}
To: {to_addresses}
Subject: Gegenstand {item} ist jetzt {availability}

Der Gegenstand {item} ist jetzt {availability}:
{url}
    """
    from_address = os.getenv('MAIL_FROM')
    to_addresses = os.getenv('MAIL_TO').split(',')
    mail = message.format(
        item=item, 
        availability=availability, 
        from_address=from_address,
        to_addresses=', '.join(to_addresses),
        url=item_url(item),
    ).strip()
    print(mail)
    if os.getenv('DRY_RUN') == 'True':
        return
    host = os.getenv('MAIL_HOST')
    port = int(os.getenv('MAIL_PORT', 465))

    username = os.getenv('MAIL_USER')
    password = os.getenv('MAIL_PASS')

    context = ssl.create_default_context()
    #with smtplib.SMTP_SSL(host, port, context=context) as server:
    with smtplib.SMTP(host, port) as server:
        server.starttls(context=context) # Secure the connection
        server.login(username, password)
        server.sendmail(
            from_address,
            to_addresses,
            mail,
        )

slugs = os.getenv('SLUGS').split(':')

#SLUGS=hemnes-schuhschrank-2fach-weiss-20169559:voxtorp-schubladenfront-dunkelgrau-90454100:hemnes-kommode-mit-6-schubladen-weiss-20374277

class IkeaSpider(scrapy.Spider):
    name = 'ikeaspider'
    start_urls = [item_url(x) for x in slugs]

    def parse(self, response):
        url = response.request.url
        item = re.search('/([^/]+)/$', url).group(1)
        stocks = response.css('.range-revamp-stockcheck__text')
        text = stocks[0].css('::text').get() if stocks else None
        if text and text != 'Kann nicht geliefert werden':
            if not set_known(item):
                send_mail(item ,text)
            yield {'text': text}
