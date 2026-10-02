from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os


# =========================================================
# CAMPUSKART BACKEND
# Python + Flask + SQLite
# =========================================================


app = Flask(__name__)

# Frontend ko backend API access karne ki permission
CORS(app)


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "campuskart.db")


def get_db():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def initialize_database():

    connection = get_db()

    cursor = connection.cursor()


    # -----------------------------------------------------
    # VENDORS TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendors (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            category TEXT NOT NULL,

            description TEXT,

            services TEXT,

            price REAL DEFAULT 0,

            phone TEXT,

            email TEXT,

            address TEXT,

            locality TEXT,

            latitude REAL,

            longitude REAL,

            rating REAL DEFAULT 0,

            total_reviews INTEGER DEFAULT 0,

            verified INTEGER DEFAULT 0,

            image_url TEXT,

            created_at TEXT NOT NULL

        )
    """)


    # -----------------------------------------------------
    # REVIEWS TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            vendor_id INTEGER NOT NULL,

            student_name TEXT NOT NULL,

            rating REAL NOT NULL,

            comment TEXT,

            created_at TEXT NOT NULL,

            FOREIGN KEY (vendor_id)
            REFERENCES vendors(id)

        )
    """)


    # -----------------------------------------------------
    # FAVORITES TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id TEXT NOT NULL,

            vendor_id INTEGER NOT NULL,

            created_at TEXT NOT NULL,

            UNIQUE(student_id, vendor_id),

            FOREIGN KEY (vendor_id)
            REFERENCES vendors(id)

        )
    """)


    # -----------------------------------------------------
    # CONTACT REQUESTS TABLE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact_requests (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            vendor_id INTEGER NOT NULL,

            student_name TEXT NOT NULL,

            student_phone TEXT,

            message TEXT,

            created_at TEXT NOT NULL,

            FOREIGN KEY (vendor_id)
            REFERENCES vendors(id)

        )
    """)


    connection.commit()

    connection.close()


# =========================================================
# HELPER FUNCTION
# =========================================================

def vendor_to_dict(vendor):

    return {

        "id": vendor["id"],

        "name": vendor["name"],

        "category": vendor["category"],

        "description": vendor["description"],

        "services": vendor["services"],

        "price": vendor["price"],

        "phone": vendor["phone"],

        "email": vendor["email"],

        "address": vendor["address"],

        "locality": vendor["locality"],

        "latitude": vendor["latitude"],

        "longitude": vendor["longitude"],

        "rating": vendor["rating"],

        "total_reviews": vendor["total_reviews"],

        "verified": bool(vendor["verified"]),

        "image_url": vendor["image_url"],

        "created_at": vendor["created_at"]

    }


# =========================================================
# HOME / HEALTH CHECK
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({

        "success": True,

        "message": "CampusKart Backend is running 🚀",

        "technology": {

            "backend": "Python Flask",

            "database": "SQLite",

            "api": "REST API"

        }

    })


@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({

        "success": True,

        "status": "online",

        "message": "CampusKart API is working"

    })


# =========================================================
# GET ALL VENDORS
# =========================================================

