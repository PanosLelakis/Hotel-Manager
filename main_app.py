#Panos Lelakis, ECE University of Patras, up1083712

#import required libraries
from flask import Flask, render_template, request, session, flash, redirect, url_for
from datetime import timedelta, datetime, date
from flask_sqlalchemy import SQLAlchemy

#setting up the database
app = Flask(__name__)
app.secret_key = "Secret Key 28" #secret key
app.permanent_session_lifetime = timedelta(hours=2)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///reservations.sqlite3" #database file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False #to avoid errors
app.config["TEMPLATES_AUTO_RELOAD"] = True

db = SQLAlchemy(app)

#each of the following classes corresponds to one table, with which shares the same name
class Reservation(db.Model): #contents of Reservation table
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), default='') #name of client
    room = db.Column(db.String(10), default='') #number of room
    date_from = db.Column(db.String(30), default='') #starting date of reservation
    date_to = db.Column(db.String(30), default='') #ending date of reservation
    notes = db.Column(db.String(300), default='') #extra notes (not required)

    def __init__(self, name, room, date_from, date_to, notes):
        self.name = name
        self.room = room
        self.date_from = date_from
        self.date_to = date_to
        self.notes = notes

class Client(db.Model): #contents of Client table
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), default='') #name of client
    age = db.Column(db.Integer, default=0) #age of client
    phone = db.Column(db.Integer, default=0) #phone number of client
    email = db.Column(db.String(50), default='') #email address of client

    def __init__(self, name, age, phone, email):
        self.name = name
        self.age = age
        self.phone = phone
        self.email = email

class Webcount(db.Model): #contents of Webcount table
    id = db.Column(db.Integer, primary_key = True)
    count = db.Column(db.Integer, default=0) #value of website view counter

    def __init__(self, count):
        self.count = count

class Room(db.Model): #contents of Room table
    id = db.Column(db.Integer, primary_key = True)
    room = db.Column(db.String, default='') #number of room
    dates = db.Column(db.String, default='') #dates reserved

    def __init__(self, room, dates):
        self.room = room
        self.dates = dates

@app.route("/home") #home page
def home():
    if not Webcount.query.filter_by(id=1).first() :
        #checks if there is already a value for the website view counter
        #if there isn't, it creates a row in the Webcount table, and sets the counter's value to zero
        db.session.add(Webcount(0))
        db.session.commit()

    #add one to the website view counter's value
    Webcount.query.filter_by(id=1).first().count += 1
    count = Webcount.query.filter_by(id=1).first().count
    db.session.commit() 

    #python passes the count value to the html file, so that we can view the counter's value in the home page
    return render_template("home.html", values=count)

@app.route("/contact") #contact page
def contact():
    return render_template("contact.html")

@app.route("/help") #help page
def help():
    return render_template("help.html")

@app.route("/view_reservations") #page for VIEWING reservations (reads the contents of Reservation table)
def view_reservations():
    #python passes the whole Reservation table to the html file, so that we can view a list of all the reservations that have been made
    return render_template("view_reservations.html", values=Reservation.query.all())

@app.route("/view_clients") #page for VIEWING clients (reads the contents of Client table)
def view_clients():
    #python passes the whole Client table to the html file, so that we can view a list of all the clients that have made a reservation
    return render_template("view_clients.html", values=Client.query.all())

@app.route("/view_rooms") #page for VIEWING rooms (reads the contents of Room table)
def view_rooms():
    #python passes the whole Room table to the html file, so that we can view a list of which dates are reserved for each of the hotel's rooms
    return render_template("view_rooms.html", values=Room.query.all())

