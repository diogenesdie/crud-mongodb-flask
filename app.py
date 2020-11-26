from flask import Flask, Response, request
from flask_cors import CORS
import hashlib
import pymongo
import json
from bson.objectid import ObjectId


# Connecting the mongo database
try:
    mongo = pymongo.MongoClient(
        host                     = "localhost",
        port                     = 27017,
        serverSelectionTimeoutMS = 1000
    )
    db = mongo.cruduser
    mongo.server_info()
except:
    print("ERROR: Cannot possible to connect to database")


def search_exists_user(email):
    """This function searches for an email in the user Document, if found returns the user, if not false
        :param email: Email to search the document
        :type: str
        :return: Data of the user who owns the email
        :rtype: dict
        :return: False if not found the email on Document
        :rtype: boolean
    """
    try:
        data = db.user.find_one({"email": f"{email}"})

        if not data:
            return False

        return data

    except Exception as ex:
        return False


# Starting the flask app
app = Flask(__name__)

CORS(app, support_credentials=True)


@app.route('/users', methods=["GET"])
def get_users():
    """This function takes all users from the database
        :return: Flask Response with status and data
        :rtype: Response
    """
    try:
        data = list(db.user.find())

        for user in data:
            user['_id'] = str(user['_id'])

        return Response(
            response = json.dumps(data),
            status   = 200,
            mimetype = "application/json"
        )
    except Exception as ex:
        return Response(
            response = json.dumps({"error": "cannot read users",}),
            status   = 500,
            mimetype = "application/json"
        )


@app.route('/users', methods=["POST"])
def create_user():
    """This function inserts a new user in the database
        :return: Flask Response with status and message
        :rtype: Response
    """
    try:
        email    = json.loads(request.data).get('email')
        name     = json.loads(request.data).get('name')
        password = json.loads(request.data).get('password').encode()

        if search_exists_user(email):
            return Response(
                response = json.dumps({
                    "error": "email already registered",
                }),
                status   = 200,
                mimetype ="application/json"
            )

        user = {
            "email": email,
            "name": name,
            "password": hashlib.md5(password).hexdigest()
        }

        dbResponse = db.user.insert_one(user)

        return Response(
            response = json.dumps({
                "message": "user created",
                "id": f"{dbResponse.inserted_id}"
            }),
            status   = 200,
            mimetype = "application/json"
        )

    except Exception as ex:
        return Response(
            response = json.dumps({"error": "cannot create user",}),
            status   = 500,
            mimetype = "application/json"
        )


@app.route("/users/<id>", methods=["PUT"])
def update_user(id):
    """This function updates a user in the database
        :param id: User ObjectId to be updated
        :type: str
        :return: Flask Response with status and message
        :rtype: Response
    """
    try:
        email      = json.loads(request.data).get('email')
        name       = json.loads(request.data).get('name')
        password   = json.loads(request.data).get('password').encode()

        if search_exists_user(email):
            return Response(
                response = json.dumps({
                    "error": "email already registered",
                }),
                status   = 200,
                mimetype ="application/json"
            )

        dbResponse = db.user.update_one(
            {"_id": ObjectId(id)},
            {
                "$set":
                    {
                        "email": email,
                        "name": name,
                        "password": hashlib.md5(password).hexdigest()
                    }
            }
        )

        if not dbResponse.modified_count:
            return Response(
                response = json.dumps({"message": "nothing to update"}),
                status   = 200,
                mimetype = "application/json"
            )

        return Response(
            response = json.dumps({"message": "user updated"}),
            status   = 200,
            mimetype = "application/json"
        )

    except Exception as ex:
        return Response(
            response = json.dumps({"error": "cannot update user", }),
            status   = 500,
            mimetype = "application/json"
        )


@app.route("/users/<id>", methods=["DELETE"])
def delete_user(id):
    """This function deletes a user from the database
        :param id: User ObjectId to be deleted
        :type: str
        :return: Flask Response with status and message
        :rtype: Response
    """
    try:
        dbResponse = db.user.delete_one({"_id": ObjectId(id)})

        if not dbResponse.deleted_count:
            return Response(
                response = json.dumps({"message": "user not found"}),
                status   = 200,
                mimetype = "application/json"
            )

        return Response(
            response = json.dumps({"message": "user deleted"}),
            status   = 200,
            mimetype = "application/json"
        )

    except Exception as ex:
        return Response(
            response = json.dumps({"error": "cannot delete user", }),
            status   = 500,
            mimetype = "application/json"
        )


@app.route("/login", methods=["POST"])
def login():
    """This function authenticates a user for login
        :return: Flask Response with status and message
        :rtype: Response
    """
    try:

        email    = json.loads(request.data).get('email')
        password = json.loads(request.data).get('password').encode()
        user     = search_exists_user(email)

        if not user:
            return Response(
                response = json.dumps({"error": "user not found"}),
                status   = 200,
                mimetype = "application/json"
            )

        if str(hashlib.md5(password).hexdigest()) == user['password']:
            return Response(
                response = json.dumps({"verification": True}),
                status   = 200,
                mimetype = "application/json"
            )

        return Response(
            response = json.dumps({"verification": False}),
            status   = 200,
            mimetype = "application/json"
        )

    except Exception as ex:
        return Response(
            response = json.dumps({"error": "failed to authenticate", }),
            status   = 500,
            mimetype = "application/json"
        )


if __name__ == '__main__':
    app.run()

