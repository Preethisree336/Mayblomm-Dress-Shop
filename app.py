from flask import *
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

eng = create_engine("mysql+pymysql://root@localhost:3306/flask_db")
db = scoped_session(sessionmaker(bind=eng))
app = Flask(__name__)
app.secret_key = "preethi123"
app.debug = True



@app.route("/")
def index():
    return render_template("userlogin.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Check username already exists
        res = db.execute(
            text("select * from user where username=:u"),
            {"u": username}
        ).fetchone()

        if res:
            return render_template(
                "register.html",
                res="Username already exists"
            )

        # Store new user
        db.execute(
            text("insert into user values(:u,:p)"),
            {"u": username, "p": password}
        )
        db.commit()

        return render_template(
            "userlogin.html",
            res="Registration successful. Please login."
        )

    return render_template("register.html")


@app.route("/user_data", methods=["POST"])
def user_data():

    username = request.form.get("username")
    password = request.form.get("password")

    # Check username and password
    res = db.execute(
        text("select * from user where username=:u and password=:p"),
        {"u": username, "p": password}
    ).fetchone()

    if res:
        session["username"] = username
        return redirect("/dress")

    else:
        return render_template(
            "userlogin.html",
            res="Invalid username or password"
        )


@app.route("/dress")
def dress():

    if "username" not in session:
        return redirect("/")

    return render_template("dress.html")


@app.route("/form_data", methods=["POST"])
def form_data():
    name = request.form.get("name")
    description = request.form.get("description")
    color = request.form.get("color")
    price = request.form.get("price")
    img = request.files['img']
    fname = img.filename

    target = os.path.join(APP_ROOT, "static/images")
    os.makedirs(target, exist_ok=True)

    desti = os.path.join(target, fname)
    img.save(desti)

    db.execute( text("insert into dress_details values(:n,:d,:c,:p,:i)"),{"n": name, "d": description, "c": color,"p": price, "i": fname})
    db.commit()

    res = "DataStored"
    return render_template("dress.html", res=res)




@app.route("/view_details")
def view_details():
    if "username" not in session:
        return redirect("/")
    vi = db.execute(text("select * from dress_details")).fetchall()
    db.commit()
    return render_template("view.html",res=vi)



@app.route("/select_dress/<string:id>", methods=["GET"])
def select_dress(id):
    res = db.execute(text("select * from dress_details where name=:val"),{"val": id}).fetchone()
    return render_template("select.html", res=res)

@app.route("/delete_dress/<string:id>", methods=["GET"])
def delete_dress(id):
    db.execute(text("delete from dress_details where name=:val"),{"val": id})
    db.commit()
    return redirect("/view_details")
@app.route("/modify_dress/<string:id>", methods=["GET"])
def modify_dress(id):
    res = db.execute(text("select * from dress_details where name=:val"),{"val": id}).fetchone()

    return render_template("modify.html", res=res)

@app.route("/modify_data", methods=["POST", "GET"])
def modify_data():
    if request.method == "POST":
        name = request.form.get("name")
        price = request.form.get("price")
        db.execute(text("update dress_details set price=:pri where name=:ds"),{"pri": price, "ds": name})
        db.commit()
        return redirect("/view_details")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ =="__main__":
    app.run()
