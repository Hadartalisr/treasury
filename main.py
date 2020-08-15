from flask import Flask, request
import moneyHeist

app = Flask(__name__)


@app.route("/ping")
def ping():
    return {"pingResults": "pong"}


@app.route("/getDates", methods=['GET'])
def get_dates():
    start_date = request.args.get('startdate')
    end_date = request.args.get('enddate')
    dr = [start_date[6:8], start_date[4:6], start_date[0:4], end_date[6:8], end_date[4:6], end_date[0:4]]
    dates = moneyHeist.main(dr)
    return {"getDatesResults": dates}


@app.route("/getLongDates", methods=['GET'])
def get_long_dates():
    start_date = request.args.get('startdate')
    end_date = request.args.get('enddate')
    amount = int(request.args.get('amount'))
    dr = [start_date[6:8], start_date[4:6], start_date[0:4], end_date[6:8], end_date[4:6], end_date[0:4]]
    get_long_days = moneyHeist.get_long_days(dr, amount)
    return {"getLongDatesResults": get_long_days}


if __name__ == "__main__":
    app.run()

