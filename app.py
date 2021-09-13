from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, ValidationError, validates

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mboopathi@localhost/flask'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Users(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    contact = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(50), nullable=False)
    salary = db.Column(db.Integer, nullable=False)

    def __repr__(self) -> str:
        return f'{Users.sno} {Users.name} {Users.email} {Users.contact} {Users.address} {Users.salary}'


class UserSchema(Schema):
    name = fields.String(required=True)
    email = fields.Email(required=True)
    contact = fields.String(required=True)
    address = fields.String(required=True)
    salary = fields.Integer(required=True)

    @validates('contact')
    def validate_contact(self, contact):
        if len(contact) != 10:
            raise ValidationError('Your contact should have 10 digits')
        if contact.isdecimal() == False:
            raise ValidationError('In contact only digits are allowed')


@app.route("/")
def start():
    return render_template("index.html")


@app.route("/crud", methods=['POST', 'GET'])
def crud():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']
        address = request.form['address']
        salary = request.form['salary']
        users = Users(name=name, email=email, contact=contact, address=address, salary=salary)
        schema = UserSchema()
        try:
            schema.validate(vars(users))
        except ValidationError as err:
            print(err)
        db.session.add(users)
        db.session.commit()
    users = Users.query.all()
    return render_template("crud.html", users=users)


@app.route("/delete/<int:sno>")
def delete(sno):
    try:
        user = Users.query.filter_by(sno=sno).first()
    except ValidationError as err:
        print(err)
    db.session.delete(user)
    db.session.commit()
    return redirect("/crud")


@app.route("/add")
def add():
    return render_template("index.html")


@app.route("/update/<int:sno>", methods=['POST', 'GET'])
def update(sno):
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']
        address = request.form['address']
        salary = request.form['salary']
        users = Users(name=name, email=email, contact=contact, address=address, salary=salary)
        schema = UserSchema()
        try:
            schema.validate(vars(users))
            u = Users.query.filter_by(sno=sno).first()
            schema.validate(vars(u))
            u.name = name
            u.email = email
            u.contact = contact
            u.address = address
            u.salary = salary
        except ValidationError as err:
            print(err)
        db.session.add(u)
        db.session.commit()
        return redirect("/crud")
    try:
        user = Users.query.filter_by(sno=sno).first()
    except ValidationError as err:
        print(err)
    return render_template("update.html", user=user)


if __name__ == "__main__":
    app.run(debug=True)