@app.route("/api/vendors", methods=["GET"])
def get_vendors():

    connection = get_db()

    cursor = connection.cursor()


    # Query parameters
    category = request.args.get("category")
    locality = request.args.get("locality")
    search = request.args.get("search")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    sort = request.args.get("sort")


    query = "SELECT * FROM vendors WHERE 1=1"

    parameters = []


    # -----------------------------------------------------
    # CATEGORY FILTER
    # -----------------------------------------------------

    if category:

        query += " AND LOWER(category) = LOWER(?)"

        parameters.append(category)


    # -----------------------------------------------------
    # LOCALITY FILTER
    # -----------------------------------------------------

    if locality:

        query += " AND LOWER(locality) LIKE LOWER(?)"

        parameters.append(f"%{locality}%")


    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    if search:

        query += """
            AND (
                LOWER(name) LIKE LOWER(?)
                OR LOWER(category) LIKE LOWER(?)
                OR LOWER(description) LIKE LOWER(?)
                OR LOWER(services) LIKE LOWER(?)
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value,
            search_value,
            search_value
        ])


    # -----------------------------------------------------
    # PRICE FILTER
    # -----------------------------------------------------

    if min_price:

        query += " AND price >= ?"

        parameters.append(float(min_price))


    if max_price:

        query += " AND price <= ?"

        parameters.append(float(max_price))


    # -----------------------------------------------------
    # SORTING
    # -----------------------------------------------------

    if sort == "rating":

        query += " ORDER BY rating DESC"


    elif sort == "distance":

        # SQLite itself doesn't know user's location.
        # Distance calculation can be added with coordinates later.

        query += " ORDER BY id DESC"


    elif sort == "price":

        query += " ORDER BY price ASC"


    else:

        query += " ORDER BY id DESC"


    cursor.execute(query, parameters)

    vendors = cursor.fetchall()

    connection.close()


    return jsonify({

        "success": True,

        "count": len(vendors),

        "vendors": [
            vendor_to_dict(vendor)
            for vendor in vendors
        ]

    })


# =========================================================
# GET SINGLE VENDOR
# =========================================================

@app.route("/api/vendors/<int:vendor_id>", methods=["GET"])
def get_vendor(vendor_id):

    connection = get_db()

    cursor = connection.cursor()


    cursor.execute(
        "SELECT * FROM vendors WHERE id = ?",
        (vendor_id,)
    )


    vendor = cursor.fetchone()

    connection.close()


    if vendor is None:

        return jsonify({

            "success": False,

            "message": "Vendor not found"

        }), 404


    return jsonify({

        "success": True,

        "vendor": vendor_to_dict(vendor)

    })


# =========================================================
# ADD NEW VENDOR
# =========================================================

@app.route("/api/vendors", methods=["POST"])
def create_vendor():

    data = request.get_json()


    if not data:

        return jsonify({

            "success": False,

            "message": "Request body is required"

        }), 400


    required_fields = [
        "name",
        "category"
    ]


    for field in required_fields:

        if not data.get(field):

            return jsonify({

                "success": False,

                "message": f"{field} is required"

            }), 400


    connection = get_db()

    cursor = connection.cursor()


    created_at = datetime.now().isoformat()


    cursor.execute("""

        INSERT INTO vendors (

            name,
            category,
            description,
            services,
            price,
            phone,
            email,
            address,
            locality,
            latitude,
            longitude,
            rating,
            total_reviews,
            verified,
            image_url,
            created_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        data.get("name"),

        data.get("category"),

        data.get("description", ""),

        data.get("services", ""),

        float(data.get("price", 0)),

        data.get("phone", ""),

        data.get("email", ""),

        data.get("address", ""),

        data.get("locality", ""),

        data.get("latitude"),

        data.get("longitude"),

        float(data.get("rating", 0)),

        int(data.get("total_reviews", 0)),

        int(data.get("verified", 0)),

        data.get("image_url", ""),

        created_at

    ))


    connection.commit()

    vendor_id = cursor.lastrowid

    connection.close()


    return jsonify({

        "success": True,

        "message": "Vendor created successfully",

        "vendor_id": vendor_id

    }), 201


# =========================================================
# UPDATE VENDOR
# =========================================================

@app.route("/api/vendors/<int:vendor_id>", methods=["PUT"])
def update_vendor(vendor_id):

    data = request.get_json()


    if not data:

        return jsonify({

            "success": False,

            "message": "Request body is required"

        }), 400


    connection = get_db()

    cursor = connection.cursor()


    cursor.execute(
        "SELECT * FROM vendors WHERE id = ?",
        (vendor_id,)
    )


    vendor = cursor.fetchone()


    if vendor is None:

        connection.close()

        return jsonify({

            "success": False,

            "message": "Vendor not found"

        }), 404


    cursor.execute("""

        UPDATE vendors

        SET

            name = ?,
            category = ?,
            description = ?,
            services = ?,
            price = ?,
            phone = ?,
            email = ?,
            address = ?,
            locality = ?,
            latitude = ?,
            longitude = ?,
            image_url = ?

        WHERE id = ?

    """, (

        data.get("name", vendor["name"]),

        data.get("category", vendor["category"]),

        data.get("description", vendor["description"]),

        data.get("services", vendor["services"]),

        float(data.get("price", vendor["price"])),

        data.get("phone", vendor["phone"]),

        data.get("email", vendor["email"]),

        data.get("address", vendor["address"]),

        data.get("locality", vendor["locality"]),

        data.get("latitude", vendor["latitude"]),

        data.get("longitude", vendor["longitude"]),

        data.get("image_url", vendor["image_url"]),

        vendor_id

    ))


    connection.commit()

    connection.close()


    return jsonify({

        "success": True,

        "message": "Vendor updated successfully"

    })


