from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.ext.automap import automap_base 

# Define the connection string
# Replace 'wcwt5', 'Tax1234!', 'localhost', '3306', and 'wct5db' with your actual MySQL credentials
connection_string = 'mysql+pymysql://wcwt5:Tax1234!@localhost:3306/wcwt5db'

# Create an engine
engine = create_engine(connection_string)

# Reflect the existing database tables
metadata = MetaData()
metadata.reflect(engine)

# Prepare the Base class for reflection
Base = automap_base(metadata=metadata)
Base.prepare()

# Access the reflected tables
Taxpayer_Info = Base.classes.wcwt5_taxpayer_info
TimesheetEntryCode_LOV = Base.classes.wcwt5_timesheetentrycode_lov
Timesheet = Base.classes.wcwt5_timesheet
Refund_Computation = Base.classes.wcwt5_refund_computation

print(type(Taxpayer_Info))
print()

# Create an inspector
inspector = inspect(engine)

# Print the description of each table along with its relationships
for table_name in metadata.tables.keys():
    table = metadata.tables[table_name]
    print(f"Table: {table_name}")
    
    # Print columns
    print("\tColumns:")
    for column in table.c:
        print(f"\t\tColumn: {column.name}, Type: {column.type}")
        
    # Print relationships
    relationships = inspector.get_foreign_keys(table_name)
    if relationships:
        print("\tRelationships:")
        for relationship in relationships:
            print(f"\t\tForeign Key: {relationship['constrained_columns']} -> {relationship['referred_table']}({relationship['referred_columns']})")
    else:
        print("\tNo relationships found.")
        
    print()



# Now you can interact with the reflected tables as needed
# For example, you can query data from the tables, insert new records, etc.

from sqlalchemy.orm import Session

# Create a session
session = Session(engine)

# Example: Query all records from the TimesheetEntryCode_LOV
TimesheetEntryCode_records = session.query(TimesheetEntryCode_LOV).all()

# Iterate over the records and access their attributes

for record in TimesheetEntryCode_records:
    print(record.TimeEntryCode)

print("Adding Taxpayer info")
newtaxpayerinfo=Taxpayer_Info(FirstName='Praveen K  Test Record 100')
session.add(newtaxpayerinfo)
print("Autogenerated ID:", newtaxpayerinfo.id)

session.commit()


# Querying for a single TimesheetEntryCode_LOV object where TimeEntryCode is 'ILL'
timelov = session.query(TimesheetEntryCode_LOV).filter_by(TimeEntryCode='ILL').first()

# Accessing attributes of the TimesheetEntryCode_LOV object
if timelov:
    print("Time Entry Code:", timelov.TimeEntryCode)  # Assuming TimeEntryCode is a valid attribute
    # Access other attributes as needed
else:
    print("No TimesheetEntryCode_LOV object found with TimeEntryCode 'ILL'")
for row in timelov:
    row_dict = row.__dict__
    column_values = {column: getattr(row, column) for column in row_dict.keys() if not column.startswith('_')}
    print(column_values)



print("Displaying all rows from Taxpayer info")

#Taxpayer_Info_records = session.query(Taxpayer_Info).all()
#for row in Taxpayer_Info_records:
#    row_dict = row.__dict__
#    column_values = {column: getattr(row, column) for column in row_dict.keys() if not column.startswith('_')}
#    print(column_values)

session.close()