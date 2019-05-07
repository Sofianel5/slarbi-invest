import requests
import urllib.parse
import datetime
import time
from flask import redirect, render_template, request, session
from functools import wraps
import math
from cs50 import SQL
from calendar import monthrange

db = SQL("sqlite:///finance.db")



def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        response = requests.get(f"https://api.iextrading.com/1.0/stock/{urllib.parse.quote_plus(symbol)}/quote")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None

def dictstocks():
    # Contact API
    try:
        response = requests.get("https://api.iextrading.com/1.0/ref-data/symbols")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        json = response.json()
        dic = {}
        i = 0
        while i < len(json):
            if json[i]["isEnabled"]:
                dic[json[i]["name"]] = json[i]["symbol"]
            i += 1
        return dic
    except (KeyError, TypeError, ValueError):
        return None


def lookupMonth(symbol):
    try:
        response = requests.get(f"https://cloud.iexapis.com/beta/stock/{urllib.parse.quote_plus(symbol)}/chart/1m?token=sk_1b9e780a79d7472ea1c7c61172873999")
        response.raise_for_status()
    except requests.RequestException:
        return None
    try:
        month = response.json()
        monthprices = {'prices': [], 'labels': []}
        for day in month:
            monthprices["prices"].append(float(day["close"]))
            monthprices["labels"].append(time.strftime('%a, %b %d', (time.strptime(day["date"], '%Y-%m-%d'))))
        return monthprices
    except (KeyError, TypeError, ValueError):
        print("key/type/value error")
        return None

def lookupYear(symbol):
    try:
        response = requests.get(f"https://cloud.iexapis.com/beta/stock/{urllib.parse.quote_plus(symbol)}/chart/1y?token=sk_1b9e780a79d7472ea1c7c61172873999")
        response.raise_for_status()
    except requests.RequestException:
        return None
    try:
        month = response.json()
        monthprices = {'prices': [], 'labels': []}
        for day in month:
            monthprices["prices"].append(float(day["close"]))
            monthprices["labels"].append(time.strftime('%a, %b %d', (time.strptime(day["date"], '%Y-%m-%d'))))
        return monthprices
    except (KeyError, TypeError, ValueError):
        print("key/type/value error")
        return None
def lookupVar(period, symbol):
    try:
        response = requests.get(f"https://cloud.iexapis.com/beta/stock/{urllib.parse.quote_plus(symbol)}/chart/{period}?token=sk_1b9e780a79d7472ea1c7c61172873999")
        response.raise_for_status()
    except requests.RequestException:
        return None
    try:
        month = response.json()
        monthprices = {'prices': [], 'labels': []}
        for day in month:
            monthprices["prices"].append(float(day["close"]))
            monthprices["labels"].append(time.strftime('%a, %b %d, %Y', (time.strptime(day["date"], '%Y-%m-%d'))))
        return monthprices
    except (KeyError, TypeError, ValueError):
        print("key/type/value error")
        return None
def lookupMax(symbol):
    try:
        response = requests.get(f"https://cloud.iexapis.com/beta/stock/{urllib.parse.quote_plus(symbol)}/chart/max?token=sk_1b9e780a79d7472ea1c7c61172873999")
        response.raise_for_status()
    except requests.RequestException:
        return None
    try:
        month = response.json()
        monthprices = {'prices': [], 'labels': []}
        for day in month:
            monthprices["prices"].append(float(day["close"]))
            monthprices["labels"].append(time.strftime('%a, %b %d', (time.strptime(day["date"], '%Y-%m-%d'))))
        return monthprices
    except (KeyError, TypeError, ValueError):
        print("key/type/value error")
        return None

#def testvalues(period)

