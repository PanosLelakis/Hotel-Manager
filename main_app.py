from flask import Flask, render_template, request, session, flash, redirect, url_for
from datetime import timedelta, datetime, date
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "Lelos IV O Megaloprephs" #secret key
app.permanent_session_lifetime = timedelta(minutes=5)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservations.sqlite3' #database file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False #to avoid errors

db = SQLAlchemy(app)

class reservations(db.Model): #contents of reservations table
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), default='')
    room = db.Column(db.String(10), default='')
    date_from = db.Column(db.String(30), default='')
    date_to = db.Column(db.String(30), default='')
    notes = db.Column(db.String(300), default='')

    def __init__(self, name, room, date_from, date_to, notes):
        self.name = name
        self.room = room
        self.date_from = date_from
        self.date_to = date_to
        self.notes = notes

class clients(db.Model): #contents of clients table
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), default='')
    age = db.Column(db.Integer, default=0)
    phone = db.Column(db.Integer, default=0)
    email = db.Column(db.String(50), default='')

    def __init__(self, name, age, phone, email):
        self.name = name
        self.age = age
        self.phone = phone
        self.email = email

class rooms(db.Model): #contents of rooms table
    id = db.Column(db.Integer, primary_key = True)
    room = db.Column(db.String, default='')
    dates = db.Column(db.String, default='')
##    description = db.Column(db.String(300), default='')
##    price = db.Column(db.Float, default=0.00)

    def __init__(self, room, dates):
        self.room = room
        self.dates = dates
        
##    def __init__(self, room, availability, description, price):
##        self.availability = availability
##        self.description = description
##        self.price = price

@app.route("/home") #home page
def home():
    return render_template("home.html")

@app.route("/contact") #contact page
def contact():
    return render_template("contact.html")

@app.route("/help") #help page
def help():
    return render_template("help.html")

@app.route("/view_reservations") #page for VIEWING reservations (reads the contents of reservations table)
def view_reservations():
    return render_template("view_reservations.html", values=reservations.query.all())

@app.route("/view_clients") #page for VIEWING clients (reads the contents of clients table)
def view_clients():
    return render_template("view_clients.html", values=clients.query.all())

@app.route("/view_rooms") #page for VIEWING rooms (reads the contents of rooms table)
def view_rooms():
    return render_template("view_rooms.html", values=rooms.query.all())

@app.route("/add_reservation", methods=["POST", "GET"]) #page for ADDING a reservation (writes in the reservations table)
def add_reservation():
    if request.method == "POST":

        name = request.form.get("name")
        session["name"] = name
        room = request.form.get("room")
        session["room"] = room
        date_from = request.form.get("date_from")
        session["date_from"] = date_from
        date_to = request.form.get("date_to")
        session["date_to"] = date_to
        notes = request.form.get("notes")
        session["notes"] = notes

        age = request.form.get("age")
        session["age"] = age
        phone = request.form.get("phone")
        session["phone"] = phone
        email = request.form.get("email")
        session["email"] = email

        datefrom = date_from.split("-") #year is the 1st element, month is the 2nd, and day is the 3rd
        dateto = date_to.split("-") #year is the 1st element, month is the 2nd, and day is the 3rd

        yearfrom = int(datefrom[0])
        monthfrom = int(datefrom[1])
        dayfrom = int(datefrom[2])

        yearto = int(dateto[0])
        monthto = int(dateto[1])
        dayto = int(dateto[2])

        entry_period = [] #help: https://stackoverflow.com/questions/993358/creating-a-range-of-dates-in-python
                        #Specifically: Get range of dates between specified start and end date (Optimized for time & space complexity)
                
        start = datetime.strptime(date_from, "%Y-%m-%d")
        end = datetime.strptime(date_to, "%Y-%m-%d")
        date_generated = [start + timedelta(days=x) for x in range(0, (end-start).days)]

        for a in date_generated:
            entry_period.append(a.strftime("%Y-%m-%d"))

        d = rooms.query.filter_by(room=room).first()

        if not d: #if there hasn't been a reservation for this room already, there is no need to check the dates
            db.session.add(rooms(room, ''))
            db.session.commit()

            r = rooms.query.filter_by(room=room).first()

            for i in entry_period:
                r.dates = r.dates + "," + i
                db.session.commit()

        else: #else, it is vital to check if the dates from input collide with already reserved dates for the specific room

            existing_dates = d.dates.split(",")
            
            for k in entry_period:
                if k in existing_dates:
                    flash("ERROR: This room is already booked for this time period")
                    return redirect(url_for("add_reservation"))
                    break

        #found_room = reservations.query.filter_by(room=room).first()

        if yearfrom == yearto and monthfrom == monthto and dayfrom == dayto:
            flash("ERROR: Please select different day")
            return redirect(url_for("add_reservation"))

        elif yearfrom < datetime.now().year or yearto < datetime.now().year or (yearfrom < datetime.now().year and yearto < datetime.now().year) or yearfrom > yearto:
            flash("ERROR: Please select acceptable year")
            return redirect(url_for("add_reservation"))

