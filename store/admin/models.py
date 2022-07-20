from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()

productTagMap = database.Table("product_tag_map",
                               database.Column('product_id', database.Integer, database.ForeignKey("product.id"),
                                               nullable=False, primary_key=True),
                               database.Column('tag_id', database.Integer, database.ForeignKey("tag.id"),
                                               nullable=False, primary_key=True))


class ProductOrderMap(database.Model):
    __tablename__ = "product_order_map"

    product_id = database.Column(database.Integer, database.ForeignKey("product.id"), nullable=False, primary_key=True)
    order_id = database.Column(database.Integer, database.ForeignKey("order.id"), nullable=False, primary_key=True)
    requested = database.Column(database.Integer)
    received = database.Column(database.Integer)
    price = database.Column(database.Float)


class Product(database.Model):
    __tablename__ = "product"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)
    quantity = database.Column(database.Integer, nullable=False)
    price = database.Column(database.Float, nullable=False)

    tags = database.relationship("Tag", secondary=productTagMap, lazy="subquery",
                                 backref=database.backref('products', lazy=True))


class Tag(database.Model):
    __tablename__ = "tag"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False, unique=True)


class Order(database.Model):
    __tablename__ = "order"

    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, nullable=False)
    price = database.Column(database.Float, nullable=False)
    status = database.Column(database.String(15), nullable=False)  # PENDING ili COMPLETE
    placed = database.Column(database.DateTime, nullable=False)

    products = database.relationship("Product", secondary=ProductOrderMap.__table__, lazy="subquery")


