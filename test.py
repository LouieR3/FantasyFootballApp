import pandas as pd
from operator import itemgetter
import glob
from espn_api.football import League
pd.options.mode.chained_assignment = None
import time

start_time = time.time()

# files = glob.glob('*.xlsx')
# appended_data = []
# for file in files:
#     print(file.split(".xlsx")[0])
#     df = pd.read_excel(file, sheet_name="Louie Power Index")
#     appended_data.append(df)
# dfFINAL = pd.concat(appended_data)
# dfFINAL = dfFINAL.iloc[: , 1:]
# dfFINAL.index += 1
# df1 = dfFINAL.sort_values(by=['Louie Power Index (LPI)'], ascending=False)

# league = "EBC League 2021"
# # league = "FamilyLeague"
# # league = "PennoniYounglings"
# file = league + ".xlsx"
# print(league)
# df1 = pd.read_excel(file, sheet_name="Schedule Grid")
# df = pd.read_excel(file, sheet_name="Louie Power Index")
# df = df.iloc[: , 1:]
# names = []
# for col in df1.columns:
#     if col != "Teams":
#         names.append(col)
# count = 0
# print(names)
# for team in names:
#     print(df.loc[df["Teams"] == team]["Louie Power Index (LPI)"])
#     count += 1
# print()
espn_s2 = "AECL47AORj8oAbgOmiQidZQsoAJ6I8ziOrC8Jw0W2M0QwSjYsyUkzobZA0CZfGBYrKf0a%2B%2B3%2Fflv6rFCZvb3%2FWo%2FfKVU4JXm9UyLsY9uIRAF4o9TuISaQjoc13SbsqMiLyaf5kR4ZwDcNr8uUxDwamEyuec5yqs07zsvy0VrOQo6NTxylWXkwABFfNVAdyqDI%2BQoQtoetdSah0eYfMdmSIBkGnxN0R0z5080zBAuY9yCm%2Fav49lUfGA7cqGyWoIky8pE3vB%2Fng%2F49JvTerFjJfzC"

# Pennoni Younglings
# league = League(league_id=310334683, year=2024, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')
# league = League(league_id=1339704102, year=2024, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')

# Family League
# league = League(league_id=1725372613, year=2023, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# EBC League
# league = League(league_id=1118513122, year=2023, espn_s2=espn_s2, swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Pennoni Transportation
# league = League(league_id=1339704102, year=2023, espn_s2='AEBnVIPLGawrfX3pYmFejB2uTpTrDT5gKM7jbAqOtvaNBfAF0muAaPFFZBzwevb6Robdlp8Ruok9B8MFrXj6DEDW6m3zhlv0j9q%2BSVF446Q%2BU3ui%2F2mNHJK34K7mlc9dhW03a4HgrNWR4GDPukRdI5orkAF3Kl5KeDamvTff%2BaIlroUAgYyKLzQyEueU%2BLCCn4Jwb5ZLPBFSW00QQ3UbYc9tGwNeDZAKIiEEfd%2FQiKWXYfQnwep48PkunIN5%2FhYoa5MsjfG6jMhQAX22al5F%2F%2Fpuq6X7ei4emvlW3KAUbUMiY%2Bx4ViHMbWOcmrwkMPPFFqOsW8%2BkFK%2B1C40tt7Z3%2BaY1', swid='{634597F9-8435-46D1-9314-B554E8B4BB2A}')
league = League(league_id=1339704102, year=2024, espn_s2='AEBezn%2BxS%2FYzfjDpGuZFs8LIvQEEkQ7oJZq2SXNw7DKPOeEwK8M%2FEI%2FxFTzG9i0x2PPra1W68s5V7GlzSBDGOlSLbCheVUXE43tCsUVzBG2XhMpFfbB0teCm9PVCBccCyIGZTZiFdQ4HtHqYWhGT%2BesSi7sF7iUaiOsWswptqdbqRYtE8%2FbKzEyD8w%2BT0o9YNEHI%2Fr0NyqDpuQthgYUIdosUif0InIWpTjvZqLfOmluUi9kzQe6NI1d%2B%2BPRevCwev82kulAGetgkKRVQCKqFSYs4', swid='{4C1C5213-4BB5-4243-87AC-0BCB2D637264}')

# Prahlad Friends League
# league = League(league_id=1781851, year=2023, espn_s2='AEBnVIPLGawrfX3pYmFejB2uTpTrDT5gKM7jbAqOtvaNBfAF0muAaPFFZBzwevb6Robdlp8Ruok9B8MFrXj6DEDW6m3zhlv0j9q%2BSVF446Q%2BU3ui%2F2mNHJK34K7mlc9dhW03a4HgrNWR4GDPukRdI5orkAF3Kl5KeDamvTff%2BaIlroUAgYyKLzQyEueU%2BLCCn4Jwb5ZLPBFSW00QQ3UbYc9tGwNeDZAKIiEEfd%2FQiKWXYfQnwep48PkunIN5%2FhYoa5MsjfG6jMhQAX22al5F%2F%2Fpuq6X7ei4emvlW3KAUbUMiY%2Bx4ViHMbWOcmrwkMPPFFqOsW8%2BkFK%2B1C40tt7Z3%2BaY1', swid='{634597F9-8435-46D1-9314-B554E8B4BB2A}')
# print(league.power_rankings(week=5))
settings = league.settings
# print(league.standings_weekly(week=5))
# print(league.standings)
# print(league._get_positional_ratings(week=5))

team_owners = [team.owners for team in league.teams]
flat_owners = [owner[0] for owner in team_owners]

# Creating the DataFrame
df = pd.DataFrame(flat_owners, columns=['displayName', 'firstName', 'lastName', 'id'])
# Map team names to their corresponding owners based on the `id` matching `team_owner`

team_owner = [team.owner[0] for team in league.teams]
# print(team_owner)
team_name = [team.team_name for team in league.teams]
print(team_name)
df['team_name'] = df['id'].map(dict(zip(team_owner, team_name)))

# Display the updated DataFrame
print(df)

# team_names = [team.team_name for team in league.teams]
# print(team_names)
# print(settings = league.settings4)
# print(count)
# 
# league = "Pennoni Younglings 2023"
# league = "EBC League 2023"


print("--- %s seconds ---" % (time.time() - start_time))