def lookupweek(symbol):
    if datetime.datetime.today().weekday() < 5:
        day0 = datetime.datetime.today()
    else:
        day0 = datetime.datetime.today()
        shift = day0.weekday() - 4
        day0 = day0 - datetime.timedelta(days = shift)

    day1 = day0 - datetime.timedelta(days = 1)
    if day1.weekday() > 4:
        shift = day1.weekday() - 4
        day1 = day1 - datetime.timedelta(days = shift)
    day2 = day1 - datetime.timedelta(days = 1)
    if day2.weekday() > 4:
        shift = day2.weekday() - 4
        day2 = day2 - datetime.timedelta(days = shift)
    day3 = day2 - datetime.timedelta(days = 1)
    if day3.weekday() > 4:
        shift = day3.weekday() - 4
        day3 = day3 - datetime.timedelta(days = shift)
    day4 = day3 - datetime.timedelta(days = 1)
    if day4.weekday() > 4:
        shift = day4.weekday() - 4
        day4 = day4 - datetime.timedelta(days = shift)
    day5 = day4 - datetime.timedelta(days = 1)
    if day5.weekday() > 4:
        shift = day5.weekday() - 4
        day5 = day5 - datetime.timedelta(days = shift)
    day6 = day5 - datetime.timedelta(days = 1)
    if day6.weekday() > 4:
        shift = day6.weekday() - 4
        day6 = day6 - datetime.timedelta(days = shift)
    day0 = day0.strftime('%Y%m%d')
    day1 = day1.strftime('%Y%m%d')
    day2 = day2.strftime('%Y%m%d')
    day3 = day3.strftime('%Y%m%d')
    day4 = day4.strftime('%Y%m%d')
    day5 = day5.strftime('%Y%m%d')
    day6 = day6.strftime('%Y%m%d')
    try:
        response0 = requests.get(f"https://cloud.iexapis.com/beta/stock/{urllib.parse.quote_plus(symbol)}/chart/date/{day0}?token=sk_1b9e780a79d7472ea1c7c61172873999")
        #response0 = requests.get(f"https://api.iextrading.com/1.0/stock/{urllib.parse.quote_plus(symbol)}/chart/date/{day0}")
        response0.raise_for_status()
    except requests.RequestException:
        print("failure0")
        return None
    try:
        response1 = requests.get(f"https://cloud.iexapis.com/beta/stock/{urllib.parse.quote_plus(symbol)}/chart/date/{day1}?token=sk_1b9e780a79d7472ea1c7c61172873999")
        #response1 = requests.get(f"https://api.iextrading.com/1.0/stock/{urllib.parse.quote_plus(symbol)}/chart/date/{day1}")
        response1.raise_for_status()
    except requests.RequestException:
        print("failure1")
        return None
    try:
        response2 = requests.get(f"https://cloud.iexapis.com/beta/stock/{urllib.parse.quote_plus(symbol)}/chart/date/{day2}?token=sk_1b9e780a79d7472ea1c7c61172873999")
        #response2 = requests.get(f"https://api.iextrading.com/1.0/stock/{urllib.parse.quote_plus(symbol)}/chart/date/{day2}")
        response2.raise_for_status()
    except requests.RequestException:
        print("failure2")
        return None
    try:
        response3 = requests.get(f"https://cloud.iexapis.com/beta/stock/{urllib.parse.quote_plus(symbol)}/chart/date/{day3}?token=sk_1b9e780a79d7472ea1c7c61172873999")
        #response3 = requests.get(f"https://api.iextrading.com/1.0/stock/{urllib.parse.quote_plus(symbol)}/chart/date/{day3}")
        response3.raise_for_status()
    except requests.RequestException:
        print("failure3")
        return None
    try:
        response4 = requests.get(f"https://cloud.iexapis.com/beta/stock/{urllib.parse.quote_plus(symbol)}/chart/date/{day4}?token=sk_1b9e780a79d7472ea1c7c61172873999")
        #response4 = requests.get(f"https://api.iextrading.com/1.0/stock/{urllib.parse.quote_plus(symbol)}/chart/date/{day4}")
        response4.raise_for_status()
    except requests.RequestException:
        print("failure4")
        return None
    try:
        response5 = requests.get(f"https://cloud.iexapis.com/beta/stock/{urllib.parse.quote_plus(symbol)}/chart/date/{day5}?token=sk_149e3498712e4d6ab796bd2d54e29599")
        #response5 = requests.get(f"https://api.iextrading.com/1.0/stock/{urllib.parse.quote_plus(symbol)}/chart/date/{day5}")
        response5.raise_for_status()
    except requests.RequestException:
        print("failure5")
        return None
    try:
        response6 = requests.get(f"https://cloud.iexapis.com/beta/stock/{urllib.parse.quote_plus(symbol)}/chart/date/{day6}?token=sk_149e3498712e4d6ab796bd2d54e29599")
        #response6 = requests.get(f"https://api.iextrading.com/1.0/stock/{urllib.parse.quote_plus(symbol)}/chart/date/{day6}")
        response6.raise_for_status()
    except requests.RequestException:
        print("failure6")
        return None

    # Parse response
    try:
        quote0 = response0.json()
        quote1 = response1.json()
        quote2 = response2.json()
        quote3 = response3.json()
        quote4 = response4.json()
        quote5 = response5.json()
        quote6 = response6.json()
    #print(quote0[0]["marketAverage"])
    #print(quote1)
    #print(quote2)
    #print(quote3)
    #print(quote4)
    #print(quote5)
    #print(quote6)
        return {
        #"name": quote0[0]["companyName"],
            "price0": float(quote0[0]["marketAverage"]),
            "price1": float(quote1[0]["marketAverage"]),
            "price2": float(quote2[0]["marketAverage"]),
            "price3": float(quote3[0]["marketAverage"]),
            "price4": float(quote4[0]["marketAverage"]),
            "price5": float(quote5[0]["marketAverage"]),
            "price6": float(quote6[0]["marketAverage"]),
        #"symbol": quote0[0]["symbol"]

        }
    except (KeyError, TypeError, ValueError):
        return None

