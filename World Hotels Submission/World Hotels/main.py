from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL 
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'SecretPass'

# Database connection configuration
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'RandomPassword'
app.config['MYSQL_DB'] = 'world_hotels'

mysql = MySQL(app)

@app.route('/')
def index():
    # Display the login page
    return render_template("LoginPage.html")

@app.route('/Main')
def main():
    # Fetch and display hotels from the database
    mycursor = mysql.connection.cursor()
    mycursor.execute('SELECT * FROM hotels')
    hotels = mycursor.fetchall()
    mycursor.close()
    return render_template("MainPage.html", hotels=hotels)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # User login functionality
    if request.method == 'POST':
        Email = request.form['Email']
        Password = request.form['Password']

        mycursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        mycursor.execute("SELECT * FROM customers WHERE Email=%s AND Password=%s", (Email, Password))
        user = mycursor.fetchone()
        mycursor.close()

        if user:
            session['loggedin'] = True
            session['CustomerID'] = user['CustomerID']
            session['Email'] = user['Email']
            session['Password'] = user['Password']
            return redirect(url_for('main'))
        else:
            flash('Login Failed. Please check your email and password.')
            return redirect(url_for('index'))

    return render_template('LoginPage.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # User registration functionality
    if request.method == 'POST':
        Email = request.form['Email']
        Password = request.form['Password']

        mycursor = mysql.connection.cursor()
        try:
            mycursor.execute("INSERT INTO customers (Email, Password) VALUES (%s, %s)", (Email, Password))
            mysql.connection.commit()
            mycursor.close()

            flash('Registration successful!')
            return redirect(url_for('login'))
        except Exception as err:
            mycursor.close()
            flash(f"Error: {err}")
            return redirect(url_for('register'))

    return render_template('registerpage.html')

@app.route('/booking/<HotelID>')
def book(HotelID):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM Hotels WHERE HotelID = %s' , (HotelID,))
    rows = cursor.fetchone()

    return render_template("BookingPage.html", rows=rows)

@app.route('/booking/<int:HotelID>/bookingconfirmation', methods=['GET', 'POST'])
def bookingconfirmation(HotelID):
    if 'CustomerID' in session:
        CustomerID = session['CustomerID']

        if request.method == 'POST' and 'CheckInDate' in request.form and 'CheckOutDate' in request.form:
            CheckInDate = request.form['CheckInDate']
            CheckOutDate = request.form['CheckOutDate']

            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO bookings(CustomerID, CheckInDate, CheckOutDate, HotelID) VALUES(%s, %s, %s, %s)',
               (CustomerID, CheckInDate, CheckOutDate, HotelID))
            mysql.connection.commit()
            cursor.execute('SELECT * FROM bookings WHERE CustomerID = %s AND HotelID = %s AND CheckInDate = %s AND CheckOutDate = %s', (CustomerID, HotelID, CheckInDate, CheckOutDate))

            booking = cursor.fetchone()
        else:
            booking = None  # Define booking variable as None if the form is not submitted

        return render_template("BookingConfirmation.html", booking=booking)
    else:
        flash('Please log in to book a hotel.', 'error')
        return redirect(url_for('login'))


@app.route('/confirmation')
def confirmation():
    return render_template('BookingConfirmation.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    # User login functionality
    if request.method == 'POST':
        Email = request.form['Email']
        Password = request.form['Password']

        mycursor = mysql.connection.cursor()
        mycursor.execute("SELECT * FROM Admins WHERE Email=%s AND Password=%s", (Email, Password))
        user = mycursor.fetchone()
        mycursor.close()

        if user:
            return redirect(url_for('admin'))
        else:
            flash('Login Failed. Please check your email and password.')
            return redirect(url_for(''))

    return render_template('admin_login.html')

@app.route('/admin/view_bookings')
def view_bookings():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Bookings")
    bookings = cursor.fetchall()
    cursor.close()
    return render_template('admin_bookings.html', bookings=bookings)

@app.route('/admin/view_users')
def view_users():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Customers")
    users = cursor.fetchall()
    cursor.close()
    return render_template('admin_users.html', users=users)

@app.route('/admin/view_hotels')
def view_hotels():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Hotels")
    hotels = cursor.fetchall()
    cursor.close()
    return render_template('admin_hotels.html', hotels=hotels)

# Route to edit user
@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE Customers SET Email=%s, Password=%s WHERE CustomerID=%s", (email, password, user_id))
        mysql.connection.commit()
        cursor.close()
        
        flash('User details updated successfully!', 'success')
        return redirect(url_for('view_users'))
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Customers WHERE CustomerID = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        return render_template('edit_user.html', user=user)

# Route to delete user
@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Customers WHERE CustomerID=%s", (user_id,))
    mysql.connection.commit()
    cursor.close()
    
    flash('User deleted successfully!', 'success')
    return redirect(url_for('view_users'))

# Route to edit hotel
@app.route('/admin/edit_hotel/<int:hotel_id>', methods=['GET', 'POST'])
def edit_hotel(hotel_id):
    if request.method == 'POST':
        location = request.form['location']
        on_peak_price = request.form['on_peak_price']
        off_peak_price = request.form['off_peak_price']
        
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE Hotels SET Location=%s, OnPeakPrice=%s, OffPeakPrice=%s WHERE HotelID=%s", (location, on_peak_price, off_peak_price, hotel_id))
        mysql.connection.commit()
        cursor.close()
        
        flash('Hotel details updated successfully!', 'success')
        return redirect(url_for('view_hotels'))
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Hotels WHERE HotelID = %s", (hotel_id,))
        hotel = cursor.fetchone()
        cursor.close()
        return render_template('edit_hotel.html', hotel=hotel)

# Route to delete hotel
@app.route('/admin/delete_hotel/<int:hotel_id>', methods=['POST'])
def delete_hotel(hotel_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Hotels WHERE HotelID=%s", (hotel_id,))
    mysql.connection.commit()
    cursor.close()
    
    flash('Hotel deleted successfully!', 'success')
    return redirect(url_for('view_hotels'))

from flask import request, redirect, url_for

# Route to edit booking
@app.route('/admin/edit_booking/<int:booking_id>', methods=['GET', 'POST'])
def edit_booking(booking_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Bookings WHERE BookingID = %s", (booking_id,))
    booking = cursor.fetchone()

    if request.method == 'POST':
        # Handle the form submission to update booking details
        checkin_date = request.form['checkin_date']
        checkout_date = request.form['checkout_date']
        
        cursor.execute("UPDATE Bookings SET CheckInDate = %s, CheckOutDate = %s WHERE BookingID = %s", (checkin_date, checkout_date, booking_id))
        mysql.connection.commit()
        cursor.close()

        flash('Booking updated successfully!', 'success')
        return redirect(url_for('view_bookings'))
    else:
        cursor.close()
        # Render the page with the form to edit booking details
        # Pass both booking and booking_id to the template
        return render_template('edit_booking.html', booking=booking, booking_id=booking_id)

# Route to delete booking
@app.route('/admin/delete_booking/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Bookings WHERE BookingID = %s", (booking_id,))
    mysql.connection.commit()
    cursor.close()

    flash('Booking deleted successfully!', 'success')
    return redirect(url_for('view_bookings'))

#privacy statement
@app.route('/PrivacyStatement')
def PrivacyStatement():
    return render_template("PrivacyStatement.html")

if __name__ == '__main__':
    app.run(debug=True)