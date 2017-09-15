from flask import render_template

from . import app
from .database import session, Entry

from flask import flash
from flask_login import login_user
from werkzeug.security import check_password_hash
from .database import User

PAGINATE_BY = 10

@app.route("/")
@app.route("/page/<int:page>")
def entries(page=1):
    # Zero-indexed page
    page_index = page - 1

    count = session.query(Entry).count()

    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1) // PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]

    return render_template("entries.html",
        entries=entries,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages
    )

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    return redirect(request.args.get('next') or url_for("entries"))
    
#acquires entry
from flask_login import login_required

@app.route("/entry/add", methods=["GET"])
@login_required
def add_entry_get():
    return render_template("add_entry.html")

from flask import request, redirect, url_for

#provides means of posting content on the main page
@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))

@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

@app.route(".login", methods=["POST"])
def login_user_pass():
    user=request.form["User"]
    password=request.form["Password"]

#acquires entries on an individual # basis
@app.route("/entry/<int:id>")
def entry_id(id):
    entry_unid = session.query(Entry).get(id)
    return render_template("entry_id.html", entry=entry)
    
#edits each entries, requires login information to utilize
@app.route("/entry/<int:id>/edit")
@login_required
def entry_id_edit(id):
    entry_unid = session.query(Entry).get(id)
    return render_template("edit_unid_entry.html")
    
#deletes entries, requires login information to utilize   
@app.route("/entry/<int:id>delete", methods["DELETE"])
def delete_entry_post(id):
    entry_unid = session.query(Entry).get(id)
    return render_template("delete_entry.html")
    
#limits entries based on number provided
@app.route("/?limit=20")
@app.route("/page/2?limit=20")





