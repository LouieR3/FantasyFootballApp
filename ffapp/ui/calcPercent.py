import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != _os.path.dirname(_d) and not _os.path.exists(_os.path.join(_d, 'paths.py')):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)


def percent(file):
    import os

    from ffapp.ui.data_loader import load_sheet

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
    df = load_sheet(file, "Louie Power Index")
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