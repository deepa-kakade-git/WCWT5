
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
