import csv
import io
import json

from redis import Redis
from flask import Flask, request, jsonify, Response
from flask_jwt_extended import JWTManager
from permissions import permission

from configuration import Configuration

app = Flask(__name__)
app.config.from_object(Configuration)
jwt = JWTManager(app)

@app.route("/update", methods=["POST"])
@permission('manager')
def vote():
    file = request.files.get('file')
    if file is None:
        return jsonify(message='Field file is missing.'), 400

    content = file.stream.read().decode("utf-8")
    stream = io.StringIO(content)
    csv_reader = csv.reader(stream)

    products = []
    for i, product in enumerate(csv_reader):
        if len(product) != 4:
            return jsonify(message='Incorrect number of values on line {}.'.format(str(i))), 400

        categories = product[0].split("|")

        try:
            quantity = int(product[2])
            if quantity <= 0:
                return jsonify(message='Incorrect quantity on line {}.'.format(str(i))), 400
        except ValueError:
            return jsonify(message='Incorrect quantity on line {}.'.format(str(i))), 400

        try:
            price = float(product[3])
            if price <= 0:
                return jsonify(message='Incorrect price on line {}.'.format(str(i))), 400
        except ValueError:
            return jsonify(message='Incorrect price on line {}.'.format(str(i))), 400

        product = {
            "categories": categories,
            "name": product[1],
            "quantity": quantity,
            "price": price,
        }
        products.append(product)

    print(products, flush=True)
    with Redis(host=Configuration.REDIS_HOST) as redis:
        redis.publish(Configuration.REDIS_SUBSCRIBE_CHANNEL, json.dumps({"products": products}))
    #    for product in products:
    #        redis.lpush(Configuration.REDIS_PRODUCT_KEY, product)
    #    redis.publish(Configuration.REDIS_SUBSCRIBE_CHANNEL, "product_batch")

   # with Redis(host=Configuration.REDIS_HOST) as redis:
   #     redis.publish(Configuration.REDIS_VOTE_CHANNEL, json.dumps({"product": products}))

    return Response(status=200)

@app.route('/')
def hello():
    return "hello", 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)
