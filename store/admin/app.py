from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from sqlalchemy import func

from models import *

from configuration import Configuration
from permissions import permission

app = Flask(__name__)
app.config.from_object(Configuration)
database.init_app(app)
jwt = JWTManager(app)

@app.route("/productStatistics", methods=["GET"])
@permission('admin')
def productStatistics():
    results = database.session.query(ProductOrderMap.product_id, func.sum(ProductOrderMap.received).label('recieved'), func.sum(ProductOrderMap.requested).label('requested')).group_by(ProductOrderMap.product_id)
    statistics = []
    for row in results:
        statistics.append({"name": Product.query.get(row.product_id).name, "sold": int(row.requested), "waiting": int(row.requested-row.recieved)})
    print(statistics)
    return jsonify({"statistics": statistics}), 200



@app.route("/categoryStatistics", methods=["GET"])
@permission('admin')
def categoryStatistics():
    results = database.session.query(Product).filter(Product.id.in_([p.product_id for p in ProductOrderMap.query.all()]))
    tag_sold = {}
    for product in results:
        sold = database.session.query(func.sum(ProductOrderMap.requested).label('requested')).group_by(ProductOrderMap.product_id).filter(ProductOrderMap.product_id == product.id).first()
        for tag in product.tags:
            tag_sold.setdefault(tag, 0)
            tag_sold[tag] = tag_sold.get(tag) + int(sold.requested)
    tag_list = [[tag_sold.get(tag, 0), tag.name] for tag in Tag.query.all()]
    tag_list.sort(key=lambda element: (-element[0], element[1]))
    print(tag_list, flush=True)
    return jsonify({"statistics": [t[1] for t in tag_list]}), 200


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5003)

