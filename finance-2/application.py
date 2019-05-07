import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from datetime import datetime
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
import time
from flask_cors import CORS, cross_origin
from helpers import apology, login_required, lookup, usd, lookupweek, returnWeekdays, lookupInfo, lookupMonth, acchistory, weekhistory, monthistory, yearhistory, projected, testvalues, getsymbols, dictstocks, monthgrowth, yeargrowth, lookupVar, lookupYear

# Configure application
app = Flask(__name__)
CORS(app)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    response.headers["Access-Control-Allow-Credentials"] = 'true'
    response.headers["Access-Control-Allow-Methods"] =  "GET, POST, DELETE, PUT, OPTIONS"
    response.headers["access-control-allow-headers"] = "Content-Type, Authorization, Content-Length, X-Requested-With"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

ref = dictstocks()
allstocks = []
stocknames = []
for name, symbol in ref.items():
    allstocks.append(symbol)
    stocknames.append(name)

@app.route("/")
def index():
    """Inuative user landing page"""
    if session.get("user_id"):
        user = db.execute("SELECT * FROM users WHERE id = :uid;", uid = session["user_id"])
        if len(user) == 1:
            render_template("landing.html")
            #return redirect("/") # changed to home to save iex data
    return render_template("landing.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/investing")
def investing():
    return render_template("investing.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/me")
@login_required
def me():
    """Show portfolio of stocks"""
    user = db.execute("SELECT * FROM users WHERE id = :userid", userid = session["user_id"])
    owns = db.execute("SELECT * FROM ownership WHERE user = :userid", userid = session["user_id"])
    stocks = {}
    for row in owns:
        stocks[row['stock']] = row["number"]
        print(stocks)
    graphinfo = {}
    for stock, number in stocks.items():
        graphinfo[stock] = lookupMonth(stock)
        print(graphinfo)
        #stockprices[stock] = lookupMonth(stock)
    #print(len(graphinfo['NFLX']['prices']))
    #print(graphinfo['NFLX']["prices"][1])
    print("graphinfo: ", graphinfo)
    weekdays = returnWeekdays()
    traderows = db.execute("SELECT * FROM transactions WHERE id = :userid", userid = session["user_id"])
    trades = []
    for row in traderows:
        trades.append({'method': row["method"], 'stock': row["stock"], 'quantity': row["numstocks"], 'price': row["pps"]})
    stockinfo = {}
    for stock, number in stocks.items():
        stockinfo[stock] = lookupInfo(stock)
    balances = acchistory(session["user_id"])
    week = weekhistory(balances)
    month = monthistory(balances)
    future = projected(balances)
    #print(month)
    year = yearhistory(balances)

    return render_template("me.html", name = user[0]["fullname"], stocks = stocks, graphinfo = graphinfo, trades = trades, weekdays = weekdays, stockinfo = stockinfo, balances = balances, month=month,year=year,week=week, projected=future)

@app.route("/browse", methods=["GET", "POST"])
@login_required
def browse():
    """Buy shares of stock"""
    test = testvalues()
    owns = db.execute("SELECT * FROM ownership WHERE user = :userid", userid = session["user_id"])
    global allstocks
    stocks = allstocks[0:15]
    graphinfo = {}
    for stock in stocks:
        graphinfo[stock] = lookupMonth(stock)
    stockinfo = {}
    for stock in stocks:
        stockinfo[stock] = lookupInfo(stock)
    return render_template("browse.html", test=test, stocks=stocks, graphinfo=graphinfo, stockinfo=stockinfo)

@app.route('/stock')
@login_required
def stock():
    stock = request.args.get('stock')
    owns = db.execute("SELECT * FROM ownership WHERE user = :userid", userid = session["user_id"])
    owned = False
    for row in owns:
        if row['stock'] == stock:
            owned = row['stillowned']
    info = lookupInfo(stock)
    name = info["name"]
    month = lookupMonth(stock)
    print(month)
    week = {'prices': month['prices'][-8:-1], 'labels': month['labels'][-8:-1]}
    year = lookupYear(stock)
    fiveyear = lookupVar('5y', stock)
    return render_template('stock.html', stock=stock, name=name, month=month,year=year,week=week, year5 = fiveyear, owned=owned)

