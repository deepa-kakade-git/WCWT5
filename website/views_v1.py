from flask import Blueprint, render_template, request, redirect, url_for, flash
import json
from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.ext.automap import automap_base 
import datetime
from sqlalchemy.orm import Session
import datetime


views = Blueprint('views', __name__)

def previous_years(num_years):
    current_year = datetime.datetime.now().year
    years = [current_year - i for i in range(1, num_years + 1)]
    return years

#MySQL Connect string
db_connection_string = 'mysql+pymysql://wcwt5:Tax1234!@localhost:3306/wcwt5db'

   
# Create database engine
dbengine = create_engine(db_connection_string)
 
# Reflect the existing database tables
metadata = MetaData()
metadata.reflect(dbengine)

# Prepare the Base class for reflection
Base = automap_base(metadata=metadata)
Base.prepare()

# Access the reflected tables
Taxpayer_Info = Base.classes.wcwt5_taxpayer_info
TimesheetEntryCode_LOV = Base.classes.wcwt5_timesheetentrycode_lov
Timesheet = Base.classes.wcwt5_timesheet
Refund_Computation = Base.classes.wcwt5_refund_computation

#golabl object instance to point to tax payer info for current session.
curr_Taxpayer_Info=Taxpayer_Info;

# Create database session
dbsession = Session(dbengine)

    

@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST': 
       previous_3_years = previous_years(3)
       return redirect(url_for('views.wcwt5_info', years=previous_3_years))
    else:
       return render_template("home.html")

@views.route('/wcwt5_info', methods=['GET','POST'])
def wcwt5_info():
    if request.method == 'POST':
       TaxYear=request.form['TaxYear']
       FirstName=request.form['FirstName']
       MiddleInitial=request.form['MiddleInitial']
       LastName=request.form['LastName']
       Address=request.form['Address']
       City=request.form['City']
       State=request.form['State']
       Zipcode=int(request.form['Zipcode']) if request.form['Zipcode'].strip() else None
       TelNo=int(request.form['TelNo']) if request.form['TelNo'].strip() else None
       CurrEmployerNm=request.form['CurrEmployerNm']
       CurrEmployerAddress=request.form['CurrEmployerAddress']
       CurrEmployerCity=request.form['CurrEmployerCity']
       CurrEmployerState=request.form['CurrEmployerState']
       CurrEmployerZipcode=int(request.form['CurrEmployerZipcode']) if request.form['CurrEmployerZipcode'].strip() else None
       CurrEmployerTelNo=int(request.form['CurrEmployerTelNo']) if request.form['CurrEmployerTelNo'].strip() else None
       OtherEmployerNm=request.form['OtherEmployerNm']
       OtherEmployerAddress=request.form['OtherEmployerAddress']
       OtherEmployerCity=request.form['OtherEmployerCity']
       OtherEmployerState=request.form['OtherEmployerState']
       OtherEmployerZipcode=int(request.form['OtherEmployerZipcode']) if request.form['OtherEmployerZipcode'].strip() else None
       OtherEmployerTelNo=int(request.form['OtherEmployerTelNo']) if request.form['OtherEmployerTelNo'].strip() else None
       new_Taxpayer_Info =Taxpayer_Info(TaxYear=TaxYear,
					FirstName=FirstName,
					MiddleInitial=MiddleInitial,
					LastName=LastName,
					Address=Address,
					City=City,
					State=State,
					Zipcode=Zipcode,
					TelNo=TelNo,
					CurrEmployerNm=CurrEmployerNm,
					CurrEmployerAddress=CurrEmployerAddress,
					CurrEmployerCity=CurrEmployerCity,
					CurrEmployerState=CurrEmployerState,
					CurrEmployerZipcode=CurrEmployerZipcode,
					CurrEmployerTelNo=CurrEmployerTelNo,
					OtherEmployerNm=OtherEmployerNm,
					OtherEmployerAddress=OtherEmployerAddress,
					OtherEmployerCity=OtherEmployerCity,
					OtherEmployerState=OtherEmployerState,
					OtherEmployerZipcode=OtherEmployerZipcode,
					OtherEmployerTelNo=OtherEmployerTelNo)
       dbsession.add(new_Taxpayer_Info)
       dbsession.commit()
       return redirect(url_for('views.wcwt5_timesheet', taxpayer_info_id=new_Taxpayer_Info.id))
    else:
       previous_3_years = previous_years(3)
       return render_template('wcwt5_info.html', years=previous_3_years)

@views.route('/wcwt5_timesheet/<int:taxpayer_info_id>', methods=['GET', 'POST'])
def wcwt5_timesheet(taxpayer_info_id):
    if request.method == 'POST':
        # Process form submission and add/delete multiple rows to/from the wcwt5_timesheet table
        timesheets = request.form.getlist('timesheets')
        for timesheet_data in timesheets:
            # Extract data for each timesheet entry from the form
            time_entry_date = timesheet_data.get('TimeEntryDate')
            time_entry_code = timesheet_data.get('TimeEntryCode')
            time_entry_other_desc = timesheet_data.get('TimeEntryOtherDesc')
            is_deleted = timesheet_data.get('isDeleted', False)

            if is_deleted:
                # If the timesheet entry is marked for deletion, delete it from the database
                db.session.query(Timesheet).filter_by(TaxpayerInfo_id=taxpayer_id, TimeEntryDate=time_entry_date, TimeEntryCode=time_entry_code).delete()
            else:
                # Otherwise, add/update the timesheet entry in the database
                timesheet = db.session.query(Timesheet).filter_by(TaxpayerInfo_id=taxpayer_id, TimeEntryDate=time_entry_date, TimeEntryCode=time_entry_code).first()
                if timesheet:
                    # Update existing timesheet entry
                    timesheet.TimeEntryOtherDesc = time_entry_other_desc
                else:
                    # Create a new timesheet entry
                    new_timesheet = Timesheet(
                        TaxpayerInfo_id=taxpayer_id,
                        TimeEntryDate=time_entry_date,
                        TimeEntryCode=time_entry_code,
                        TimeEntryOtherDesc=time_entry_other_desc
                    )
                    db.session.add(new_timesheet)

        # Commit changes to the database session
        db.session.commit()

        # Redirect to a success page or another route
        return redirect(url_for('views.success'))
    else:
        # Fetch existing timesheets for the taxpayer from the database
        existing_timesheets = Timesheet.query.filter_by(TaxpayerInfo_id=taxpayer_info_id).all()

        # Render the HTML template for adding, displaying, and deleting timesheets
        return render_template('add_timesheets.html', taxpayer_id=taxpayer_info_id, existing_timesheets=existing_timesheets)
