import pandas as pd
from operator import itemgetter
import glob
from espn_api.football import League

files = glob.glob('*.xlsx')

# league = League(league_id=1339704102, year=2024, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')
league = League(league_id=310334683, year=2025, espn_s2='AEC3jc8inPISUEojfHvhzvOsdtsGWNv8sGIxjkBQjQyNQgX%2FDRaM5IKm%2BwyY2guiak1uwiE0xIkP4XEcoTzgLlumNMYgQbnqS3HjnAWI9%2BTZYo2N70ktU9isjCRXRlIvcOFKDV1OmY71%2FgJhMWKodsvEmli0dYCDTMXFF%2Bd7nuCxvGsFSBxV2BPdh8NdKpTEasZN4VhjgG6o9Iczv%2FySPOI9N2x1CGiVJNx8E8rblTk86tPPIr4QdKjYSS7a7Xs2h6KG9i9sLCV%2Be1DJvwtVhgOX',swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
team_owner = [team.owner for team in league.teams]
team_owners = [team.owners for team in league.teams]
# print(team_owners)
# sfd
team_names  = [team.team_name for team in league.teams]
team_dict   = dict(zip(team_names, team_owner))
# print(team_names)
# print(team_dict)

# Create a list of dictionaries for the DataFrame
data = []
for team in team_owners:
    team = team[0]
    data.append({
        "Display Name": team['firstName'] + " " + team['lastName'],
        "ID": team['id']
    })

# Create the DataFrame
df = pd.DataFrame(data)
# print(df)

# Reverse the team_dict to map IDs to team names
id_to_team_name = {id_: team_name for team_name, ids in team_dict.items() for id_ in ids}

# Map team names to the DataFrame based on ID
df['Team Name'] = df['ID'].map(id_to_team_name)

# Display the DataFrame
print(df)
dgf
appended_data = []
leagueList = []
for file in files:
    leagueName = file.split(".xlsx")[0]
    name, year = leagueName.rsplit(maxsplit=1)
    year = int(year)
    leagueList.append(leagueName)
    df = pd.read_excel(file, sheet_name="Louie Power Index")
    df["League"] = leagueName
    print(df)

    if name == "Pennoni Younglings":
        # Pennoni Younglings
        league = League(league_id=310334683, year=year, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
        team_owners = [team.owner for team in league.teams]
        team_names = [team.team_name for team in league.teams]
        team_dict = dict(zip(team_names, team_owners))

        # Apply dictionary mapping to Teams column
        print(df)
        df.insert(1, "Owner", df['Teams'].map(team_dict))
        # print(df)

    elif name == "Family League":
        # Family League
        league = League(league_id=1725372613, year=year, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
        team_owners = [team.owner for team in league.teams]
        team_names = [team.team_name for team in league.teams]
        team_dict = dict(zip(team_names, team_owners))

        # Apply dictionary mapping to Teams column
        df.insert(1, "Owner", df['Teams'].map(team_dict))
        # print(df)

    elif name == "EBC League":
        # EBC League
        league = League(league_id=1118513122, year=year, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
        team_owners = [team.owner for team in league.teams]
        team_names = [team.team_name for team in league.teams]
        team_dict = dict(zip(team_names, team_owners))

        # Apply dictionary mapping to Teams column
        df.insert(1, "Owner", df['Teams'].map(team_dict))
        # print(df)

    elif name == "0755 Fantasy Football":
        # Pennoni Transportation
        league = League(league_id=1339704102, year=year, espn_s2='AEBnVIPLGawrfX3pYmFejB2uTpTrDT5gKM7jbAqOtvaNBfAF0muAaPFFZBzwevb6Robdlp8Ruok9B8MFrXj6DEDW6m3zhlv0j9q%2BSVF446Q%2BU3ui%2F2mNHJK34K7mlc9dhW03a4HgrNWR4GDPukRdI5orkAF3Kl5KeDamvTff%2BaIlroUAgYyKLzQyEueU%2BLCCn4Jwb5ZLPBFSW00QQ3UbYc9tGwNeDZAKIiEEfd%2FQiKWXYfQnwep48PkunIN5%2FhYoa5MsjfG6jMhQAX22al5F%2F%2Fpuq6X7ei4emvlW3KAUbUMiY%2Bx4ViHMbWOcmrwkMPPFFqOsW8%2BkFK%2B1C40tt7Z3%2BaY1', swid='{634597F9-8435-46D1-9314-B554E8B4BB2A}')
        team_owners = [team.owner for team in league.teams]
        team_names = [team.team_name for team in league.teams]
        team_dict = dict(zip(team_names, team_owners))

        # Apply dictionary mapping to Teams column
        # df.insert(1, "Owner", df['Teams'].map(team_dict))
        # print(df)

    elif name == "Game of Yards!":
        # Prahlad Friends League
        league = League(league_id=1781851, year=year, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')
        team_owners = [team.owner for team in league.teams]
        team_names = [team.team_name for team in league.teams]
        team_dict = dict(zip(team_names, team_owners))

        # Apply dictionary mapping to Teams column
        df.insert(1, "Owner", df['Teams'].map(team_dict))
        # print(df)

    elif name == "Brown Munde":
        # Prahlad Other Friends League
        league = League(league_id=367134149, year=year, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')
        team_owners = [team.owner for team in league.teams]
        team_names = [team.team_name for team in league.teams]
        team_dict = dict(zip(team_names, team_owners))

        # Apply dictionary mapping to Teams column
        df.insert(1, "Owner", df['Teams'].map(team_dict))
        # print(df)

    appended_data.append(df)
print()
print()
print()
dfFINAL = pd.concat(appended_data)
dfFINAL = dfFINAL.iloc[: , 1:]
# dfFINAL.index += 1
df1 = dfFINAL.sort_values(by=['Louie Power Index (LPI)'], ascending=False).reset_index(drop=True)
print(df1)