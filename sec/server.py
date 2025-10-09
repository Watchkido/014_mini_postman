
# pip install flask
# python server.py
# ip deines rechners:  z.b. http://192.168.178.77:5000

from flask import Flask, jsonify, request

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# --- Initialdaten ---
users = [
    {"id": 1, "first_name": "George", "last_name": "Bluth", "email": "george.bluth@reqres.in", "job": "CEO"},
    {"id": 2, "first_name": "Janet", "last_name": "Weaver", "email": "janet.weaver@reqres.in", "job": "Marketing Manager"},
    {"id": 3, "first_name": "Emma", "last_name": "Wong", "email": "emma.wong@reqres.in", "job": "Software Developer"},
    {"id": 4, "first_name": "Eve", "last_name": "Holt", "email": "eve.holt@reqres.in", "job": "Designer"},
    {"id": 5, "first_name": "Charles", "last_name": "Morris", "email": "charles.morris@reqres.in", "job": "Project Manager"}
]


# --- Root Route: API-Uebersicht ---
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Mini Postman API Server",
        "version": "1.0",
        "endpoints": {
            "GET /users": "Alle User anzeigen",
            "GET /users/<id>": "Einzelnen User anzeigen",
            "POST /users": "Neuen User erstellen",
            "PUT /users/<id>": "User komplett ersetzen",
            "PATCH /users/<id>": "User teilweise aendern",
            "DELETE /users/<id>": "User loeschen"
        },
        "example_usage": {
            "get_all_users": "GET http://localhost:5000/users",
            "get_user_by_id": "GET http://localhost:5000/users/1",
            "create_user": "POST http://localhost:5000/users (mit JSON Body)"
        }
    }), 200


# --- API Info Route ---
@app.route("/api", methods=["GET"])
def api_info():
    return jsonify({
        "api": "Mini Postman API",
        "status": "running",
        "total_users": len(users),
        "available_routes": [
            "GET /",
            "GET /api", 
            "GET /users",
            "GET /users/<id>",
            "POST /users",
            "PUT /users/<id>",
            "PATCH /users/<id>",
            "DELETE /users/<id>"
        ]
    }), 200


# --- GET: alle User anzeigen ---
@app.route("/users", methods=["GET"])
def get_users():
    return jsonify({"data": users}), 200


# --- GET: einzelner User ---
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    for user in users:
        if user["id"] == user_id:
            return jsonify(user), 200
    return jsonify({"error": "User not found"}), 404


# --- POST: neuen User anlegen ---
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or "first_name" not in data or "last_name" not in data or "email" not in data:
        return jsonify({"error": "Missing required fields: first_name, last_name, email"}), 400

    new_id = max(user["id"] for user in users) + 1 if users else 1
    new_user = {
        "id": new_id,
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "email": data["email"],
        "job": data.get("job", "")  # Job ist optional
    }
    users.append(new_user)
    return jsonify(new_user), 201


# --- PUT: kompletten User ersetzen ---
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    for user in users:
        if user["id"] == user_id:
            # Für Aufgabe 3: Wenn "name" gesendet wird, aktualisiere first_name/last_name
            if "name" in data:
                name_parts = data["name"].split(" ", 1)
                user["first_name"] = name_parts[0] if name_parts else user["first_name"]
                user["last_name"] = name_parts[1] if len(name_parts) > 1 else user["last_name"]
            
            # Aktualisiere verfügbare Felder
            user.update({
                "first_name": data.get("first_name", user["first_name"]),
                "last_name": data.get("last_name", user["last_name"]),
                "email": data.get("email", user["email"]),
                "job": data.get("job", user["job"])
            })
            return jsonify(user), 200
    return jsonify({"error": "User not found"}), 404


# --- PATCH: einzelne Felder ändern ---
@app.route("/users/<int:user_id>", methods=["PATCH"])
def patch_user(user_id):
    data = request.get_json()
    for user in users:
        if user["id"] == user_id:
            user.update(data)
            return jsonify(user), 200
    return jsonify({"error": "User not found"}), 404


# --- DELETE: User löschen ---
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    global users
    users = [user for user in users if user["id"] != user_id]
    return jsonify({"message": f"User {user_id} deleted"}), 200


# --- Server starten ---
if __name__ == "__main__":
    # Server auf allen Interfaces verfügbar machen (0.0.0.0)
    # Damit ist er über localhost UND die Netzwerk-IP erreichbar
    app.run(host='0.0.0.0', port=5000, debug=True)
