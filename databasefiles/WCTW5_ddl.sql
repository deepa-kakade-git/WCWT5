CREATE SCHEMA IF NOT EXISTS wcwt5db;

USE wcwt5db;

DROP TABLE IF EXISTS wcwt5_taxpayer_info;

CREATE TABLE wcwt5_taxpayer_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    TaxYear YEAR,
    FirstName VARCHAR(255),
    MiddleInitial CHAR(1),
    LastName VARCHAR(255),
    Address VARCHAR(255),
    City VARCHAR(255),
    State VARCHAR(255),
    Zipcode VARCHAR(10),
    TelNo VARCHAR(20),
    CurrEmployerNm VARCHAR(255),
    CurrEmployerAddress VARCHAR(255),
    CurrEmployerCity VARCHAR(255),
    CurrEmployerState VARCHAR(255),
    CurrEmployerZipcode VARCHAR(10),
    CurrEmployerTelNo VARCHAR(20),
    OtherEmployerNm VARCHAR(255),
    OtherEmployerAddress VARCHAR(255),
    OtherEmployerCity VARCHAR(255),
    OtherEmployerState VARCHAR(255),
    OtherEmployerZipcode VARCHAR(10),
    OtherEmployerTelNo VARCHAR(20),
);


DROP TABLE IF EXISTS wcwt5_timesheetentrycode_lov;

CREATE TABLE wcwt5_timesheetentrycode_lov (
    TimeEntryCode VARCHAR(10) PRIMARY KEY,
    TimeEntryDesc VARCHAR(50),
    TimeEntrytype VARCHAR(50)
);


DROP TABLE IF EXISTS wcwt5_timesheet;

/* 
Rows for holidays, weekends and taxpayer entered days for the tax year/WCTW5 refund form
Assumption : Full day entry only. Partial days not allowed
*/
CREATE TABLE wcwt5_timesheet (
    TimesheetId INT AUTO_INCREMENT PRIMARY KEY,
    TaxpayerInfo_id INT,
    FOREIGN KEY (TaxpayerInfo_id) REFERENCES wcwt5_taxpayer_info(id),
    TimeEntryDate DATE,
    TimeEntryCode VARCHAR(10),
    FOREIGN KEY (TimeEntryCode) REFERENCES wcwt5_timesheetentrycode_lov(TimeEntryCode),
    TimeEntryOtherDesc VARCHAR(50)
);


DROP TABLE IF EXISTS wcwt5_refund_computation;

CREATE TABLE wcwt5_refund_computation (
    TaxpayerInfo_id INT PRIMARY KEY,
    Line4GrossEarnings DECIMAL(10,2),
    Line6EarningstoAllocated DECIMAL(10,2),
    Line7AllocationPrcnt DECIMAL(5,2),
    Line8NontaxPortionEarnings DECIMAL(10,2),
    Line9TotNontaxEarnings DECIMAL(10,2),
    Line10EarningsSubToTax DECIMAL(10,2),
    Line11aTaxRate DECIMAL(7,4),
    Line11bTaxDue DECIMAL(10,2),
    Line11cTaxAcctNum VARCHAR(20),
    Line11cTaxWithheldAmt DECIMAL(10,2),
    Line12RefundDue DECIMAL(10,2),
    Line13NetRefundOrAmtDue DECIMAL(10,2),
    Line7aTotalDaysWorked INT,
    Line7bDaysWorkedOutside INT,
    Line7cDaysWorkedOutPrcnt DECIMAL(10,2),
    NotWorkedSatSun INT,
    NotWorkedHolidays INT,
    NotWorkedVac INT,
    NotWorkedIll INT,
    NotWorkedOther INT,
    NotWorkedTotal INT

    FOREIGN KEY (TaxpayerInfo_id) REFERENCES wcwt5_taxpayer_info(id)
);



/* Insert List of Valid Values for TimeEntryCode */
INSERT INTO wcwt5_timesheetentrycode_lov (TimeEntryCode, TimeEntryDesc, TimeEntryType) VALUES
('WND', 'Weekend', 'NONWORKING'),
('VAC', 'Vacation', 'NONWORKING'),
('ILL', 'Sick Day', 'NONWORKING'),
('OTH', 'Other Non Working', 'NONWORKING'),
('WFH', 'Work From Home', 'WORKING'),
('WFO', 'Work from outside of Wilmington', 'WORKING'),
('WFW', 'Work from within Wilmington', 'WORKING')
;

vac 11
ill 4 
oth 2
Hol 10
tot : 27

365-233 = 132 - 27 = 105


wfh 17 wfo 7 