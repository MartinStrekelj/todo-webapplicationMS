from flask import Flask, render_template, request, redirect, url_for, make_response
from models import db, User, List, Item
import hashlib
import uuid

app = Flask(__name__)
db.create_all()

def findUser(session_token):
    user = db.query(User).filter_by(session_token=session_token).first()
    return user


@app.route("/")
def index():
    session_token = request.cookies.get("session_token")
    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
        userID = user.id
        todo_lists = db.query(List).all()
        if len(todo_lists) > 0 :
            lists = db.query(List).filter_by(uid = userID)
            return render_template("dashboard.html", user=user, lists=lists)
        return render_template("dashboard.html", user=user)
    else:
        user = None
        return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        username = request.form.get("username")
        email    = request.form.get("user-email")
        password = request.form.get("password")
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()


        user = User(username = username,
                    email= email,
                    password= hashed_pw)

        db.add(user)
        db.commit()

        return redirect(url_for("index"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")


    elif request.method== "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()

        # pregled ali user obstaja
        user = db.query(User).filter_by(username=username).first()

        if user:
            if hashed_pw == user.password:
                #Creating session token
                session_token = str(uuid.uuid4())
                user.session_token = session_token
                # db update with token
                db.add(user)
                db.commit()
                # cookie response
                response = make_response(redirect(url_for("index")))
                response.set_cookie("session_token", session_token, httponly=True, samesite="Strict")
                return response

            else:
                return render_template("failedlogin.html")
        else:
            return render_template("failedlogin.html")


@app.route("/edit", methods=["GET", "POST"])
def edit():

    # find user
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        return render_template("edit.html", user=user)


    elif request.method == "POST":

        #username change
        username = request.form.get("username")
        if len(username) > 0:
            user.username = username

        #email change
        email    = request.form.get("user-email")
        if len(email) > 0:
            user.email = email

        #password change
        password = request.form.get("password")
        passwordtest = request.form.get("password-repeat")
        if (len(password) > 0) and (password == passwordtest):
            hashed_pw = hashlib.sha256(password.encode()).hexdigest()
            user.password = hashed_pw

        db.add(user)
        print("commit")
        db.commit()

        return redirect((url_for("edit")))

@app.route("/logout", methods = ["GET"])
def logout():
    response = make_response(redirect(url_for("index")))
    response.set_cookie("session_token", "", expires=0)
    return response

@app.route("/addList", methods=["GET", "POST"])
def addList():
    # find user
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    if request.method == "GET":
       return render_template("addlist.html", user=user)
    if request.method == "POST":
        listName = request.form.get("list-name")
        uid = user.id
        itemlist = List(list_name = listName,
                        uid = uid)

        print(uid, listName)

        db.add(itemlist)
        db.commit()

        return (redirect(url_for("index")))

@app.route("/<lists_id>" , methods=["GET"])
def displayList(lists_id):
    # find user
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    userID = user.id
    # find list
    itemList = db.query(List).get(int(lists_id))
    listID = itemList.id
    #find all lists
    lists = db.query(List).filter_by(uid=userID)

    #find all notes
    items = db.query(Item).filter_by(lid=listID)

    return render_template("showlist.html", itemlist = itemList, user = user, lists = lists, items = items )

    # return render_template("showlist.html", itemlist = itemList, user = user, lists = lists )

@app.route("/note/<item_id>", methods=["GET"])
def strikeItem(item_id):

    item = db.query(Item).get(int(item_id))
    itemLID = item.lid
    if item.active == 1:
        item.active = 0
    else:
        item.active = 1

    db.add(item)
    db.commit()

    return redirect("/{0}".format(itemLID))


@app.route("/<list_id>/rename", methods=[ "GET" , "POST"])
def renameList(list_id):
    itemlist = db.query(List).get(int(list_id))
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    if request.method == "GET":
       return render_template("renamelist.html", itemlist=itemlist, user=user)
    if request.method == "POST":
        newListName = request.form.get("newListName")
        itemlist.list_name = newListName

        db.add(itemlist)
        db.commit()
        return redirect(url_for("index"))


@app.route("/<list_id>/delete", methods=["GET", "POST"])
def deleteList(list_id):
    itemlist = db.query(List).get(int(list_id))
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    if request.method == "GET":
       return render_template("deletelist.html", itemlist=itemlist, user=user)
    if request.method == "POST":
        items = db.query(Item).filter_by(lid=itemlist.id)
        for item in items:
                db.delete(item)
        db.delete(itemlist)
        db.commit()
        return redirect(url_for("index"))

@app.route("/<list_id>/add", methods=["GET", "POST"])
def addNote(list_id):
    itemlist = db.query(List).get(int(list_id))
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        return(render_template("addnote.html", itemlist=itemlist, user=user))

    if request.method == "POST":
        title = request.form.get("todo_title")
        deadline = request.form.get("todo_deadline")
        text = request.form.get("todo_text")
        active = 1
        listID = itemlist.id

        item = Item(title = title,
                    deadline = deadline,
                    text  = text,
                    active = active,
                    lid = listID)
        db.add(item)
        db.commit()

        return redirect("/{0}".format(itemlist.id))

@app.route("/<list_id>/deletenotes", methods=["GET"])
def deleteNotes(list_id):
    itemlist = db.query(List).get(int(list_id))
    items = db.query(Item).filter_by(lid = itemlist.id)
    for item in items:
        if not item.active:
            db.delete(item)

    db.commit()

    return redirect("/{0}".format(itemlist.id))


if __name__ == "__main__":
    app.run()