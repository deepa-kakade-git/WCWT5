from __future__ import print_function
from flask import Blueprint, render_template, request, redirect, url_for, flash
import json
from sqlalchemy import create_engine, MetaData, Table, inspect, func
from sqlalchemy.ext.automap import automap_base
import datetime
from sqlalchemy.orm import Session
import datetime
from sqlalchemy.exc import SQLAlchemyError
import sys

views = Blueprint("views", __name__)


def previous_years(num_years):
    current_year = datetime.datetime.now().year
    years = [current_year - i for i in range(1, num_years + 1)]
    return years


# MySQL Connect string
db_connection_string = "mysql+pymysql://wcwt5:Tax1234!@localhost:3306/wcwt5db"


# Create database engine
dbengine = create_engine(db_connection_string)

# Reflect the existing database tables
metadata = MetaData()
metadata.reflect(dbengine)

# Prepare the Base class for reflection
Base = automap_base(metadata=metadata)
Base.prepare()


# Access the reflected table classes
Taxpayer_Info = Base.classes.wcwt5_taxpayer_info
TimesheetEntryCode_LOV = Base.classes.wcwt5_timesheetentrycode_lov
Timesheet = Base.classes.wcwt5_timesheet
Refund_Computation = Base.classes.wcwt5_refund_computation

# golabl object instance to point to tax payer info for current session.
curr_Taxpayer_Info = Taxpayer_Info

# Create database session
dbsession = Session(dbengine)


#Class to calculate total nonworking days
class NonWorkingDays:
    def __init__(self, year):
        self.year = year
        self.saturdays_sundays = self.calculate_saturdays_sundays()
        self.holidays = 12
        self.vacation_days = 0
        self.illness_days = 0
        self.other_non_working_days = 0
        
    def calculate_saturdays_sundays(self):
        saturdays_sundays = []
        for month in range(1, 13):
            for day in range(1, 32):
                try:
                    date_obj = datetime.date(self.year, month, day)
                    if date_obj.weekday() in [5, 6]:
                        saturdays_sundays.append(date_obj)
                except ValueError:
                    pass  # Handling days that do not exist in the month
        return len(saturdays_sundays)

    def total_non_working_days(self):
        return self.saturdays_sundays + self.holidays + self.vacation_days + self.illness_days + self.other_non_working_days


@views.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
       if "newWcwt5" in request.form:
          previous_3_years = previous_years(3)
          return redirect(url_for("views.wcwt5_info", years=previous_3_years))
       elif "exsWcwt5" in request.form:
           return redirect(url_for("views.wcwt5_get_existing"))

    else:
        return render_template("home.html")


@views.route("/wcwt5_get_existing", methods=["GET", "POST"])
def wcwt5_get_existing():
    if request.method == "POST":
        taxpayer_info_id = request.form["TaxpayerinfoId"]
        return redirect(url_for('views.wcwt5_display', taxpayer_info_id=taxpayer_info_id ))  # Redirect to a relevant page after deletion
    else:
        return render_template("wcwt5_get_existing.html")



@views.route("/wcwt5_info", methods=["GET", "POST"])
def wcwt5_info():
    if request.method == "POST":
        TaxYear = request.form["TaxYear"]
        FirstName = request.form["FirstName"]
        MiddleInitial = request.form["MiddleInitial"]
        LastName = request.form["LastName"]
        Address = request.form["Address"]
        City = request.form["City"]
        State = request.form["State"]
        Zipcode = (
            int(request.form["Zipcode"]) if request.form["Zipcode"].strip() else None
        )
        TelNo = int(request.form["TelNo"]) if request.form["TelNo"].strip() else None
        CurrEmployerNm = request.form["CurrEmployerNm"]
        CurrEmployerAddress = request.form["CurrEmployerAddress"]
        CurrEmployerCity = request.form["CurrEmployerCity"]
        CurrEmployerState = request.form["CurrEmployerState"]
        CurrEmployerZipcode = (
            int(request.form["CurrEmployerZipcode"])
            if request.form["CurrEmployerZipcode"].strip()
            else None
        )
        CurrEmployerTelNo = (
            int(request.form["CurrEmployerTelNo"])
            if request.form["CurrEmployerTelNo"].strip()
            else None
        )
        OtherEmployerNm = request.form["OtherEmployerNm"]
        OtherEmployerAddress = request.form["OtherEmployerAddress"]
        OtherEmployerCity = request.form["OtherEmployerCity"]
        OtherEmployerState = request.form["OtherEmployerState"]
        OtherEmployerZipcode = (
            int(request.form["OtherEmployerZipcode"])
            if request.form["OtherEmployerZipcode"].strip()
            else None
        )
        OtherEmployerTelNo = (
            int(request.form["OtherEmployerTelNo"])
            if request.form["OtherEmployerTelNo"].strip()
            else None
        )
        new_Taxpayer_Info = Taxpayer_Info(
            TaxYear=TaxYear,
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
            OtherEmployerTelNo=OtherEmployerTelNo,
        )
        dbsession.add(new_Taxpayer_Info)
        dbsession.commit()
        autogen_taxpayer_info_id = new_Taxpayer_Info.id
        # return redirect(url_for('views.wcwt5_timesheet', taxpayer_info_id=new_Taxpayer_Info.id))
        return redirect(
            url_for(
                "views.wcwt5_add_timesheet", taxpayer_info_id=autogen_taxpayer_info_id
            )
        )
    else:
        previous_3_years = previous_years(3)
        return render_template("wcwt5_info.html", years=previous_3_years)