def lookupInfo(symbol):
    try:
        info_response = requests.get(f"https://cloud.iexapis.com/beta/stock/{urllib.parse.quote_plus(symbol)}/company?token=sk_1b9e780a79d7472ea1c7c61172873999")
        logo_response = requests.get(f"https://cloud.iexapis.com/beta/stock/{urllib.parse.quote_plus(symbol)}/logo?token=sk_1b9e780a79d7472ea1c7c61172873999")
    except:
        return None
    try:
        info = info_response.json()
        logo = logo_response.json()
        return {
            "name": info["companyName"],
            "description": info["description"],
            "logo_url": logo["url"]
        }
    except (KeyError, TypeError, ValueError):
        return None

def returnWeekdays():
    if datetime.datetime.today().weekday() < 5:
        day0 = datetime.datetime.today()
    else:
        day0 = datetime.datetime.today()
        shift = day0.weekday() - 4
        day0 = day0 - datetime.timedelta(days = shift)

    day1 = day0 - datetime.timedelta(days = 1)
    if day1.weekday() > 4:
        shift = day1.weekday() - 4
        day1 = day1 - datetime.timedelta(days = shift)
    day2 = day1 - datetime.timedelta(days = 1)
    if day2.weekday() > 4:
        shift = day2.weekday() - 4
        day2 = day2 - datetime.timedelta(days = shift)
    day3 = day2 - datetime.timedelta(days = 1)
    if day3.weekday() > 4:
        shift = day3.weekday() - 4
        day3 = day3 - datetime.timedelta(days = shift)
    day4 = day3 - datetime.timedelta(days = 1)
    if day4.weekday() > 4:
        shift = day4.weekday() - 4
        day4 = day4 - datetime.timedelta(days = shift)
    day5 = day4 - datetime.timedelta(days = 1)
    if day5.weekday() > 4:
        shift = day5.weekday() - 4
        day5 = day5 - datetime.timedelta(days = shift)
    day6 = day5 - datetime.timedelta(days = 1)
    if day6.weekday() > 4:
        shift = day6.weekday() - 4
        day6 = day6 - datetime.timedelta(days = shift)
    day0 = day0.strftime('%-m/%-d/%Y')
    day1 = day1.strftime('%-m/%-d/%Y')
    day2 = day2.strftime('%-m/%-d/%Y')
    day3 = day3.strftime('%-m/%-d/%Y')
    day4 = day4.strftime('%-m/%-d/%Y')
    day5 = day5.strftime('%-m/%-d/%Y')
    day6 = day6.strftime('%-m/%-d/%Y')
    return [day6, day5, day4, day3, day2, day1, day0]
def lookupday(stock, day):
    date = day.strftime('%Y%m%d')
    try:
        response = requests.get(f"https://cloud.iexapis.com/beta/stock/{urllib.parse.quote_plus(stock)}/chart/date/{date}?token=sk_1b9e780a79d7472ea1c7c61172873999")#sk_149e3498712e4d6ab796bd2d54e29599
        response.raise_for_status()
    except requests.RequestException:
        return None
    try:
        quote = response.json()
    except (KeyError, TypeError, ValueError, AttributeError):
        return lookupday(stock, day - datetime.timedelta(days=1))
    if not quote:
        return lookupday(stock, day - datetime.timedelta(days=1))
    else:
        return quote[len(quote)-1]["marketAverage"]

