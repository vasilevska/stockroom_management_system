from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import database
from sqlalchemy_utils import database_exists, create_database

import os

app = Flask(__name__)
app.config.from_object(Configuration)

migrateObject = Migrate(app, database)

# done = False
# while not done:
if __name__ == '__main__':
    try:
        database.init_app(app)
        if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
            create_database(app.config["SQLALCHEMY_DATABASE_URI"])

        with app.app_context() as context:
            init()
            migrate(message="first migration")
            upgrade()

            database.session.commit()
            # done = True
    except Exception as e:
        print(e)