@views.route("/wcwt5_add_timesheet/<int:taxpayer_info_id>", methods=["GET", "POST"])
def wcwt5_add_timesheet(taxpayer_info_id):
    if request.method == "POST":
        time_entry_date = request.form["time_entry_date"]
        time_entry_code = request.form["time_entry_code"]
        time_entry_other_desc = request.form["time_entry_other_desc"]
        if time_entry_date:
           # Create a new timesheet entry
           new_timesheet = Timesheet(
                TaxpayerInfo_id=taxpayer_info_id,
                TimeEntryDate=time_entry_date,
                TimeEntryCode=time_entry_code,
                TimeEntryOtherDesc=time_entry_other_desc,
           )

           dbsession.add(new_timesheet)

           dbsession.commit()
        # Redirect to a success page or another route
        # return redirect(url_for('views.debug', timesheets=timesheets))
        if "addTime" in request.form:
            return redirect(
                url_for("views.wcwt5_add_timesheet", taxpayer_info_id=taxpayer_info_id)
            )
        elif "revTime" in request.form:
            # Render the HTML template for adding, displaying, and deleting timesheets
            return redirect(
                            url_for(
                                    "views.wcwt5_review_timesheet", taxpayer_info_id=taxpayer_info_id
                                   )                    
            )

    else:
        # Fetch the TaxYear associated with the taxpayer_info_id
        taxpayer_info = (
            dbsession.query(Taxpayer_Info).filter_by(id=taxpayer_info_id).first()
        )
        tax_year = taxpayer_info.TaxYear

        # Fetch existing timesheets for the taxpayer from the database
        existing_timesheets = (
            dbsession.query(Timesheet).filter_by(TaxpayerInfo_id=taxpayer_info_id).all()
        )

        # Render the HTML template for adding, displaying, and deleting timesheets
        return render_template(
            "wcwt5_add_timesheet.html",
            taxpayer_info_id=taxpayer_info_id,
            existing_timesheets=existing_timesheets,
            tax_year=tax_year
        )

@views.route("/wcwt5_review_timesheet/<int:taxpayer_info_id>", methods=["GET", "POST"])
def wcwt5_review_timesheet(taxpayer_info_id):
    if request.method == "POST":
       if "addTime" in request.form:
            return redirect(
                url_for("views.wcwt5_add_timesheet", taxpayer_info_id=taxpayer_info_id)
            )
       elif "delTime" in request.form:
            timesheet_id_to_delete = request.form['del_timesheet_id']
            timesheet = dbsession.query(Timesheet).filter_by(TimesheetId=timesheet_id_to_delete).first()
            if timesheet:
               # Delete the timesheet record from the database
               dbsession.delete(timesheet)
               dbsession.commit()
            return redirect(url_for('views.wcwt5_review_timesheet', taxpayer_info_id=taxpayer_info_id ))  # Redirect to a relevant page after deletion
       elif 'conRefund' in request.form:
            # Continue to Next Step button clicked
            # Redirect to the route for the next step
            timesheets = (
                         dbsession.query(Timesheet).filter_by(TaxpayerInfo_id=taxpayer_info_id).all()
                    )
            return redirect(url_for('views.wcwt5_refund_compute', taxpayer_info_id=taxpayer_info_id ))  # Redirect to a relevant page after deletion
            
    else:
        existing_timesheets = (
            dbsession.query(Timesheet).filter_by(TaxpayerInfo_id=taxpayer_info_id).all()
        )
        return render_template("wcwt5_review_timesheet.html",             
               taxpayer_info_id=taxpayer_info_id,
               timesheets=existing_timesheets)


