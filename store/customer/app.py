from operator import and_

from flask import Flask, request, jsonify
from flask_jwt_extended import get_jwt_identity, JWTManager, get_jwt
from datetime import datetime

from models import *
from configuration import Configuration
from permissions import permission

app = Flask(__name__)
app.config.from_object(Configuration)
database.init_app(app)
jwt = JWTManager(app)

@app.route("/search", methods=["GET"])
@permission('customer')
def search_products():
    product_name = request.args.get('name')
    product_tag = request.args.get('category')

    if product_name is None:
        product_name = ""
    if product_tag is None:
        product_tag = ""

    tags_obj = Tag.query.filter(Tag.name.contains(product_tag))
    products_obj = Product.query.filter(Product.name.contains(product_name))
    tag_names = []
    products = []
    for product in products_obj:
        flag = False
        cur_tag_names = []
        for tag in product.tags:
            cur_tag_names.append(tag.name)
            if tag not in tags_obj:
                continue
            else:
                flag = True
                if tag.name not in tag_names:
                    tag_names.append(tag.name)
        if flag:
            products.append({"categories": cur_tag_names, "id": product.id, "name": product.name, "price": product.price, "quantity": product.quantity})
            #products.append(product.dict())
    tag_names.sort()

    return jsonify(categories=tag_names, products=products), 200


def check_missing(json, keys):
    return ['Field {} is missing.'.format(key) for key in keys if json.get(key, "") == ""]


@app.route("/order", methods=["POST"])
@permission('customer')
def place_order():
    claims = get_jwt()
    identity = claims["id"]

    missing = check_missing(request.json, ['requests'])
    if len(missing):
        message = missing[0]
        return jsonify(message=message), 400
    requests = request.json.get('requests')
    products = []
    price = 0

    order = Order(user_id=identity, price=0, status="COMPLETE", placed=datetime.now())
    database.session.add(order)
    database.session.flush()
    database.session.refresh(order)
    order_id = order.id
    for i, req in enumerate(requests):
        if req.get("id", "") == "":
            database.session.rollback()
            return jsonify(message="Product id is missing for request number {}.".format(str(i))), 400
        if req.get("quantity", "") == "":
            database.session.rollback()
            return jsonify(message="Product quantity is missing for request number {}.".format(str(i))), 400
        try:
            pid = int(req.get("id"))
            if pid <= 0:
                raise ValueError

        except ValueError:
            database.session.rollback()
            return jsonify(message='Invalid product id for request number {}.'.format(str(i))), 400

        try:
            quantity = req.get("quantity")
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            database.session.rollback()
            return jsonify(message='Invalid product quantity for request number {}.'.format(str(i))), 400
        with database.session.no_autoflush:
            product = Product.query.get(pid)
            if not product:
                database.session.rollback()
                return jsonify(message='Invalid product for request number {}.'.format(str(i))), 400
            order.products.append(product)
            database.session.flush()
            assoc = ProductOrderMap.query.filter(and_(ProductOrderMap.order_id == order.id, ProductOrderMap.product_id == product.id)).first()
            assoc.price = product.price
        if product.quantity < quantity:
            order.status = "PENDING"
            assoc.received = product.quantity
            product.quantity = 0
            assoc.requested = quantity
        else:
            assoc.received = quantity
            assoc.requested = quantity
            product.quantity -= quantity
        database.session.add(product)

        price += product.price * quantity
        # database.session.add(assoc)

        order.price = price
    database.session.commit()
    database.session.close()
    return jsonify(id=order_id), 200


@app.route("/status", methods=["GET"])
@permission('customer')
def get_orders():
    claims = get_jwt()
    identity = claims["id"]

    orders = []
    for o in Order.query.filter(Order.user_id == identity):
        products = []
        for p in o.products:
            mapping = ProductOrderMap.query.filter(and_(ProductOrderMap.order_id == o.id, ProductOrderMap.product_id == p.id)).first()
            products.append({"categories": [t.name for t in p.tags], "name": p.name, "price": mapping.price, "received": mapping.received, "requested": mapping.requested})
        orders.append({"products": products, "price": o.price, "status": o.status, "timestamp": o.placed})
    return jsonify({"orders": orders}), 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
