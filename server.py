from flask import Flask, request, send_from_directory
from paperbroker import PaperBroker
from paperbroker.orders import Order
import ujson

# initialize a PaperBroker with defaults
broker = PaperBroker()

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')

# helper function to return json
def json(data):
    global app
    response = app.response_class(
        response=ujson.dumps(data).replace('NaN', 'null'),
        status=200,
        mimetype='application/json'
    )
    return response

# begin routes

@app.route("/quotes/<asset>", methods=['GET'])
def get_quote(asset:str):
    return json(broker.get_quote(asset))


@app.route("/quotes/<asset>/options/<expiration_date>", methods=['GET'])
def get_options(asset=None, expiration_date=None, only_priceable=True):
    if only_priceable:
        return json([_ for _ in broker.get_options(asset, expiration_date) if _.is_priceable()])
    else:
        return json([_ for _ in broker.get_options(asset, expiration_date)])


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
    simulate = not(not(request.args.get('simulate', False))) if simulate is None else simulate

    order = Order()
    for x in range(4):
        if request.args.get('legs[{}][asset]'.format(x-1), None) is not None:
            asset = request.args.get('legs[{}][asset]'.format(x-1), None)
            order_type = request.args.get('legs[{}][order_type]'.format(x-1), None)
            quantity = request.args.get('legs[{}][quantity]'.format(x-1), None)

            if order_type is None:
                raise Exception('order_type is a required field')

            if quantity is None:
                raise Exception('quantity is a required field')

            order.add_leg(asset=asset, order_type=order_type, quantity=quantity)

    account = broker.get_account(account_id=account_id)
    return json(broker.enter_order(account = account, order=order, simulate=simulate))

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('static', path or 'index.html')


@app.route('/')
def send_index():
    return send_from_directory('static', 'index.html')



if __name__ == "__main__":
    port = 8231
    app.debug = False
    print("PaperBroker Flask Server is starting on localhost:{}".format(port))
    app.run(host = "127.0.0.1", port = port, debug=False)
