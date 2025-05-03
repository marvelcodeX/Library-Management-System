from flask import Flask, render_template, request,flash,redirect,url_for,jsonify
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import secrets




app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
admin_credentials = {
    'admin': 'pass'  # Change to your desired username and password
}

import mysql.connector
def use_database():
    global mycursor
    global cnx
    cnx = mysql.connector.connect(user='root', password='pwd', host='localhost', database='db_name')

   
    mycursor = cnx.cursor()

    sql = "INSERT INTO book (`SL.NO`, `A/c No`, `Title`, `Author`, `Edition/Year`, `Publication`) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (data['sl_no'], data['ac_no'], data['title'], data['author'], data['edition'], data['publication'])

    #val = ("AAAAA", "22222","3333","MySubject")
    mycursor.execute(sql, val)

    cnx.commit()

    print(mycursor.rowcount, "record inserted.")





def use_database1(ac_no):
    global mycursor
    global cnx
    cnx = mysql.connector.connect(user='root', password='pwd', host='localhost', database='db_name')


   
    mycursor = cnx.cursor()

    sql = "DELETE FROM book WHERE `A/C No` = %s "
    val = (ac_no,)

    mycursor.execute(sql, val)

    cnx.commit()

    print(mycursor.rowcount, "record deleted.")







def use_database2(ac_no, data):
    try:
        # Establish the connection
        cnx = mysql.connector.connect(user='root', password='pwd', host='localhost', database='db_name')
        mycursor = cnx.cursor()

        # Get current date for Issue Date and Return Date
        current_date = datetime.now()  # Get the current date
        return_date = current_date + timedelta(days=1)  # Calculate return date

        # Update the book status to 'unavailable' and set return_date
        sql_update = "UPDATE book SET issue_status = 'Unavailable', return_date = %s WHERE `A/c No` = %s"
        mycursor.execute(sql_update, (return_date, ac_no))  # Execute the update query

        # Prepare data for insertion
        sql_insert = "INSERT INTO issue(`Student_Name`, `Reg_no`, `AC_No`, `Title`, `Author`, `Issue_Date`) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (data['sname'], data['reg_no'], ac_no, data['title'], data['author'], current_date.strftime('%Y-%m-%d'), return_date.strftime('%Y-%m-%d'))
        
        mycursor.execute(sql_insert, val)  # Execute the insert query
        cnx.commit()  # Commit the transaction

        print("Book issued successfully.")
    except mysql.connector.Error as db_error:
        print(f"Database error: {db_error}")  # Handle database errors
        raise  # Raise the exception to be caught in the route
    finally:
        if mycursor:
            mycursor.close()  # Close the cursor
        if cnx:
            cnx.close()  # Close the database connection






def use_database3(ac_no):
    global mycursor
    global cnx
    global data

    # Establish the connection
	cnx = mysql.connector.connect(user='root', password='pwd', host='localhost', database='db_name')


    mycursor = cnx.cursor()
    sql_check = "SELECT * FROM issue WHERE `AC_No` = %s"
    mycursor.execute(sql_check, (ac_no,))
    issue_record = mycursor.fetchone()

    # If no record found, the book has not been issued
    if not issue_record:
        print("This book has not been issued, so it cannot be returned.")
        return

    # Update the book status to 'Available' where A/c No matches
    sql_update = "UPDATE book SET issue_status = 'Available', return_date = NULL WHERE `A/c No` = %s"
    mycursor.execute(sql_update, (ac_no,))  # Pass the ac_no to the query

    #Insert into returnb table (assuming data contains all necessary fields)
    sql_insert = "INSERT INTO returnb(`Student_Name`,`Reg_no`,`AC_No`, `Title`, `Author`,  `Return_Date`) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (data['sname'], data['reg_no'], data['ac_no'], data['title'], data['author'], data['date'])

    mycursor.execute(sql_insert, val)  # Execute the insert query

    
    sql_delete = "DELETE FROM issue WHERE `AC_No` = %s"
    val = (ac_no,) 
    mycursor.execute(sql_delete, val)

    # Commit the changes to the database
    cnx.commit()

    print(mycursor.rowcount, "record inserted.")

