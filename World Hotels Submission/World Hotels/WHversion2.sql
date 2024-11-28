-- Define the database
CREATE DATABASE world_hotels;
USE world_hotels;

-- Define the tables
CREATE TABLE Customers (
    CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    Email VARCHAR(255) UNIQUE,
    Password VARCHAR(255)
);

CREATE TABLE Hotels (
    HotelID INT AUTO_INCREMENT PRIMARY KEY,
    Location VARCHAR(255),
    OnPeakPrice DECIMAL(10, 2),
    OffPeakPrice DECIMAL(10, 2)
);

CREATE TABLE Rooms (
    RoomID INT AUTO_INCREMENT PRIMARY KEY,
    HotelID INT,
    FeatureDescription VARCHAR(255),
    FOREIGN KEY (HotelID) REFERENCES Hotels(HotelID)
);

CREATE TABLE Bookings (
    BookingID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT,
    CheckInDate DATE,
    CheckOutDate DATE,
    HotelID INT,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (HotelID) REFERENCES Hotels(HotelID)  -- Foreign key constraint added here
);

CREATE TABLE Cancellations (
    CancellationID INT AUTO_INCREMENT PRIMARY KEY,
    BookingID INT,
    CancellationDate DATE,
    CancellationCharge DECIMAL(10, 2),
    FOREIGN KEY (BookingID) REFERENCES Bookings(BookingID)
);

CREATE TABLE Admins (
    AdminID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(255) UNIQUE,
    Password VARCHAR(255)
);
