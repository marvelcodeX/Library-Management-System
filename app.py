from flask import Flask, render_template, request
import mysql.connector
from mysql.connector import Error
 #Importing required functions 

import mysql.connector
def use_database():
    global mycursor
    global cnx
    cnx = mysql.connector.connect(user='aastha', password='aastha1',
                              host='localhost',
                              database='LIBRARY')
   
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
    cnx = mysql.connector.connect(user='aastha', password='aastha1',
                              host='localhost',
                              database='LIBRARY')
   
    mycursor = cnx.cursor()

    sql = "DELETE FROM book WHERE `A/C No` = %s "
    val = (ac_no,)

    mycursor.execute(sql, val)

    cnx.commit()

    print(mycursor.rowcount, "record deleted.")






def use_database2(ac_no):
    global mycursor
    global cnx
    global data

    # Establish the connection
    cnx = mysql.connector.connect(user='aastha', password='aastha1',
                                  host='localhost',
                                  database='LIBRARY')
   
    mycursor = cnx.cursor()

    # Update the book status to 'unavailable' and set return_date
    sql_update = "UPDATE book SET Issue_status = 'Unavailable', return_date = CURDATE() + INTERVAL 15 DAY WHERE `A/c No` = %s"
    mycursor.execute(sql_update, (ac_no,))  # Execute the update query

    # Insert into issue table
    sql_insert = "INSERT INTO issue(`Student_Name`,`Reg_no`,`AC_No`, `Title`, `Author`,  `Issue_Date`) VALUES ( %s, %s, %s, %s, %s, %s)"
    val = (data['sname'], data['reg_no'], data['ac_no'], data['title'], data['author'], data['date'])
    
    mycursor.execute(sql_insert, val)  # Execute the insert query
    cnx.commit()  # Commit the transaction
    print("Book issued successfully.")






def use_database3(ac_no):
    global mycursor
    global cnx
    global data

    # Establish the connection
    cnx = mysql.connector.connect(user='aastha', password='aastha1',
                                  host='localhost',
                                  database='LIBRARY')
   
    mycursor = cnx.cursor()

    # Update the book status to 'Available' where A/c No matches
    sql_update = "UPDATE book SET Issue_status = 'Available', return_date = NULL WHERE `A/c No` = %s"
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




def use_database4(data):
    global mycursor
    global cnx
    
    cnx = mysql.connector.connect(
        user='aastha', 
        password='aastha1',
        host='localhost',
        database='LIBRARY'
    )
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
    global mycursor
    global cnx
    
    cnx = mysql.connector.connect(
        user='aastha', 
        password='aastha1',
        host='localhost',
        database='LIBRARY'
    )
    mycursor = cnx.cursor(dictionary=True)

    result = None

    if 'ac_no' in data and data['ac_no']:
        sql = "SELECT * FROM book WHERE `A/c No` = %s"
        val = (data['ac_no'],)
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




app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')




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
    global data
    ac_no = request.form.get('ac_no')
    data=request.form
    
    if ac_no:
        use_database2(ac_no,)
        print(f"Book issued with account number: {ac_no}")

    return render_template('home.html')




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


@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/search_book', methods=['POST'])
def search_book():
    global data
    data = request.form

    # Determine which function to call based on the input fields
    if 'ac_no' in data and data['ac_no']:
        table_html = use_database5(data)
    else:
        table_html = use_database4(data)

    # Render search.html with the table_html content
        return render_template('search.html', table=table_html)
    
   





if __name__ == '__main__': 
	# Run the application on the local development server 
    app.run(debug=True,host='0.0.0.0',port=8000)


#test line ignore