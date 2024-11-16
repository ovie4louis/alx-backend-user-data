0. Et moi et moi et moi!
mandatory
Score: 0.0% (Checks completed: 0.0%)
Copy all your work of the 0x06. Basic authentication project in this new folder.

In this version, you implemented a Basic authentication for giving you access to all User endpoints:

GET /api/v1/users
POST /api/v1/users
GET /api/v1/users/<user_id>
PUT /api/v1/users/<user_id>
DELETE /api/v1/users/<user_id>
Now, you will add a new endpoint: GET /users/me to retrieve the authenticated User object.

Copy folders models and api from the previous project 0x06. Basic authentication
Please make sure all mandatory tasks of this previous project are done at 100% because this project (and the rest of this track) will be based on it.
Update @app.before_request in api/v1/app.py:
Assign the result of auth.current_user(request) to request.current_user
Update method for the route GET /api/v1/users/<user_id> in api/v1/views/users.py:
If <user_id> is equal to me and request.current_user is None: abort(404)
If <user_id> is equal to me and request.current_user is not None: return the authenticated User in a JSON response (like a normal case of GET /api/v1/users/<user_id> where <user_id> is a valid User ID)
Otherwise, keep the same behavior
