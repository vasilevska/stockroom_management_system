import re

from flask import Flask, request, jsonify, Response
from flask_jwt_extended import *
from sqlalchemy import and_

from configuration import Configuration

from models import User, database
from permissions import permission

app = Flask(__name__)
app.config.from_object(Configuration)
jwt = JWTManager(app)
database.init_app(app)


def check_missing(json, keys):
    return ['Field {} is missing.'.format(key) for key in keys if json.get(key, "") == ""]


def valid_email(email):
    return True if re.fullmatch(r'[^@]+@[^@]+\.[^@]{2,}', email) and len(email) < 256 else False


def valid_password(password):
    return True if re.fullmatch(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[\d])[a-zA-Z\d]{8,256}$', password) else False


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/proba', methods=["GET"])
def proba():
    svi = User.query.all()
    return str(svi)


@app.route("/login", methods=["POST"])
def login():
    missing = check_missing(request.json, ['email', 'password'])
    if len(missing):
        message = missing[0]
        return jsonify(message=message), 400

    email = request.json.get("email", "")
    password = request.json.get("password", "")

    if not valid_email(email):
        return jsonify(message='Invalid email.'), 400

    user = User.query.filter(and_(User.email == email, User.password == password)).first()
    if user is None:
        return jsonify(message="Invalid credentials."), 400

    additional_claims = {
        "forename": user.forename,
        "surname": user.surname,
        "email": user.email,
        "role": user.role,
        "id": user.userId
    }

    access_token = create_access_token(identity=user.email, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=user.email, additional_claims=additional_claims)
    # time.sleep(1)

    return jsonify(accessToken=access_token, refreshToken=refresh_token), 200


@app.route('/register', methods=["POST"])
def register():
    missing = check_missing(request.json, ['forename', 'surname', 'email', 'password', 'isCustomer'])
    if len(missing):
        message = missing[0]
        return jsonify(message=message), 400

    password = request.json.get("password", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    isCustomer = request.json.get("isCustomer", "")

    role = "customer" if isCustomer else "manager"

    if not valid_email(email):
        return jsonify(message='Invalid email.'), 400
    if not valid_password(password):
        return jsonify(message='Invalid password.'), 400

    user = User.query.filter(User.email == email).first()
    if user:
        return jsonify(message="Email already exists."), 400

    user = User(forename=forename, surname=surname, email=email, password=password, role=role)
    database.session.add(user)
    database.session.commit()

    return Response(status=200)


@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refreshClaims = get_jwt()

    additionalClaims = {
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "email": refreshClaims["email"],
        "role": refreshClaims["role"],
        "id": refreshClaims["id"]
    }

    return jsonify(accessToken=create_access_token(identity=identity, additional_claims=additionalClaims)), 200


@app.route("/delete", methods=["POST"])
@permission('admin')
def delete():
    missing = check_missing(request.json, ['email'])
    if len(missing):
        message = missing[0]
        return jsonify(message=message), 400

    email = request.json.get("email", "")

    if not valid_email(email):
        return jsonify(message='Invalid email.'), 400

    user = User.query.filter(User.email == email).first()
    if not user:
        return jsonify(message="Unknown user."), 400
    database.session.delete(user)
    database.session.commit()

    return Response(status=200)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)
