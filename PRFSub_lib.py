import pandas as pd
from datetime import datetime

def digestFileContents(FileLocation):
    #Define Vars
    PRF_List = list()
    position = int()
    UserError = False

    # Read the Excel file
    df = pd.read_excel(FileLocation, engine='openpyxl')
    
    # Find the row where the string is present
    target_row = next((i for i, row in df.iterrows() if "Do not alter form, especially formulas" in row.astype(str).values), None)
    if target_row is None:
        print("Target string not found.")
        UserError = True

    #Sort into 2d array with some sorting
    for i in range(2, target_row+1):
        line = df.iloc[i]
        fields = line.astype(str).explode()  # Convert line to string before splitting
        if(i == target_row):
            PRF_List.append([['File Details'],[(fields.iloc[0].lstrip('Updated:  ')),fields.iloc[5]]])
        else:
            for GetVals in fields.iloc[1:]: 
                if (i == 2 and (GetVals != 'Item')):
                    PRF_List.append([GetVals,[]])
                elif (GetVals != 'nan' and (GetVals != '0')) :
                    PRF_List[position][1].append(GetVals)
                    position += 1
            position = 0
    # Exclude items where the first element of the item is 'File Details'
    filtered_inner_list_lengths = [len(item[1]) for item in PRF_List if item[0] != ['File Details']]

    # Check if all lengths are the same, set UserError to True if not
    if len(filtered_inner_list_lengths) > 0 and not all(length == filtered_inner_list_lengths[0] for length in filtered_inner_list_lengths):
        UserError = True
    else:
        UserError = False
    return([UserError,PRF_List])

def extract_file_details(PRF_List):
    file_details = next((item for item in PRF_List if item[0] == ['File Details']), None)
    if file_details:
        return file_details[1]
    return None

def restructure_data(PRF_List, file_details):
    item_data = [item for item in PRF_List if isinstance(item[0], str)]
    zipped_data = list(zip(*[items[1] for items in item_data]))

    # Append file details to each record, if available
    if file_details:
        last_modified, total_price = file_details
        return [item + (last_modified, total_price) for item in zipped_data]
    else:
        return zipped_data

def store_parsed_data(PRF_List, team_number, team_procurement_detail,restructured_data,db):
    file_details = [item for item in PRF_List if item[0] == ['File Details']]
    if file_details:
        file_last_modified, total_file_price = file_details[0][1]
        try:
            file_last_modified = datetime.strptime(file_last_modified, '%m/%d/%Y')  # Adjust the format as needed
        except ValueError:
            file_last_modified = datetime.utcnow()  # Default value or handle error as needed
    else:
        file_last_modified = datetime.utcnow()  # Default or error
        total_file_price = 0.0  # Default or error
        print(restructured_data)
    for item in restructured_data:
        description, part_number, quantity, unit_price, ext_price, url_link, delivery_date, file_last_modified, total_file_price = item

        try:
            delivery_date = datetime.strptime(delivery_date, '%m/%d/%Y')  # Adjust format as needed
        except ValueError:
            delivery_date = None  # Default or handle error

        # Create a new record
        new_record = team_procurement_detail(
            team_number=team_number,
            item_description=description,
            part_number=part_number,
            quantity=int(quantity),
            unit_price=float(unit_price),
            ext_price=float(ext_price),
            url_link=url_link,
            delivery_date=delivery_date,
            file_last_modified=file_last_modified,
            total_file_price=float(total_file_price)
        )

        # Now print the new_record
        print("Adding record:", new_record)

        # Add to the session
        db.session.add(new_record)

    try:
        db.session.commit()
        print("Commit successful")
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        # Handle or log the error as needed