@app.route('/checkout')
@login_required
def checkout():
    if request.args.get('method') == 'buy':
        price = lookup(request.args.get('stock'))['price']
        return render_template('checkout.html', stock=request.args.get('stock'), method=request.args.get('method'), price=price)
    if request.args.get('method') == 'sell':
        owns = db.execute("SELECT * FROM ownership WHERE user = :userid", userid = session["user_id"])
        stocks = []
        for row in owns:
            stocks.append(row["stock"])
            if row['stock'] == request.args.get('stock'):
                m = row["number"]
        print(stocks)
        if request.args.get('stock') in stocks:
            return render_template('checkout.html', max=m, stock=request.args.get('stock'), method="Sell")
        else:
            return apology("do not own")
    else:
        return redirect('/browse')


@app.route('/purchase')
def purchase():
    if request.method == "POST":
        if not request.form.get('quantity'):
            message = "Must enter quantity"
            return render_template('checkout.html', message=message, error=True, method='Buy', stock=request.form.get('stock'))
        if not request.form.get('stock'):
            message = "Must enter stock"
            return render_template('checkout.html', message=message, error=True, method='Buy', stock=request.form.get('stock'))
        if int(request.form.get('quantity')) < 1:
            message = "Must enter valid quantity"
            return render_template('checkout.html', message=message, error=True, method='Buy', stock=request.form.get('stock'))
        price = lookup(request.form.get('stock')) * int(request.form.get('quantity'))
        user = db.execute("SELECT * FROM users WHERE id = :userid", userid = session["user_id"])
        if bool(user[0]["active"]):
            db.execute("UPDATE users SET active = False WHERE id = :uid", uid = session['user_id']) #remember to set true again
            if user[0]['cash'] < price:
                message = "Must enter valid quantity, you do not have enough money"
                return render_template('checkout.html', message=message, error=True, method='Buy', stock=request.form.get('stock'))
            new_cash = user[0]["cash"] - price
            db.execute("UPDATE users SET cash = :new_cash WHERE id = :uid", uid = session["user_id"], new_cash = new_cash)
            owning = db.execute("SELECT * FROM ownership WHERE user = :userid", userid = session["user_id"])
            owns = False
            for row in owning:
                if row["stock"] == request.form.get('stock'):
                    owns = True
            if not owns:
                db.execute("INSERT INTO ownership ('user', 'stock', 'number', 'buytime', 'stillowned') VALUES(:user, :stock, :number, :buytime, :stillowned)", user = session["user_id"], stock = request.form.get('stock'), number = request.form.get('quantity'), buytime = datetime.today() ,stillowned = True)
            else:
                db.execute("UPDATE ownership SET number = number + :quantity WHERE user = :username and stock = :stock", stock = request.form.get('stock'), quantity = request.form.get('quantity'), user = session["user_id"])
                db.execute("UPDATE ownership SET buytime = :now WHERE user = :username", now = datetime.today(), user = session["user_id"])
            db.execute("INSERT INTO transactions ('method', 'pps', 'numstocks', 'time', 'id') VALUES(1, :pps, :number, :buytime, :id)", pps= price / float())

@app.route('/sell')
def sell():
    if request.method == "POST":
        owns = db.execute("SELECT * FROM ownership WHERE user = :userid", userid = session["user_id"])
        stocks = []
        quantities = {}
        for row in owns:
            stocks.append(row["stock"])
            quanitities[row["stock"]] = row["number"]
        print(stocks)
        print(owns)
        if request.form.get('stock') in stocks:
            if request.form.get('quantitiy') <= quanitities[request.form.get('stock')]:
                return



@app.route('/stocklist')
@cross_origin(origins='*')
def stocklist():
    return jsonify(allstocks)

@app.route('/names')
@cross_origin(origins='*')
def names():
    return jsonify(stocknames)

@app.route('/refrence')
@cross_origin(origins='*')
def refrence():
    return jsonify(ref)


@app.route('/getdata')
@cross_origin(origins='*')
def getdata():
    print("got")
    section = int(request.args.get('section'))*15
    stocks = getsymbols()[section:section+15]
    response = []
    info = ""
    name = ""
    data = []
    for stock in stocks:
        info = lookupInfo(stock)
        data = lookupMonth(stock)
        name = info["name"]
        url = info["logo_url"]
        response.append({"stock": stock, "url": url, "data": data["prices"], "labels": data["labels"], "name": name})
    return jsonify(response)

