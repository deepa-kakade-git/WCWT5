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
#Reflection is the process of reading the database schema and
# populating SQLAlchemy's metadata with information about tables, columns, and relationships.
metadata = MetaData()
metadata.reflect(dbengine)

# Prepare the Base class for reflection
# automap_base function provided by SQLAlchemy that creates a new base
# class f definitions based on an existing database schema.
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

@views.route('/wcwt5_timesheet', methods=['GET', 'POST'])
def wcwt5_timesheet():
    if request.method == 'POST':
        pass
    else:
        # Render the HTML template for adding, displaying, and deleting timesheets
        taxpayer_id = request.args.get('taxpayer_info_id')
        return render_template('wcwt5_timesheet.html', taxpayer_info_id=taxpayer_id)
