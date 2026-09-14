from flask import Flask,render_template,request,redirect,flash
import json
from datetime import datetime
app=Flask(__name__)
app.secret_key="expense-tracker-secret key"
def load_expenses():
    try:
       with open("expenses.json","r")as  file:
         return json.load(file)
    except FileNotFoundError:
         return[]

@app.route("/")
def home():
    expenses=load_expenses()

    search=request.args.get("search","").lower()
    if search:
        expenses=[
            expense for expense in expenses
            if search in expense["description"].lower()
        ]
    category=request.args.get("category","").lower()
    if category:
            expenses=[
                expense for expense in expenses
                if expense ["category"].lower()==category
            ]
    date=request.args.get("date","").strip()
    if date:
            expense=[
                expense for expense in expenses
                if expense["date"]==date
            ]
    sort=request.args.get("sort","")
      

    if sort == "amount_asc":
            expenses.sort(key=lambda expense: expense["amount"])

    elif sort == "amount_desc":
            expenses.sort(key=lambda expense:expense["amount"],reverse=True)

    elif sort == "date_asc":
             expenses.sort(key=lambda expense:datetime.strptime( expense["date"],"%d-%m-%Y"))

    elif sort == "date_desc":
          expenses.sort(
        key=lambda expense: datetime.strptime(
            expense["date"], "%d-%m-%Y"
        ),
        reverse=True
    )

    total=sum(expense["amount"]for expense in expenses)
    highest=max(expenses,key=lambda expense:float(expense["amount"]))["amount"]if expenses else 0
    average=total/len(expenses)if expenses else 0
    category_totals={}
    for expense in expenses:
        category=expense["category"]
        if category in category_totals:
            category_totals[category]+=expense["amount"]
        else:
            category_totals[category]=expense["amount"]
    return render_template("index.html",
                           expenses=expenses,
                            total=total,
                            highest=highest,
                            average=average,
                            category_totals=category_totals
                          )
@app.route("/add", methods=["POST"])
def add_expenses():
    expenses = load_expenses()

    amount_text = request.form.get("amount", "").strip()
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()
    date = request.form.get("date", "").strip()

    # Check empty fields
    if not amount_text or not category or not description or not date:
        flash("All fields are required.")
        return redirect("/")

    # Check amount
    try:
        amount = float(amount_text)
    except ValueError:
        flash("Amount must be a valid number.")
        return redirect("/")

    # Check negative/zero amount
    if amount <= 0:
        flash("Amount must be greater than 0.")
        return redirect("/")

    # Check date
    try:
        datetime.strptime(date, "%d-%m-%Y")
    except ValueError:
        flash("Date must be in dd-mm-yyyy format.")
        return redirect("/")

    expense = {
        "amount": amount,
        "category": category,
        "description": description,
        "date": date
    }

    expenses.append(expense)

    with open("expenses.json", "w") as file:
        json.dump(expenses, file, indent=4)

    flash("Expense added successfully.")
    return redirect("/")

@app.route("/delete/<int:index>")
def delete_expenses(index):
    expenses=load_expenses()
    if 0<=index<len(expenses):
       expenses.pop(index)

    with open("expenses.json","w")as file:
        json.dump(expenses,file,indent=4)
    return redirect("/")
@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit_expense(index):
    expenses = load_expenses()

    if 0 <= index < len(expenses):
        if request.method == "POST":
            expenses[index]["amount"] = float(request.form["amount"])
            expenses[index]["category"] = request.form["category"]
            expenses[index]["description"] = request.form["description"]
            expenses[index]["date"] = request.form["date"]

            with open("expenses.json", "w") as file:
                json.dump(expenses, file, indent=4)

            return redirect("/")

        return render_template("edit.html", expense=expenses[index])

    return redirect("/")
if __name__=="__main__":
    app.run(debug=True)