@app.route('/search')
@cross_origin(origins='*')
def search():
    query = request.args.get("q").lower()
    if query == "":
        return
    print(query)
    print("SEARCHING")
    stocks = []
    for name, symbol in ref.items():
        if query in name.lower():
            if symbol not in stocks:
                stocks.append(symbol)
        if query in symbol.lower():
            if symbol not in stocks:
                stocks.append(symbol)
    response = []
    info = ""
    name = ""
    data = []
    for stock in stocks:
        info = lookupInfo(stock)
        data = lookupMonth(stock)
        name = info["name"]
        url = info["logo_url"]
        response.append({"stock": stock, "url": url, "data": data["prices"], "labels": data["labels"], "name": name})
    return jsonify(response)

@app.route("/sort")
@cross_origin(origins='*')
def sort():
    stocks = []
    method = request.args.get('method')
    if method == "growth":
        #TODO: Day, week periods
        if request.args.get('period') == '1m:':
            for stock in allstocks:
                stocks.append({"stock": [stock], "growth": monthgrowth(stock)})
            if request.args.get('direction') == 'hl':
                stocks = sorted(stocks, key = lambda i: i["growth"])
                print(stocks)
                ordered = []
                for stock in stocks:
                    ordered.append(stock["stock"] )
                return ordered
            if request.args.get('direction') == 'lh':
                stocks = sorted(stocks, key = lambda i: i["growth"],reverse=True)
                print(stocks)
                ordered = []
                for stock in stocks:
                    ordered.append(stock["stock"] )
                return ordered

        if request.args.get('period') == '1y':
            for stock in allstocks:
                stocks.append({"stock": [stock], "growth": yeargrowth(stock)})
            if request.args.get('direction') == 'hl':
                stocks = sorted(stocks, key = lambda i: i["growth"])
                print(stocks)
                ordered = []
                for stock in stocks:
                    ordered.append(stock["stock"] )
                print(ordered)
                return ordered
            if request.args.get('direction') == 'lh':
                stocks = sorted(stocks, key = lambda i: i["growth"],reverse=True)
                print(stocks)
                ordered = []
                for stock in stocks:
                    ordered.append(stock["stock"] )
                print(ordered)
                return ordered
    if method == 'price':
        stocks = []
        for stock in allstocks:
            stocks.append({"stock": [stock], "price": lookup(stock)})
        print(stocks)
        if request.args.get('direction') == 'hl':
            ordered = []
            for stock in sorted(stocks, key = lambda i: i["price"]):
                ordered.append(stock["price"])
            print(ordered)
            return ordered
        else:
            ordered = []
            for stock in sorted(stocks, key = lambda i: i["price"]):
                ordered.append(stock["price"])
            print(ordered)
            return ordered





@app.route('/buy', methods=["GET", "POST"])
@login_required
def buy():
    return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":


        # Ensure username was submitted
        if not request.form.get("username") or not request.form.get("password"):
            error = True
            username = False
            if not request.form.get("password"):
                password = False
            else:
                password = True
            return render_template("login.html", error = error, username = username, password = password, wrong = False)
            #return apology("must provide username", 403)

        # Ensure password was submitted
        #elif not request.form.get("password"):
            #return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username").rstrip())

        #last_login_attempt = rows[0]["last_login_attempt"]

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            db.execute("UPDATE users SET last_login_attempt = :rnow WHERE username = :username", rnow = time.time(), username = request.form.get("username"))
            return render_template("login.html", error = True, username = True, password = True, wrong = True)

        last_login_attempt = rows[0]["last_login_attempt"]
        if last_login_attempt is not None:
            if time.time() - last_login_attempt < 5:
                return apology("Chill.")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    return apology("TODO")


@app.route("/register", methods=["GET", "POST"]) #TODO: add email form, send an email
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not request.form.get("first-name").isalpha():
            validfname = False
        if not request.form.get("last-name").isalpha():
            validlname = False
        if not validlname or not validfname:
            return render_template("register.html", error = True, username = username, password = password, validfname = validfname, validlname = validlname)
        fullname = str(request.form.get("first-name")).capitalize() + " " + str(request.form.get("last-name")).capitalize()
        if not (username and password and request.form.get("first-name") and request.form.get("last-name")):
            return apology("Please submit all required forms")

        user = db.execute("SELECT * FROM users WHERE username = :username", username = username)
        if len(user) == 0:
            db.execute("INSERT INTO users ('username', 'hash', 'cash', 'fullname') VALUES(:username, :hashed, 10000, :fullname)", username = username, hashed = generate_password_hash(password), fullname = fullname)
            user_id = db.execute("SELECT id FROM users WHERE username = :username", username = username)
            session["user_id"] = user_id
            return redirect("/index")
        else:
            return apology("This username is taken")
    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
