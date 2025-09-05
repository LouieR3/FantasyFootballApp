def playoff_num(league_id, espn_s2, swid, year):
    import pandas as pd
    from espn_api.football import League
    import os
    league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
    settings = league.settings
    playoff_team_count = settings.playoff_team_count

    # # Split the filename and extension
    # name, extension = os.path.splitext(file)

    # playoff_team_count = settings.playoff_team_count
    # # Check if the last part of the name is a year (assumes it's a 4-digit year)
    # parts = name.split()
    # if parts and parts[-1].isdigit() and len(parts[-1]) == 4:
    #     result = " ".join(parts[:-1])
    #     year = int(parts[-1])

    # print(result)
    # # print(parts)
    # # print(year)

    # df = pd.read_excel(file, sheet_name="Louie Power Index")
    # num_rows = len(df)

    # if num_rows == 12 or num_rows == 11:
    #     playoff_number = 8
    # elif num_rows == 10 or num_rows == 8:
    #     playoff_number = 6
    return playoff_team_count

# file = "0755 Fantasy Football 2022.xlsx"
# percentLis = playoff_num(file)
# print(percentLis)