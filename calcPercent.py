def percent(file):
    import pandas as pd
    from espn_api.football import League
    import os

    # Split the filename and extension
    name, extension = os.path.splitext(file)

    # Check if the last part of the name is a year (assumes it's a 4-digit year)
    parts = name.split()
    if parts and parts[-1].isdigit() and len(parts[-1]) == 4:
        result = " ".join(parts[:-1])
        year = int(parts[-1])

    print(result)
    # print(parts)
    # print(year)
    df = pd.read_excel(file, sheet_name="Louie Power Index")
    record_split = df['Record'].iloc[0].split('-')

    # Convert to ints
    record_nums = [int(num) for num in record_split] 

    # Sum 
    current_week = sum(record_nums)

    percentList = []
    
    percentList.append(current_week)

    top25 = round(current_week * 0.75)
    percentList.append(top25)

    bot25 = round(current_week * 0.25)
    percentList.append(bot25)
    
    top10 = round(current_week * 0.9)
    percentList.append(top10)
    
    bot10 = round(current_week * 0.1)
    percentList.append(bot10)

    return percentList
# file = "EBC League 2022.xlsx"
# percentLis = percent(file)
# print(percentLis)