@app.route("/add_reservation", methods=["POST", "GET"]) #page for ADDING a reservation (writes in the Reservation table)
def add_reservation():

    if request.method == "POST":

        #get name of client
        name = request.form.get("name")
        session["name"] = name

        #get number of room
        room = request.form.get("room")
        session["room"] = room

        #get starting date of reservation
        date_from = request.form.get("date_from")
        session["date_from"] = date_from

        #get ending date of reservation
        date_to = request.form.get("date_to")
        session["date_to"] = date_to

        #get extra notes (not required)
        notes = request.form.get("notes")
        session["notes"] = notes

        #get age of client
        age = request.form.get("age")
        session["age"] = age

        #get phone number of client
        phone = request.form.get("phone")
        session["phone"] = phone

        #get email address of client
        email = request.form.get("email")
        session["email"] = email

        if not name or not room or not date_from or not date_to:
            #checks if all required fields have been filled
            flash("ERROR: Please fill all required fields")
            return redirect(url_for("add_reservation"))

        #the following lines of code check if the dates for the reservation are acceptable

        datefrom = date_from.split("-") #year is the 1st element, month is the 2nd, and day is the 3rd
        dateto = date_to.split("-") #year is the 1st element, month is the 2nd, and day is the 3rd

        yearfrom = int(datefrom[0]) #yearfrom is the year given in the starting date of reservation
        monthfrom = int(datefrom[1]) #monthfrom is the month given in the starting date of reservation
        dayfrom = int(datefrom[2]) #dayfrom is the day (number of day) given in the starting date of reservation

        yearto = int(dateto[0]) #yearto is the year given in the ending date of reservation
        monthto = int(dateto[1]) #monthto is the month given in the ending date of reservation
        dayto = int(dateto[2]) #dayto is the the day (number of day) given in the ending date of reservation

        if date_from == date_to:
            #checks if the starting date of reservation is the same as the ending date of reservation

            flash("ERROR: Please select different day")
            return redirect(url_for("add_reservation"))

        elif yearfrom < datetime.now().year or yearto < datetime.now().year or (yearfrom < datetime.now().year and yearto < datetime.now().year) or yearfrom > yearto:
        #checks if:
            #1. year in starting date of reservation is older than the year in pc's clock
            #2. year in ending date of reservation is older than the year in pc's clock
            #3. both the first and second are true
            #4. year in ending date of reservation is older than year in starting date of reservation

            flash("ERROR: Please select acceptable year")
            return redirect(url_for("add_reservation"))

        elif (yearto-yearfrom) > 1 :
            #checks if the reservation lasts for more than 1 year
            
            flash("ERROR: You were about to reserve this room for more than 1 whole year - Are you planning on making this room your damn grave or what?...")
            return redirect(url_for("add_reservation"))

        elif Reservation.query.filter_by(name=name).first():
            #checks if there is already a reservation under the exact same name of client

            flash("ERROR: Another reservation exists under this name")
            return redirect(url_for("add_reservation"))

        else:

            entry_period = [] #help: https://stackoverflow.com/questions/993358/creating-a-range-of-dates-in-python
                            #Specifically: Get range of dates between specified start and end date (Optimized for time & space complexity)
                
            start = datetime.strptime(date_from, "%Y-%m-%d") #we force a specific date format: year-month-day, for example 2021-6-18
            end = datetime.strptime(date_to, "%Y-%m-%d")
            date_generated = [start + timedelta(days=x) for x in range(0, (end-start).days)]

            #the last day of the reservation isn't added, because this is the day in which the client will leave the room, so the room will actually be free for the rest of the day
            #IF we wanted to add the last day as well: date_generated = [start + timedelta(days=x) for x in range(0, (end-start).days)+1]

            for a in date_generated:
                entry_period.append(a.strftime("%Y-%m-%d"))

            d = Room.query.filter_by(room=room).first()

            if not d: #if there hasn't been a reservation for this room already, there is no need to check the dates
                db.session.add(Room(room, '')) #add data to the Room table (creates a new row, because there hasn't been a reservation for this room)
                db.session.commit()

            else: #else, it is vital to check if the dates from input collide with already reserved dates for the specific room

                existing_dates = d.dates.split(",")
            
                for k in entry_period:
                    if k in existing_dates:
                        flash("ERROR: This room is already booked for this time period")
                        return redirect(url_for("add_reservation"))
                        break

            flash("Added reservation successfully")
            entry = Reservation(name, room, date_from, date_to, notes) #add data to the Reservation table (creates a new row)
            entry2 = Client(name, age, phone, email) #add data to the Client table (creates a new row)
            db.session.add(entry)
            db.session.add(entry2)

            t = Room.query.filter_by(room=room).first() #search for the number of room in the Room table
            for q in entry_period:
                t.dates = t.dates + "," + q #add the dates of the new reservation to the list of the already-reserved dates for the room
                db.session.commit()

            db.session.commit() #commit (save) changes to the database file

        return render_template("add_reservation.html")
    else:
        return render_template("add_reservation.html")