@views.route("/wcwt5_refund_compute/<int:taxpayer_info_id>", methods=["GET", "POST"])
def wcwt5_refund_compute(taxpayer_info_id):
	gbyquery = dbsession.query(
	Timesheet.TimeEntryCode,
	TimesheetEntryCode_LOV.TimeEntrytype,
	func.count().label('entry_count')
	).join(
	TimesheetEntryCode_LOV,
	Timesheet.TimeEntryCode == TimesheetEntryCode_LOV.TimeEntryCode
	).filter(
	Timesheet.TaxpayerInfo_id == taxpayer_info_id  # Assuming you want to filter by TaxpayerInfo_id
	).group_by(
	TimesheetEntryCode_LOV.TimeEntrytype,
	Timesheet.TimeEntryCode
	).all()

	# Query the taxpayer info record to obtain Tax Year
	taxpayer_info = (
 		dbsession.query(Taxpayer_Info).filter_by(id=taxpayer_info_id).first())
	tax_year = taxpayer_info.TaxYear

	non_working_days_curr = NonWorkingDays(tax_year)
	working_days_out_wil=0
	for aggrRecords in gbyquery:
		if aggrRecords.TimeEntryCode == 'VAC':
			# Update vacation days count
			non_working_days_curr.vacation_days = aggrRecords.entry_count
		elif aggrRecords.TimeEntryCode == 'ILL':
			# Update illness days count
			non_working_days_curr.illness_days = aggrRecords.entry_count
		elif aggrRecords.TimeEntryCode == 'OTH':
			# Update other non-working days count
			non_working_days_curr.other_non_working_days = aggrRecords.entry_count
		elif aggrRecords.TimeEntryCode == 'WFH':
			working_days_out_wil += aggrRecords.entry_count
		elif aggrRecords.TimeEntryCode == 'WFO':
			working_days_out_wil += aggrRecords.entry_count
		non_working_days_curr.holidays=10

	Line7aTotalDaysWorked=(365 -
				(non_working_days_curr.other_non_working_days + 
				non_working_days_curr.saturdays_sundays +
				non_working_days_curr.illness_days +
				non_working_days_curr.vacation_days +
				non_working_days_curr.holidays))

	Line7cDaysWorkedOutPrcnt = working_days_out_wil / Line7aTotalDaysWorked


	if request.method == "POST":
		#Get the data entered from form
		Line4Gross_Earnings = request.form["Line4GrossEarnings"]
		Line11cTaxWithheldAmt = request.form["Line11cTaxWithheldAmt"]

		#Calculate other values
		Line4GrossEarnings=float(Line4Gross_Earnings)
		Line6EarningstoAllocated=Line4Gross_Earnings
		Line7AllocationPrcnt=Line7cDaysWorkedOutPrcnt
		Line8NontaxPortionEarnings = float(Line6EarningstoAllocated) * float(Line7AllocationPrcnt)
		Line9TotNontaxEarnings=float(Line8NontaxPortionEarnings)
		Line10EarningsSubToTax=Line4GrossEarnings-Line9TotNontaxEarnings
		Line11aTaxRate=0.0125
		Line11bTaxDue=Line10EarningsSubToTax*Line11aTaxRate
		Line12RefundDue=float(Line11cTaxWithheldAmt)-Line11bTaxDue
		Line13NetRefundOrAmtDue=Line12RefundDue
		NotWorked_Total= non_working_days_curr.total_non_working_days()


		new_Refund_Computation = Refund_Computation(
						TaxpayerInfo_id=taxpayer_info_id,
						Line4GrossEarnings=Line4GrossEarnings,
						Line6EarningstoAllocated=Line6EarningstoAllocated,
						Line7AllocationPrcnt=Line7AllocationPrcnt,
						Line8NontaxPortionEarnings=Line8NontaxPortionEarnings,
						Line9TotNontaxEarnings=Line9TotNontaxEarnings,
						Line10EarningsSubToTax=Line10EarningsSubToTax,
						Line11aTaxRate=Line11aTaxRate,
						Line11bTaxDue=Line11bTaxDue,
						Line11cTaxAcctNum=None,
						Line11cTaxWithheldAmt=Line11cTaxWithheldAmt,
						Line12RefundDue=Line12RefundDue,
						Line13NetRefundOrAmtDue=Line13NetRefundOrAmtDue,
						Line7aTotalDaysWorked=Line7aTotalDaysWorked,
						Line7bDaysWorkedOutside=working_days_out_wil,
						Line7cDaysWorkedOutPrcnt=Line7cDaysWorkedOutPrcnt,
						NotWorkedSatSun=non_working_days_curr.saturdays_sundays,
						NotWorkedHolidays=non_working_days_curr.holidays,
						NotWorkedVac=non_working_days_curr.vacation_days,
						NotWorkedIll=non_working_days_curr.illness_days,
						NotWorkedOther=non_working_days_curr.other_non_working_days, 
						NotWorkedTotal=NotWorked_Total

                                             )
		try:
			dbsession.add(new_Refund_Computation)
			dbsession.commit()
		except IntegrityError:
			# Handle integrity constraint violations, such as duplicate keys or foreign key violations
			dbsession.rollback()
		# Optionally, log the error or display a user-friendly message
		except SQLAlchemyError as e:
			# Handle other SQLAlchemy-related errors
			dbsession.rollback()
			# Optionally, log the error or display a user-friendly message
		except Exception as e:
			# Handle unexpected errors
			dbsession.rollback()
			# Log the error for further investigation
			print(f"An unexpected error occurred: {e}")
		return redirect(url_for('views.wcwt5_display', taxpayer_info_id=taxpayer_info_id ))  # Redirect to a relevant page after deletion
	else:
		return render_template("wcwt5_refund_compute.html", timesheets=gbyquery, non_work_totals=non_working_days_curr, working_days_out_wil=working_days_out_wil )


