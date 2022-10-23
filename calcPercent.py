def percent(file):
    import pandas as pd

    df = pd.read_excel(file, sheet_name="Schedule Grid")
    df.index += 1

    names = []
    for col in df.columns:
        if col != "Teams":
            names.append(col)
        
    percentList = []
    count = int(df[names[0]][1].split(" ")[0]) + int(df[names[0]][1].split(" ")[2]) + int(df[names[0]][1].split(" ")[4])
    percentList.append(count)

    top25 = round(count * 0.75)
    percentList.append(top25)

    bot25 = round(count * 0.25)
    percentList.append(bot25)
    
    top10 = round(count * 0.9)
    percentList.append(top10)
    
    bot10 = round(count * 0.1)
    percentList.append(bot10)

    return percentList