# =========================================================
# DELETE VENDOR
# =========================================================

@app.route("/api/vendors/<int:vendor_id>", methods=["DELETE"])
def delete_vendor(vendor_id):

    connection = get_db()

    cursor = connection.cursor()


    cursor.execute(
        "DELETE FROM vendors WHERE id = ?",
        (vendor_id,)
    )


    deleted = cursor.rowcount

    connection.commit()

    connection.close()


    if deleted == 0:

        return jsonify({

            "success": False,

            "message": "Vendor not found"

        }), 404


    return jsonify({

        "success": True,

        "message": "Vendor deleted successfully"

    })


# =========================================================
# ADD REVIEW
# =========================================================

@app.route("/api/vendors/<int:vendor_id>/reviews", methods=["POST"])
def add_review(vendor_id):

    data = request.get_json()


    if not data:

        return jsonify({

            "success": False,

            "message": "Request body is required"

        }), 400


    student_name = data.get("student_name")

    rating = data.get("rating")

    comment = data.get("comment", "")


    if not student_name or rating is None:

        return jsonify({

            "success": False,

            "message": "Student name and rating are required"

        }), 400


    rating = float(rating)


    if rating < 1 or rating > 5:

        return jsonify({

            "success": False,

            "message": "Rating must be between 1 and 5"

        }), 400


    connection = get_db()

    cursor = connection.cursor()


    cursor.execute(
        "SELECT id FROM vendors WHERE id = ?",
        (vendor_id,)
    )


    vendor = cursor.fetchone()


    if vendor is None:

        connection.close()

        return jsonify({

            "success": False,

            "message": "Vendor not found"

        }), 404


    created_at = datetime.now().isoformat()


    cursor.execute("""

        INSERT INTO reviews (

            vendor_id,
            student_name,
            rating,
            comment,
            created_at

        )

        VALUES (?, ?, ?, ?, ?)

    """, (

        vendor_id,
        student_name,
        rating,
        comment,
        created_at

    ))


    # -----------------------------------------------------
    # RECALCULATE VENDOR RATING
    # -----------------------------------------------------

    cursor.execute("""

        SELECT
            AVG(rating) AS average_rating,
            COUNT(*) AS total_reviews

        FROM reviews

        WHERE vendor_id = ?

    """, (vendor_id,))


    rating_data = cursor.fetchone()


    average_rating = rating_data["average_rating"]

    total_reviews = rating_data["total_reviews"]


    cursor.execute("""

        UPDATE vendors

        SET
            rating = ?,
            total_reviews = ?

        WHERE id = ?

    """, (

        round(average_rating, 1),

        total_reviews,

        vendor_id

    ))


    connection.commit()

    connection.close()


    return jsonify({

        "success": True,

        "message": "Review added successfully",

        "rating": round(average_rating, 1),

        "total_reviews": total_reviews

    }), 201


# =========================================================
# GET REVIEWS
# =========================================================

@app.route("/api/vendors/<int:vendor_id>/reviews", methods=["GET"])
def get_reviews(vendor_id):

    connection = get_db()

    cursor = connection.cursor()


    cursor.execute("""

        SELECT *

        FROM reviews

        WHERE vendor_id = ?

        ORDER BY id DESC

    """, (vendor_id,))


    reviews = cursor.fetchall()

    connection.close()


    return jsonify({

        "success": True,

        "count": len(reviews),

        "reviews": [

            {

                "id": review["id"],

                "vendor_id": review["vendor_id"],

                "student_name": review["student_name"],

                "rating": review["rating"],

                "comment": review["comment"],

                "created_at": review["created_at"]

            }

            for review in reviews

        ]

    })


