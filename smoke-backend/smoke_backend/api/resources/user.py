# -*- coding: utf-8 -*-
"""Handles communication with the SQLAlchemy database and handles its contents.

.. [#f1] https://marshmallow.readthedocs.io/en/3.0/
.. [#f2] http://docs.sqlalchemy.org/en/latest/orm/session_api.html#sqlalchemy.orm.session.Session
.. [#f3] https://pythonhosted.org/Flask-JWT/
.. [#f4] http://docs.sqlalchemy.org/en/latest/core/schema.html
.. [#f5] https://flask-restful.readthedocs.io/en/0.3.5/quickstart.html
.. [#f6] https://pythonhosted.org/Flask-JWT/
"""
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from smoke_backend.models import User
from smoke_backend.extensions import ma, db
from smoke_backend.commons.pagination import paginate


class UserSchema(ma.ModelSchema):
    """Models a current user logged in to the backend through a single object Marshmallow Model. [#f1]_

    Extends the Marshmallow ModelSchema class. [#f1]_

    Attributes:
        password (String): The user entered password. [#f1]_
    """
    password = ma.String(load_only=True, required=True)

    class Meta:
        """Metadata of the login session."""
        model = User
        sqla_session = db.session


class UserResource(Resource):
    """Single object resource for Flask control of the user database.

    Extends a Flask-RESTful Resource [#f4]_ object.

    Attributes:
        method_decorators: Singleton array of decorator objects to require a valid JWT token to be present. [#f3]_
            [#f6]_
    """
    method_decorators = [jwt_required]

    def get(self, user_id):
        """Show and return a user.

        Paramaters:
            user_id (int): The ID of the user to get.

        Returns:
            user: A dictionary of the user data.

        Raises:
            404: If user was not available.
        """
        schema = UserSchema()
        user = User.query.get_or_404(user_id)
        return {"user": schema.dump(user).data}

    def put(self, user_id):
        """Update a user.

        Paramaters:
            user_id (int): The ID of the user to get.

        Returns:
            user: Returns a dictionary of the user data or an error message if the User was not in the database.

        Raises:
            404: If user was not available.
        """
        schema = UserSchema(partial=True)
        user = User.query.get_or_404(user_id)
        user, errors = schema.load(request.json, instance=user)
        if errors:
            return errors, 422

        return {"msg": "user updated", "user": schema.dump(user).data}

    def delete(self, user_id):
        """Delete a user.

        Paramaters:
            user_id (int): The ID of the user to get.

        Returns:
            str: A message noting that the user was deleted.

        Raises:
            404: If user was not available.
        """
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        return {"msg": "user deleted"}


class UserList(Resource):
    """Returns a list of all of the users currently in the database.

    Uses pagination.py to generate a paginated view of all of the users in the database.

    Attributes:
        method_decorators: Singleton array of decorator objects to require a valid JWT token to be present. [#f3]_
            [#f6]_
    """
    method_decorators = [jwt_required]

    def get(self):
        """Get a list of all users.

        Returns:
            A paginated list of all the users as defined by pagination.py.
        """
        schema = UserSchema(many=True)
        query = User.query
        return paginate(query, schema)

    def post(self):
        """Create a new user & put it in the database if there are no errors.

        Returns:
            String: Noting whether the user was created or the error which caused creation to fail.

        Raises:
            404: If the json request failed.
        """
        schema = UserSchema()
        user, errors = schema.load(request.json)
        if errors:
            return errors, 422

        db.session.add(user)
        db.session.commit()

        return {"msg": "user created", "user": schema.dump(user).data}, 201
