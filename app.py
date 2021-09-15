from flask import Flask, render_template, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, ValidationError, validates , EXCLUDE
from io import BytesIO

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
    filename = db.Column(db.String(300), nullable=False)
    file = db.Column(db.LargeBinary(length = None),nullable= False)

    def __repr__(self) -> str:
        return f'{Users.sno} {Users.name} {Users.email} {Users.contact} {Users.address} {Users.salary}'


class UserSchema(Schema):
    name = fields.String(required=True)
    email = fields.Email(required=True)
    contact = fields.String(required=True)
    address = fields.String(required=True)
    salary = fields.Integer(required=True)
    file = fields.Raw(type = 'file', required=True)

    class Meta:
        unknown = EXCLUDE
    @validates('contact')
    def validate_contact(self, contact):
        if len(contact) != 10:
            raise ValidationError('Contact should have 10 digits')
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
        file =  request.files['file']
        filename = file.filename
        user = Users(name=name, email=email, contact=contact, address=address, salary=salary,filename=filename, file= file.read())
        schema = UserSchema()
        try:
            schema.load(vars(user))
            db.session.add(user)
            db.session.commit()
            user = Users.query.all()
            return render_template("crud.html", users=user)
        except ValidationError as err:
            print(err)
            print(err.messages.get('contact'))
    users = Users.query.all()
    if users:
        return render_template("crud.html", users=users)
    else:
        return render_template("crud.html", users=users)
        print('No records found')

@app.route("/delete/<int:sno>")
def delete(sno):
    user = Users.query.filter_by(sno=sno).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return redirect("/crud")
    else:
        print('No records found')



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
        schema = UserSchema()
        print(request.files)
        if request.files['file'].filename == '':
            user = Users(name=name, email=email, contact=contact, address=address, salary=salary)
            try:
                schema.load(vars(user))
                u = Users.query.filter_by(sno=sno).first()
                if u:
                    u.name = name
                    u.email = email
                    u.contact = contact
                    u.address = address
                    u.salary = salary
                    u.file = u.file
                    u.filename = u.filename
                    db.session.add(u)
                    db.session.commit()
                    return redirect("/crud")
                else:
                    print('No record found')
            except ValidationError as err:
                print(err.messages.get('contact'))
        else:
            file = request.files['file']
            filename = file.filename
            user = Users(name=name, email=email, contact=contact, address=address, salary=salary, filename=filename,file=file.read())
            try:
                schema.load(vars(user))
                u = Users.query.filter_by(sno=sno).first()
                if u:
                    u.name = name
                    u.email = email
                    u.contact = contact
                    u.address = address
                    u.salary = salary
                    if u.file:
                        u.file = file
                        u.filename = filename
                    db.session.add(u)
                    db.session.commit()
                    return redirect("/crud")
                else:
                    print('No record found')
            except ValidationError as err:
                print(err.messages.get('contact'))
    user = Users.query.filter_by(sno=sno).first()
    if user:
        return render_template("update.html", user=user)
    else:
        print('No records found')

@app.route("/filedownload/<int:sno>", methods=['POST', 'GET'])
def filedownload(sno):
    if request.method == 'GET':
        user = Users.query.filter_by(sno=sno).first()
        return send_file(BytesIO(user.file), attachment_filename=user.filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