# =========================================================
# ADD FAVORITE
# =========================================================

@app.route("/api/favorites", methods=["POST"])
def add_favorite():

    data = request.get_json()


    if not data:

        return jsonify({

            "success": False,

            "message": "Request body is required"

        }), 400


    student_id = data.get("student_id")

    vendor_id = data.get("vendor_id")


    if not student_id or not vendor_id:

        return jsonify({

            "success": False,

            "message": "student_id and vendor_id are required"

        }), 400


    connection = get_db()

    cursor = connection.cursor()


    try:

        cursor.execute("""

            INSERT INTO favorites (

                student_id,
                vendor_id,
                created_at

            )

            VALUES (?, ?, ?)

        """, (

            student_id,

            vendor_id,

            datetime.now().isoformat()

        ))


        connection.commit()


    except sqlite3.IntegrityError:

        connection.close()

        return jsonify({

            "success": False,

            "message": "Vendor already added to favorites"

        }), 409


    connection.close()


    return jsonify({

        "success": True,

        "message": "Vendor added to favorites"

    }), 201


# =========================================================
# REMOVE FAVORITE
# =========================================================

@app.route(
    "/api/favorites/<string:student_id>/<int:vendor_id>",
    methods=["DELETE"]
)
def remove_favorite(student_id, vendor_id):

    connection = get_db()

    cursor = connection.cursor()


    cursor.execute("""

        DELETE FROM favorites

        WHERE student_id = ?

        AND vendor_id = ?

    """, (

        student_id,

        vendor_id

    ))


    deleted = cursor.rowcount

    connection.commit()

    connection.close()


    return jsonify({

        "success": deleted > 0,

        "message":
            "Favorite removed"
            if deleted > 0
            else "Favorite not found"

    })


# =========================================================
# CONTACT VENDOR
# =========================================================

@app.route("/api/contact", methods=["POST"])
def contact_vendor():

    data = request.get_json()


    if not data:

        return jsonify({

            "success": False,

            "message": "Request body is required"

        }), 400


    vendor_id = data.get("vendor_id")

    student_name = data.get("student_name")

    student_phone = data.get("student_phone", "")

    message = data.get("message", "")


    if not vendor_id or not student_name:

        return jsonify({

            "success": False,

            "message": "vendor_id and student_name are required"

        }), 400


    connection = get_db()

    cursor = connection.cursor()


    cursor.execute("""

        INSERT INTO contact_requests (

            vendor_id,
            student_name,
            student_phone,
            message,
            created_at

        )

        VALUES (?, ?, ?, ?, ?)

    """, (

        vendor_id,

        student_name,

        student_phone,

        message,

        datetime.now().isoformat()

    ))


    connection.commit()

    request_id = cursor.lastrowid

    connection.close()


    return jsonify({

        "success": True,

        "message": "Contact request submitted",

        "request_id": request_id

    }), 201


# =========================================================
# ADMIN - VERIFY VENDOR
# =========================================================

@app.route(
    "/api/admin/vendors/<int:vendor_id>/verify",
    methods=["PUT"]
)
def verify_vendor(vendor_id):

    connection = get_db()

    cursor = connection.cursor()


    cursor.execute("""

        UPDATE vendors

        SET verified = 1

        WHERE id = ?

    """, (vendor_id,))


    updated = cursor.rowcount

    connection.commit()

    connection.close()


    if updated == 0:

        return jsonify({

            "success": False,

            "message": "Vendor not found"

        }), 404


    return jsonify({

        "success": True,

        "message": "Vendor verified successfully"

    })


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    initialize_database()

    print("")
    print("==========================================")
    print("       CAMPUSKART BACKEND 🚀")
    print("==========================================")
    print("Server: http://127.0.0.1:5000")
    print("API:    http://127.0.0.1:5000/api/vendors")
    print("==========================================")
    print("")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
    