@app.route("/delete_reservation", methods=["POST", "GET"]) #page for DELETING a reservation (edits the Reservation table)
def delete_reservation():
    if request.method == "POST":
        #get the name of the client, of which the reservation we want to delete
        name = request.form.get("name")
        session["name"] = name

        found_name = Reservation.query.filter_by(name=name).first() #searcb for the entered name in the Reservation table

        if found_name: #if there is a reservation under the entered name

            room = found_name.room #room is the number of room reserved by the client
            date_from = found_name.date_from #date_from is the starting date of the reservation we want to delete
            date_to = found_name.date_to #date_to is the ending date of the reservation we want to delete

            start = datetime.strptime(date_from, "%Y-%m-%d")
            end = datetime.strptime(date_to, "%Y-%m-%d")
            date_generated = [start + timedelta(days=x) for x in range(0, (end-start).days)]

            entry_period = [] #entry_period will contain the reserved dates to be deleted
            for a in date_generated:
                entry_period.append(a.strftime("%Y-%m-%d"))

            temp_list = [] #temp_list will contain the reserved dates that the room will have AFTER the deletion of the reservation
            temp_list = Room.query.filter_by(room=room).first().dates.split(",")

            for c in entry_period:
                try:
                    temp_list.remove(c) #remove the reserved dates to be deleted from temp_list
                except ValueError: #if there were no dates to be deleted, a ValueError message would pop up, so with this exception we just bypass it
                    pass
 
            Room.query.filter_by(room=room).first().dates = '' #empties the list of the reserved dates for the room
            db.session.commit()

            if temp_list: #if there are reserved dates left after the deletion of the reservation (if temp_list isn't empty)
                for q in temp_list:
                    Room.query.filter_by(room=room).first().dates = Room.query.filter_by(room=room).first().dates + "," + q #add the reserved dates left in the list of the reserved dates for the room
                    db.session.commit()

            db.session.delete(found_name) #delete data from Reservation table
            db.session.commit() #commit (save) changes to the database file
            
            flash("Reservation deleted successfully")

        else: #if there ISN'T a reservation under the entered name
            flash("ERROR: Couldn't find reservation under this name")
            return redirect(url_for("delete_reservation"))

        return render_template("delete_reservation.html")
    else:
        return render_template("delete_reservation.html")

@app.route("/delete_client", methods=["POST", "GET"]) #page for DELETING a client (edits the Client table)
def delete_client():
    if request.method == "POST":
        #get the name of the client, of which the info we want to delete from the database
        name = request.form.get("name")
        session["name"] = name

        found_name = Client.query.filter_by(name=name).first() #search for the entered name in the Client table

        if found_name: #if the entered name is found in the Client table

            found_name_res = Reservation.query.filter_by(name=name).first() #search for the reservation corresponding to the entered name

            if found_name_res: #if there is a reservation under entered name
                flash("ERROR: Reservation exists under this name. Delete reservation first.")
                return redirect(url_for("delete_client"))

            else: #if there ISN'T a reservation under entered name
                db.session.delete(found_name)
                db.session.commit()
                
                flash("Client deleted successfully")
                return redirect(url_for("delete_client"))

        else: #if the entered name ISN'T found in the Client table
            flash("ERROR: Couldn't find client with this name")
            return redirect(url_for("delete_client"))

        return render_template("delete_client.html")
    else:
        return render_template("delete_client.html")


if __name__ == "__main__":
    db.create_all() #create database (if it does not exist) and all tables
    app.run(debug=True, use_reloader=False) #debug=True to update page without restarting python (useful if we edit the html files only, doesn't update automatically if we edit the python file)
                                            #use_reloader=False so that when an error has occured, an error page is loaded that contains info about the problem
