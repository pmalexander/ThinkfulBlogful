from flask import render_template

from . import app
from .database import session, Entry

from flask import flash
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from flask_login import login_manager
from werkzeug.security import check_password_hash
from flask import request, redirect, url_for
from .database import User


#opens page to populate 20 entries per instance
PAGINATE_BY = 20

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

#limits entries based on number provided
@app.route("/?limit=20")
@app.route("/page/2?limit=20")

#prompts user to login to gain access privileges to delete and edit functions, login required to delete and edit
@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_user_pass():
    user=request.form["User"]
    password=request.form["Password"]
    
#prompts user login using stored e-mail and password, redirects upon failure to provide appropriate information
@app.route("/login", methods=["POST"])
def login_entry():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    return redirect(request.args.get('next') or url_for("entries"))

#allows user to add new entries to page
@app.route("/entry/add", methods=["GET"])
@login_required
def add_entry_get():
    return render_template("add_entry.html")

from flask_login import current_user

@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))

#allows users to acquire entries on an individual numbered basis
@app.route("/entry/<int:id>")
def unique_entry_id(id):
    entry_unid = session.query(Entry).get(id)
    print (entry_unid)
    return render_template("entry_id.html", unique_entry_id=unique_entry_id
    )
    
#edits entries, requires login information to utilize editing feature, retrieves specific entry
@app.route("/entry/<int:id>/edit", methods=["GET"])
@login_required
def entry_id_edit_g(id):
    entry_unid = session.query(Entry).get(id)
    return render_template("entry_id_edit.html", entry_unid=entry_unid
    )

#edits entries, requires login informatino to utilize editing feature, applies edits to entry
@app.route("/entry/<int:id>/edit", methods=["POST"])
@login_required
def entry_id_edit_p(id):
    entry_unid = session.query(Entry).get(id)
    entry_unid.title = request.form["title"]
    entry_unid.content = (request.form["content"])
    
    session.commit()
    return redirect(url_for("entry"))

#deletes entries, requires login information to utilize before deletion   
@app.route("/entry/<int:id>delete", methods=["GET", "POST"])
@login_required
def delete_entry(id):
    entry_unid = session.query(Entry).get(id)
    session.query(Entry).get(id).delete(id)
    session.commit()
    return redirect(url_for('entries'))
    
    return render_template("delete_entry.html")
    
#provides logged user ability to logout
#@app.route("/logout")
#@login.required
#def user_logout(id)