##        elif found_room: #help: https://stackoverflow.com/questions/993358/creating-a-range-of-dates-in-python
##                        #Specifically: Get range of dates between specified start and end date (Optimized for time & space complexity)
##
##            fr_period = []
##
##            frstart = datetime.strptime(found_room.date_from, "%Y-%m-%d")
##            frend = datetime.strptime(found_room.date_to, "%Y-%m-%d")
##            frdate_generated = [frstart + timedelta(days=y) for y in range(0, (frend-frstart).days)]
##
##            for b in frdate_generated:
##                fr_period.append(b.strftime("%Y-%m-%d"))
##
##            flash("ERROR: This room is already booked for this time period")
##            return redirect(url_for("add_reservation"))

        else:
            flash("Added reservation successfully")
            entry = reservations(name, room, date_from, date_to, notes)
            entry2 = clients(name, age, phone, email)
            db.session.add(entry)
            db.session.add(entry2)

            t = rooms.query.filter_by(room=room).first()
            for q in entry_period:
                t.dates = t.dates + "," + q
                db.session.commit()

            db.session.commit()

        return render_template("add_reservation.html")
    else:
        return render_template("add_reservation.html")

@app.route("/delete_reservation", methods=["POST", "GET"]) #page for DELETING a reservation (edits the reservations table)
def delete_reservation():
    if request.method == "POST":
        name_or_room = request.form.get("name_or_room")
        session["name_or_room"] = name_or_room

        found_name = reservations.query.filter_by(name=name_or_room).first()
        found_room = reservations.query.filter_by(room=name_or_room).first()

        if found_name:

            db.session.delete(found_name)
            db.session.commit()
            
            flash("Reservation deleted successfully")
            return redirect(url_for("delete_reservation"))

        elif found_room:

            db.session.delete(found_room)
            db.session.commit()
            
            flash("Reservation deleted successfully")
            return redirect(url_for("delete_reservation"))

        else:
            flash("ERROR: Couldn't find reservation under this name or room")
            return redirect(url_for("delete_reservation"))

        return render_template("delete_reservation.html")
    else:
        return render_template("delete_reservation.html")

@app.route("/delete_client", methods=["POST", "GET"]) #page for DELETING a client (edits the clients table)
def delete_client():
    if request.method == "POST":
        name = request.form.get("name")
        session["name"] = name

        found_name = clients.query.filter_by(name=name).first()

        if found_name:

            found_name_res = reservations.query.filter_by(name=name).first()

            if found_name_res:
                flash("ERROR: Reservation exists under this name. Delete reservation first.")
                return redirect(url_for("delete_client"))

            else:
                db.session.delete(found_name)
                db.session.commit()
                
                flash("Client deleted successfully")
                return redirect(url_for("delete_client"))

        else:
            flash("ERROR: Couldn't find client with this name")
            return redirect(url_for("delete_client"))

        return render_template("delete_client.html")
    else:
        return render_template("delete_client.html")


if __name__ == "__main__":
    db.create_all() #create database and all tables
    app.run(debug=True, use_reloader=False) #debug=True to update page without restarting python, use_reloader=Flase to avoid errors
