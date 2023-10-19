import pandas as pd

def digestFileContents():
    #Define Vars
    PRF_List = list()
    position = int()
    UserError = False

    # Read the Excel file
    df = pd.read_excel(r'C:\Users\joshk\PurdueApp\uploads\Parts Requisition Form.xlsx', engine='openpyxl')
    
    # Find the row where the string is present using a different method
    target_row = next((i for i, row in df.iterrows() if "Do not alter form, especially formulas" in row.astype(str).values), None)
    if target_row is None:
        print("Target string not found.")
        return

    #Sort into 2d array with some sorting
    for i in range(2, target_row):
        line = df.iloc[i]
        fields = line.astype(str).explode()  # Convert line to string before splitting
        for GetVals in fields.iloc[1:]: 
            if (i == 2 and (GetVals != 'Item')):
                PRF_List.append([GetVals,[]])
            elif (GetVals != 'nan' and (GetVals != '0')) :
                PRF_List[position][1].append(GetVals)
                position += 1
        position = 0

    #check that all categories contrain the same number of values, otherwise throw an error
    inner_list_lengths = [len(item[1]) for item in PRF_List]
    if all(length == inner_list_lengths[0] for length in inner_list_lengths) == False:
        UserError = True

    print(UserError)
    print(PRF_List)
    # Print the rows up to the target_row
    #print(df.iloc[3:target_row])

digestFileContents()
