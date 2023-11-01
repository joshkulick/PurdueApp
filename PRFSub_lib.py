import pandas as pd

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

    print(UserError)
    print(PRF_List)