def accbalanceday(day, uid):
    usertrades = db.execute("SELECT * FROM transactions WHERE id = :uid", uid = uid)
    user = db.execute("SELECT * FROM users WHERE id = :uid", uid = uid)
    cash = user[0]["cash"]
    for row in usertrades:
        if datetime.datetime.strptime(row["time"], '%Y-%m-%d %H:%M:%S.%f') < day:
            cash += row["method"] * row["pps"] * row["numstocks"]
        else:
            break
    owns = db.execute("SELECT * FROM ownership WHERE user = :uid", uid = uid)
    stocks = {}
    #print(usertrades)
    def daysort(e):
        return datetime.datetime.strptime(e["time"], '%Y-%m-%d %H:%M:%S.%f')
    usertrades = sorted(usertrades, key=daysort, reverse=True)
    #print(usertrades)
    for row in usertrades:
        if datetime.datetime.strptime(row["time"], '%Y-%m-%d %H:%M:%S.%f') > day:
            break
        else:
            #print(stocks, row)
            if row["stock"] not in stocks and row["method"] == 1:
                stocks[row["stock"]] = row["numstocks"]
            else:
                stocks[row["stock"]] += row["numstocks"] * row["method"]
    liquid = 0
    date = day.strftime('%-m/%-d/%Y')
    for stock, number in stocks.items():
        price = lookupday(stock, day)
        liquid += price * number
    return cash + liquid
def acchistory(uid):
    user = db.execute("SELECT * FROM users WHERE id = :uid", uid = uid)
    start = datetime.datetime.strptime(user[0]["creation"], '%Y-%m-%d %H:%M:%S.%f')
    time = datetime.datetime.now() - start
    balances = []
    for i in range(time.days):
        day = start + datetime.timedelta(days=i)
        balances.append({'day': day.strftime('%-m/%-d/%Y'), 'balance': accbalanceday(day, uid)})
    return balances
def weekhistory(balances):
    week = []
    i = 0
    while i < 7:
        try:
            week = [balances[-1-i]] + week
        except:
            break
        i+=1
    return week
def monthistory(balances):
    month = []
    now = datetime.datetime.now()
    lenmonth = monthrange(now.year, now.month)[1]
    i = 0
    while i < lenmonth:
        try:
            month = [balances[-1-i]] + month
            #print([balances[-1-i]], month)
        except:
            break
        i += 1
    return month
def yearhistory(balances):
    i = 0
    year = []
    while i < 365:
        try:
            year = [balances[-1-i]] + year
        except:
            break
        i += 1
    return year
def getsymbols():
    try:
        response = requests.get(f"https://cloud.iexapis.com/beta/ref-data/iex/symbols?token=sk_1b9e780a79d7472ea1c7c61172873999")#sk_149e3498712e4d6ab796bd2d54e29599
        response.raise_for_status()
    except requests.RequestException:
        return None
    try:
        response = response.json()
    except (KeyError, TypeError, ValueError, AttributeError):
        return
    symbols = []
    for symbol in response:
        if symbol["isEnabled"] == True:
            symbols.append(symbol["symbol"])
    return symbols
def mathgrowth(rate, end):
    date = datetime.datetime.strptime(end['day'], '%m/%d/%Y')
    balances = []
    i = 0
    money = end['balance']
    while i < 365:
        money *= math.e**(rate)
        date = date+datetime.timedelta(days = 1)
        balances.append({'day': date.strftime('%m/%d/%Y'), 'balance': money})
        i += 1
    return balances
def projected(balances):
    start = balances[0]
    end = balances[len(balances)-1]
    time = (datetime.datetime.strptime(end['day'], '%m/%d/%Y') - datetime.datetime.strptime(start['day'], '%m/%d/%Y')).days
    increase = end['balance']/start['balance']
    rate = math.log(increase) / time
    return mathgrowth(rate, end)

def monthgrowth(stock):
    try:
        response = requests.get(f"https://cloud.iexapis.com/beta/stock/{urllib.parse.quote_plus(symbol)}/chart/1m?token=sk_1b9e780a79d7472ea1c7c61172873999")
        response.raise_for_status()
    except requests.RequestException:
        return None
    try:
        month = response.json()
        return month[-1]["changeOverTime"]

    except (KeyError, TypeError, ValueError):
        print("key/type/value error")
        return None

def yeargrowth(stock):
    try:
        response = requests.get(f"https://cloud.iexapis.com/beta/stock/{urllib.parse.quote_plus(symbol)}/chart/1y?token=sk_1b9e780a79d7472ea1c7c61172873999")
        response.raise_for_status()
    except requests.RequestException:
        return None
    try:
        month = response.json()
        return month[-1]["changeOverTime"]

    except (KeyError, TypeError, ValueError):
        print("key/type/value error")
        return None

def testvalues():
    return mathgrowth(.04, {'balance': 100000, 'day': "11/10/2021"})

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
