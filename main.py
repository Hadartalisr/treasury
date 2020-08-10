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


if __name__ == "__main__":
    app.run()

