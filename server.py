import jsonpickle
from flask import Flask, request
from paperbroker import PaperBroker
from paperbroker.orders import Order

# initialize a PaperBroker with defaults
broker = PaperBroker()

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')

# helper function to return pickled json
def json(data):
    global app
    response = app.response_class(
        response=jsonpickle.encode(data, unpicklable=False),
        status=200,
        mimetype='application/json'
    )
    return response

# begin routes

@app.route("/quotes/<asset>", methods=['GET'])
def get_quote(asset:str):
    return json(broker.get_quote(asset))


@app.route("/quotes/<asset>/options/<expiration_date>", methods=['GET'])
def get_options(asset=None, expiration_date=None):
    return json(broker.get_options(asset, expiration_date))


@app.route("/expirations/<asset>", methods=['GET'])
def get_expiration_dates(asset=None):
    return json(broker.get_expiration_dates(asset))


@app.route("/accounts", methods=['POST'])
@app.route("/accounts/create", methods=['GET'])
def open_account():
    return json(broker.open_account())


@app.route("/accounts/<account_id>", methods=['GET'])
def get_account(account_id: str = None):
    return json(broker.get_account(account_id=account_id))


@app.route("/accounts/<account_id>/orders/buy_to_open/<asset>", methods=['POST'])
def buy_to_open(account_id:str = None, asset:str = None):
    quantity = int(request.args.get('quantity', 1))
    simulate = not ( not (request.args.get('simulate', False) ) )
    return json(broker.buy_to_open(account = broker.get_account(account_id=account_id), asset=asset, quantity=quantity, simulate=simulate))


@app.route("/accounts/<account_id>/orders/sell_to_open/<asset>", methods=['POST'])
def sell_to_open(account_id:str = None, asset:str = None):
    quantity = int(request.args.get('quantity', 1))
    simulate = not ( not (request.args.get('simulate', False) ) )
    return json(broker.sell_to_open(account = broker.get_account(account_id=account_id), asset=asset, quantity=quantity, simulate=simulate))


@app.route("/accounts/<account_id>/orders/buy_to_close/<asset>", methods=['POST'])
def buy_to_close(account_id:str = None, asset:str = None):
    quantity = int(request.args.get('quantity', 1))
    simulate = not ( not (request.args.get('simulate', False) ) )
    return json(broker.buy_to_close(account = broker.get_account(account_id=account_id), asset=asset, quantity=quantity, simulate=simulate))


@app.route("/accounts/<account_id>/orders/sell_to_close/<asset>", methods=['POST'])
def sell_to_close(account_id:str = None, asset:str = None):
    quantity = int(request.args.get('quantity', 1))
    simulate = not ( not (request.args.get('simulate', False) ) )
    return json(broker.sell_to_close(account = broker.get_account(account_id=account_id), asset=asset, quantity=quantity, simulate=simulate))



@app.route("/accounts/<account_id>/positions/liquidate", methods=['POST'])
def liquidate_account_positions(account_id:str, positions=None, simulate=None):
    simulate = (not ( not (request.args.get('simulate', False) ) )) if simulate is not None else simulate
    account = broker.get_account(account_id=account_id)
    return json(broker.close_positions(account=account, positions=account.positions, simulate=simulate))


@app.route("/accounts/<account_id>/orders/simulate", methods=['POST'])
@app.route("/accounts/<account_id>/orders/create/simulate", methods=['GET'])
def simulate_order(account_id: str):
    return enter_order(account_id, simulate=True)


@app.route("/accounts/<account_id>/orders", methods=['POST'])
@app.route("/accounts/<account_id>/orders/create", methods=['GET'])
def enter_order(account_id: str, simulate=None):
    simulate = (not ( not (request.args.get('simulate', False) ) )) if simulate is not None else simulate

    order = Order()
    for x in range(4):
        if request.args.get('asset[{}]'.format(x), None) is not None:
            asset = request.args.get('asset[{}]'.format(x), None)
            order_type = request.args.get('order_type[{}]'.format(x), None)
            quantity = request.args.get('quantity[{}]'.format(x), None)

            if order_type is None:
                raise Exception('order_type is a required field')

            if quantity is None:
                raise Exception('quantity is a required field')

            order.add_leg(asset=asset, order_type=order_type, quantity=quantity)

    return json(broker.enter_order(account = broker.get_account(account_id=account_id), order=order, simulate=simulate))


@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('static', path or 'index.html')


@app.route('/')
def send_index():
    return send_from_directory('static', 'index.html')



"""

@app.route("/live/sell_otm_vertical_spread_quick_order_page/<symbol>", methods=['GET'])
def simulate_order(account: Account, order: Order, estimator: Estimator = None):
    account_after = self.market_adapter.simulate_order(account=account, order=order, estimator=estimator)
    validate_account(account_after)
    return account_after


@app.route("/live/sell_otm_vertical_spread_quick_order_page/<symbol>", methods=['GET'])
def close_position(account: Account, position=None):
    return self.close_positions(account, [position])


@app.route("/live/sell_otm_vertical_spread_quick_order_page/<symbol>", methods=['GET'])
def close_positions(account: Account, positions=None):
    if positions is None:
        positions = []

    btc = {}
    stc = {}
    assets_by_symbol = {}
    for p in positions:
        assets_by_symbol[p.asset.symbol] = p.asset
        if p.quantity > 0:
            stc[p.asset.symbol] = stc.get(p.asset.symbol, 0) + p.quantity
        else:
            btc[p.asset.symbol] = btc.get(p.asset.symbol, 0) + p.quantity

    o = Order()
    for s in stc.keys():
        o.add_leg(order_type='stc', asset=assets_by_symbol[s], quantity=-1 * stc[s])
    for b in btc.keys():
        o.add_leg(order_type='btc', asset=assets_by_symbol[b], quantity=abs(btc[b]))

    self.enter_order(account, o)

"""

if __name__ == "__main__":
    port = 8231
    app.debug = False
    print("PaperBroker Flask Server is starting on localhost:{}".format(port))
    app.run(host = "127.0.0.1", port = port, debug=False)