def check_return_date():
    global mycursor
    try:
        cnx = mysql.connector.connect(user='root', password='pwd', host='localhost', database='db_name')

        mycursor = cnx.cursor(dictionary=True)

        # Query for books that are due tomorrow
        query = """
        SELECT Title, Student_Name, return_date
        FROM issue
        WHERE return_date = CURDATE() + INTERVAL 1 DAY
        """
        mycursor.execute(query)
        books_due_tomorrow = mycursor.fetchall()
        
        print("Books due tomorrow fetched from database:", books_due_tomorrow)  # Debugging output

        mycursor.close()
        cnx.close()

        return books_due_tomorrow  # Always return a list, even if empty

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []  # Return an empty list to avoid undefined issues







def use_database4(data):
    global mycursor
    global cnx
    
    cnx = mysql.connector.connect(user='root', password='pwd', host='localhost', database='db_name')

    mycursor = cnx.cursor(dictionary=True)

    result = None

    if 'sl_no' in data and data['sl_no']:
        sql = "SELECT * FROM book WHERE `SL.NO` = %s"
        val = (data['sl_no'],)
        mycursor.execute(sql, val)
        result = mycursor.fetchall()
    elif 'author' in data and data['author']:
        sql = "SELECT * FROM book WHERE `Author` LIKE %s"
        val = ('%' + data['author'] + '%',)
        mycursor.execute(sql, val)
        result = mycursor.fetchall()

    mycursor.close()
    cnx.close()

    # Generate HTML
    html = "<div style='margin-bottom: 100px;'></div>"
    html += "<table style='border-collapse: collapse; width: 70%;'>\n" 
    html += "<tr style='background-color: #333; color: white;'>\n" 
    html += "<th style='padding: 10px;'>SL.NO</th>\n"
    html += "<th style='padding: 10px;'>A/c No</th>\n" 
    html += "<th style='padding: 10px;'>Title</th>\n" 
    html += "<th style='padding: 10px;'>Author</th>\n"
    html += "<th style='padding: 10px;'>Edition/Year</th>\n"
    html += "<th style='padding: 10px;'>Publication</th>\n"
    html += "<th style='padding: 10px;'>Issue_status</th>\n"
    html += "</tr>\n" 
    
    if result:
        for row in result:
            html += "<tr style='background-color: #f2f2f2;'>\n"
            html += "<td style='padding: 10px;'>{}</td>\n".format(row['SL.NO'])
            html += "<td style='padding: 10px;'>{}</td>\n".format(row['A/c No'])
            html += "<td style='padding: 10px;'>{}</td>\n".format(row['Title'])
            html += "<td style='padding: 10px;'>{}</td>\n".format(row['Author'])
            html += "<td style='padding: 10px;'>{}</td>\n".format(row['Edition/Year'])
            html += "<td style='padding: 10px;'>{}</td>\n".format(row['Publication'])
            html += "<td style='padding: 10px;'>{}</td>\n".format(row['Issue_status'])
            html += "</tr>\n"
        html += "</table>"
    else:
        html += "<p>No results found.</p>"

    return html

    
def use_database5(data):
    import mysql.connector  # Ensure you have the mysql.connector import

    result = None
    try:
        # Connect to the database
        cnx = mysql.connector.connect(user='root', password='pwd', host='localhost', database='db_name')
        mycursor = cnx.cursor(dictionary=True)

        if 'ac_no' in data and data['ac_no']:
            sql = "SELECT * FROM book WHERE `A/c No` = %s"
            val = (data['ac_no'],)
            mycursor.execute(sql, val)
            result = mycursor.fetchall()

    except mysql.connector.Error as err:
        print(f"Error: {err}")  # Print any database errors
    finally:
        # Close the cursor and connection
        if mycursor:
            mycursor.close()
        if cnx:
            cnx.close()

    # Generate HTML
    html = "<div style='margin-bottom: 100px;'></div>"
    html += "<table style='border-collapse: collapse; width: 70%;'>\n" 
    html += "<tr style='background-color: #333; color: white;'>\n" 
    html += "<th style='padding: 10px;'>SL.NO</th>\n"
    html += "<th style='padding: 10px;'>A/c No</th>\n" 
    html += "<th style='padding: 10px;'>Title</th>\n" 
    html += "<th style='padding: 10px;'>Author</th>\n"
    html += "<th style='padding: 10px;'>Edition/Year</th>\n"
    html += "<th style='padding: 10px;'>Publication</th>\n"
    html += "<th style='padding: 10px;'>Issue_status</th>\n"
    html += "</tr>\n" 
    
    if result:
        for row in result:
            html += "<tr style='background-color: #f2f2f2;'>\n"
            html += "<td style='padding: 10px;'>{}</td>\n".format(row['SL.NO'])
            html += "<td style='padding: 10px;'>{}</td>\n".format(row['A/c No'])
            html += "<td style='padding: 10px;'>{}</td>\n".format(row['Title'])
            html += "<td style='padding: 10px;'>{}</td>\n".format(row['Author'])
            html += "<td style='padding: 10px;'>{}</td>\n".format(row['Edition/Year'])
            html += "<td style='padding: 10px;'>{}</td>\n".format(row['Publication'])
            html += "<td style='padding: 10px;'>{}</td>\n".format(row['Issue_status'])
            html += "</tr>\n"
        html += "</table>"
    else:
        html += "<p>No results found.</p>"

    return html






