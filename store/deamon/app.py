import json
from operator import and_

from flask import Flask
from redis.client import Redis
from models import *

from configuration import Configuration
from models import ProductOrderMap

app = Flask(__name__)
app.config.from_object(Configuration)
database.init_app(app)


with Redis(host=Configuration.REDIS_HOST, port=6379, db=0) as r:
    sub = r.pubsub()
    sub.subscribe(Configuration.REDIS_SUBSCRIBE_CHANNEL)
    while True:
        msg = sub.get_message(True)
        if msg:
            with app.app_context() as context:
                data = msg.get('data')
                products = json.loads(data.decode('utf-8')).get('products')
                new_products = []
                for product in products:
                    p = Product.query.filter(Product.name == product.get("name")).first()
                    if p:
                        tags = [tag.name for tag in p.tags]
                        tags.sort()
                        product.get("categories").sort()
                        if tags != product.get("categories"):
                            continue
                        if p.quantity == 0:
                            pom = ProductOrderMap.query.filter(and_(ProductOrderMap.product_id == p.id, ProductOrderMap.received<ProductOrderMap.requested)).all()
                            for m in pom:
                                needed = m.requested - m.received
                                if needed > product.get("quantity"):
                                    m.received += product.get("quantity")
                                    product["quantity"] = 0
                                    continue
                                else:
                                    m.received = m.requested
                                    product["quantity"] = product.get("quantity")-needed
                                    check = ProductOrderMap.query.filter(and_(ProductOrderMap.order_id == m.order_id, ProductOrderMap.received < ProductOrderMap.requested)).first()
                                    if not check:
                                        order = Order.query.get(m.order_id)
                                        order.status = "COMPLETE"
                                        database.session.add(order)
                                    if product.get("quantity") == 0:
                                        continue
                                database.session.add(m)
                        if not p.quantity + product.get("quantity"): price = product.get("price")
                        else: price = (p.quantity * p.price + product.get("quantity")*product.get("price"))/(p.quantity + product.get("quantity"))
                        quantity = p.quantity + product.get("quantity")
                        p.price = price
                        p.quantity = quantity
                    else:
                        tags = [tag.name for tag in Tag.query.all()]
                        add_tags = []
                        new_tags = []
                        for tag in product.get("categories"):
                            if tag not in tags:
                                t = Tag(name=tag)
                                new_tags.append(t)
                                add_tags.append(t)
                            else:
                                add_tags.append(Tag.query.filter(Tag.name == tag).first())
                        if len(new_tags):
                            database.session.add_all(new_tags)
                            database.session.commit()

                        p = Product(name=product.get("name"), quantity=product.get("quantity"),
                                    price=product.get("price"), tags=add_tags)

                    new_products.append(p)
                database.session.add_all(new_products)
                database.session.commit()

