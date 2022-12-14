import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
bp = Blueprint('auth', __name__, url_prefix = '/auth')

@bp.route("/register", methods = ['GET', 'POST'])
def register(): 
    if request.method == 'POST': 
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        if not username: 
            error = "Username is required"
        elif not password: 
            error = "Password is required"
        
        if error is None: 
            try: 
                db.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, generate_password_hash(password)))
                db.commit(), 
            except db.IntegrityError: 
                error = f"User {username} is already registered"
            
        if error is None:  
            return redirect(url_for("auth.login"))
        else: 
            flash(error)
    else: 
        return render_template("auth/register.html")

@bp.route("/login", methods = ["POST", "GET"])
def login(): 
    if request.method == "POST": 
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        user = db.execute("SELECT * FROM user WHERE username = ?", (request)).fetchone()
        
        if user is None or not check_password_hash(user["password"], password): 
            flash("Invalid credential")
        else: 
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("/index"))
    else: 
        return render_template("auth/login.html")

@bp.before_app_request
def load_logged_in_user():     
    user_id = session.get('user_id')
    db = get_db()
    if user_id is None: 
        g.user = None
    else: 
        g.user = db.execute("SELECT * FROM user WHERE id = ?", (user_id)).fetchone()
    
@bp.route("logout")
def logout(): 
    session.clear() 
    return redirect(url_for("login"))
    
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs): 
        if g.user is None: 
            return redirect(url_for("auth.login"))
        else: 
            return view(**kwargs)   
    return wrapped_view

                