@app.route('/')
def login():
    return render_template('login.html')

@app.route('/admin', methods=['POST'])
def admin_login():
    username = request.form['username']
    password = request.form['password']
    
    if username in admin_credentials and admin_credentials[username] == password:
        return render_template('home.html')  # Redirect to admin page
    else:
        return render_template('login.html', message="Invalid username or password!")
    
@app.route('/user')
def user_page():
    return redirect(url_for('show_user_page'))

@app.route('/user_page')  # change it to reroite to search.html
def show_user_page():
    return render_template('search.html')




@app.route('/add')
def add():
    return render_template('add.html')

@app.route('/add_book', methods=['POST']) 
def add_book(): 
    
    
    global data
    data=request.form 

    use_database()
    ## Return the extracted information 
    print ( "Add book")
    return render_template('home.html')




@app.route('/delete')
def delete():
    return render_template('delete.html')

@app.route('/delete_book', methods=['POST']) 
def delete_book(): 
    ac_no = request.form.get('ac_no')
    
    if ac_no:
	## Return the extracted information 
        use_database1(ac_no,)
	
        print(f"Book name: {ac_no}")
    return render_template('home.html')
@app.route('/issue')
def issue():
    return render_template('issue.html')

@app.route('/issue_book', methods=['POST']) 
def issue_book(): 
    ac_no = request.form.get('ac_no')  # Get account number from form
    data = request.form  # Get the form data
    
    if ac_no:
        try:
            use_database2(ac_no, data)  # Call function to update database
            flash("Book issued successfully.", "success")  # Flash success message
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")  # Flash error message

    return redirect(url_for('home'))





@app.route('/returnb')
def returnb():
    return render_template('returnb.html')

@app.route('/return_book', methods=['POST']) 
def return_book(): 
    
   
    global data
    ac_no = request.form.get('ac_no')
    data=request.form 
    use_database3(ac_no)
    ## Return the extracted information 
    print ( "return book")
    return render_template('home.html')


@app.route('/')
def home():
    books_due = check_return_date()  # This should return a list
    messages = []

    print("Books due from check_return_date:", books_due)  # Debugging output

    if books_due:
        for book in books_due:
            messages.append(f"Reminder: The book '{book['Title']}' has not been returned by '{book['Student_Name']}' and is due tomorrow ({book['return_date']}).")
    else:
        messages.append("No books are due for return tomorrow.")

    print("Messages before rendering:", messages)  # Debugging output
    return render_template('home.html', messages=messages)  # Render the template

@app.route('/check_books_due')
def check_books_due():
    books_due = check_return_date()  # Your function to get due books
    if not books_due:
        return jsonify(books_due=[])

    return jsonify(books_due=books_due)











@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/search_book', methods=['POST'])
def search_book():
    global data
    data = request.form  # Get the form data submitted by the user

    # Determine which function to call based on the input fields
    if 'ac_no' in data and data['ac_no']:  # Check if 'ac_no' exists and is not empty
        table_html = use_database5(data)  # Call the function for valid account number
    else:
        table_html = use_database4(data)  # Call the alternative function

    # Render search.html with the table_html content
    return render_template('search.html', table=table_html)
@app.route('/home')
def s_home():
    return render_template('home.html') 
   





if __name__ == '__main__': 

    app.run(debug=True,host='0.0.0.0',port=8000)

  