@views.route("/wcwt5_display/<int:taxpayer_info_id>")
def wcwt5_display(taxpayer_info_id):
	wcwt5_taxpayer_info = (
 		dbsession.query(Taxpayer_Info).filter_by(id=taxpayer_info_id).first()
	)

	wcwt5_timesheets = (dbsession.query(
				Timesheet.TimeEntryDate,
				Timesheet.TimeEntryCode,
				TimesheetEntryCode_LOV.TimeEntrytype,
				TimesheetEntryCode_LOV.TimeEntryDesc,
				Timesheet.TimeEntryOtherDesc
	).join(
	TimesheetEntryCode_LOV,
	Timesheet.TimeEntryCode == TimesheetEntryCode_LOV.TimeEntryCode
	).filter(
	Timesheet.TaxpayerInfo_id == taxpayer_info_id  # Assuming you want to filter by TaxpayerInfo_id
	).order_by(
	Timesheet.TimeEntryDate
	).all()
	)
	

	wcwt5_refund_computation = (
            dbsession.query(Refund_Computation).filter_by(TaxpayerInfo_id=taxpayer_info_id).first()
        )

	return render_template("wcwt5_refund_display.html", wcwt5_taxpayer_info=wcwt5_taxpayer_info, timesheets=wcwt5_timesheets,  wcwt5_refund_computation=wcwt5_refund_computation)

@views.route("/debug")
def debug():
    timesheets = request.args.getlist("timesheets")
    return render_template("debug.html", timesheets=timesheets)


##########  Not USED ###########################
@views.route("/wcwt5_timesheet/<int:taxpayer_info_id>", methods=["GET", "POST"])
def wcwt5_timesheet(taxpayer_info_id):
    if request.method == "POST":
        # Process form submission and add/delete multiple rows to/from the wcwt5_timesheet table
        timesheets = request.form.getlist("timesheets")
        for timesheet_data in timesheets:
            # Create a new timesheet entry
            # Extract data for each timesheet entry from the form
            # time_entry_date = timesheet_data.get('TimeEntryDate')
            # time_entry_code = timesheet_data.get('TimeEntryCode')
            # time_entry_other_desc = timesheet_data.get('TimeEntryOtherDesc')
            new_timesheet = Timesheet(
                TaxpayerInfo_id=12,
                TimeEntryDate="2012-01-01",
                TimeEntryCode="WFO",
                TimeEntryOtherDesc="Gone Fishing",
            )
            dbsession.add(new_timesheet)

        dbsession.commit()
        # Redirect to a success page or another route
        # return redirect(url_for('views.success'))
        return redirect(url_for("views.wcwt5_timesheet", taxpayer_info_id=11))

    else:
        # Fetch the TaxYear associated with the taxpayer_info_id
        taxpayer_info = (
            dbsession.query(Taxpayer_Info).filter_by(id=taxpayer_info_id).first()
        )
        tax_year = taxpayer_info.TaxYear

        # Fetch existing timesheets for the taxpayer from the database
        existing_timesheets = (
            dbsession.query(Timesheet).filter_by(TaxpayerInfo_id=taxpayer_info_id).all()
        )

        # Render the HTML template for adding, displaying, and deleting timesheets
        return render_template(
            "wcwt5_timesheet.html",
            taxpayer_info_id=taxpayer_info_id,
            existing_timesheets=existing_timesheets,
            tax_year=tax_year,
        )
