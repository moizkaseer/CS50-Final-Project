import urllib
from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

import json

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))
    cash_in_hand=db.Column(db.Integer,default=500)
    stock = db.relationship('Stock', backref='owner')


class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    qty = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


def getQuotePrice(symbol):
    base_url = 'https://financialmodelingprep.com/api/v3/stock/real-time-price/'
    content = urllib.urlopen(base_url + symbol).read()
    print ("content is ", content)
    json_content = json.loads(content)
    print ("m is ", json_content['symbol'], " price", json_content['price'])
    if content:
        print("returning the price")
        return(json_content['price'])
    else:
        return render_template("404.html", display_content="Invalid symbol. No quote available")



'''     *********     '''
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form['email']
        password = request.form['password']
        data = User.query.filter_by(email=email, password=password).first()

        if data is not None:
            session['user'] = data.id
            print(session['user'])
            return redirect(url_for("home"))
        return render_template("incorrect_login.html")




'''     *********     '''
@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(email=request.form['email'], password=request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')



'''     *********     '''
@app.route('/home')
def home():
    user_id=session["user"]
    stock = Stock.query.filter_by(owner_id =user_id).first()
    print(type(stock.name))
    [str(x) for x in stock.name]
    print(x)
    return render_template('home.html',stock=stock, user=user_id)



'''     *********     '''
@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))



'''     *********     '''
@app.route('/show')
def show():
    show_user = User.query.all()
    return render_template('show.html', show_user=show_user)




'''     *********     '''
@app.route('/quote', methods=['GET', 'POST'])
def quote():

    if request.method == "POST":
        if not request.form.get("quote"):
            return render_template("404.html", display_content="No quote provided")
        symbol=request.form['quote']

        try:
            quote= getQuotePrice(symbol)
            return render_template("quote.html", quote=quote)
        except:
                return render_template("404.html", display_content="Invalid symbol. No quote available")

    # GET method
    else:
        return render_template("quote.html")



'''     *********     '''
@app.route('/buy', methods=['GET', 'POST'])
def buy():
    if request.method == "POST":
        symbol = request.form['symbol']
        shares = request.form['shares']

        if not request.form.get("symbol"):
            return render_template("404.html", display_content="No symbol provided")

        try:
            price=getQuotePrice(symbol)
            total_cash_spend= price*int(shares)
            user_id=session["user"]
            u=User.query.get(user_id)
            final_cash_in_hand=u.cash_in_hand-total_cash_spend
            print("final= ",final_cash_in_hand)
            if(final_cash_in_hand>0):
                u.cash_in_hand=final_cash_in_hand

                new_stock = Stock(name=symbol, qty=shares,owner_id=u.id )
                print("new stock", new_stock)
                db.session.add(new_stock)
                db.session.commit()
                print("commited")
            else:
                return render_template("404.html", display_content="Insufficient balance in the amount")
            print("After update: ",u.cash_in_hand)
            return redirect(url_for("home"))
        except:
                return render_template("404.html", display_content="Invalid symbol. No quote available")

    # GET method
    else:
        return render_template("buy.html")





'''     *********     '''
@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if request.method == "POST":
        symbol = request.form['symbol']
        shares = request.form['shares']

        if not request.form.get("symbol"):
            return render_template("404.html", display_content="No symbol provided")

        try:
            price=getQuotePrice(symbol)
            total_cash_spend= price*int(shares)
            user_id=session["user"]
            u=User.query.get(user_id)
            final_cash_in_hand=u.cash_in_hand-total_cash_spend
            print("final= ",final_cash_in_hand)
            if(final_cash_in_hand>0):
                u.cash_in_hand=final_cash_in_hand
                db.session.commit()
            else:
                return render_template("404.html", display_content="Insufficient balance in the amount")
            print(u.cash_in_hand)
            return redirect(url_for("home"))
        except:
                return render_template("404.html", display_content="Invalid symbol. No quote available")

    # GET method
    else:
        return render_template("sell.html")


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    db.create_all()
    app.run(debug=True)