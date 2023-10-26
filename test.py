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
# Pennoni Younglings
# league = League(league_id=310334683, year=2023, espn_s2='AEAfTKrAtdKbMxfMyenv9DJYTiU3C8VnQUxCN2Th4N3NOlCz9K%2FI6Q7ivooWGDq9sntbsoARrL32sOaiwyJFrdsaLBZO1AZzNTIkB00%2BX4fqBIVFgMRZe96xpKk72nJ9kfqgSf7rcQDIsQ6SDXU4fT6O0v9er%2BRsJWvZyLF4qPJ5tfqwvPMFgRBjX4ve1uzcAwgaDkVWSQwE27XWMyHoAYOzMU89l7vcEjtIWsdsdJVmjSUEHBSuK1wuMXeOG0GG54S4ckEu2jJB4QRFN%2FqMyEDM', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Family League
# league = League(league_id=1725372613, year=2023, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# EBC League
league = League(league_id=1118513122, year=2023, espn_s2='AEBxvJwo9gYK1pk%2B3S36%2FFZS5WVqYHsY3l6QKMwy538U7Q%2BbCKt237iKEykfAurrxK0T%2B4M%2FhsXk6t2oLyY%2Fle6b5DUKWvsi1ZXzyMRzW7mBevrrtS1Uhyr7KNCPzM0ccOB1Daw4Xv%2FnY9b9KiMxPCRNcosaDEkZfjR%2ByCcF2KtYqhZ90gEfrdWGG4GlVjpMw7Ve4fL7V0mHDp3NgozRqkB7cZH2dZ0fOjF%2BPMwo9hQZ3V3R9jQdvAp2f3Dx2nbDiG%2Fi9oqM9cN1U87DEjHRu7CI', swid='{4656A2AD-A939-460B-96A2-ADA939760B8B}')

# Pennoni Transportation
# league = League(league_id=1339704102, year=2023, espn_s2='AEBnVIPLGawrfX3pYmFejB2uTpTrDT5gKM7jbAqOtvaNBfAF0muAaPFFZBzwevb6Robdlp8Ruok9B8MFrXj6DEDW6m3zhlv0j9q%2BSVF446Q%2BU3ui%2F2mNHJK34K7mlc9dhW03a4HgrNWR4GDPukRdI5orkAF3Kl5KeDamvTff%2BaIlroUAgYyKLzQyEueU%2BLCCn4Jwb5ZLPBFSW00QQ3UbYc9tGwNeDZAKIiEEfd%2FQiKWXYfQnwep48PkunIN5%2FhYoa5MsjfG6jMhQAX22al5F%2F%2Fpuq6X7ei4emvlW3KAUbUMiY%2Bx4ViHMbWOcmrwkMPPFFqOsW8%2BkFK%2B1C40tt7Z3%2BaY1', swid='{634597F9-8435-46D1-9314-B554E8B4BB2A}')

# Prahlad Friends League
# league = League(league_id=1781851, year=2023, espn_s2='AEBnVIPLGawrfX3pYmFejB2uTpTrDT5gKM7jbAqOtvaNBfAF0muAaPFFZBzwevb6Robdlp8Ruok9B8MFrXj6DEDW6m3zhlv0j9q%2BSVF446Q%2BU3ui%2F2mNHJK34K7mlc9dhW03a4HgrNWR4GDPukRdI5orkAF3Kl5KeDamvTff%2BaIlroUAgYyKLzQyEueU%2BLCCn4Jwb5ZLPBFSW00QQ3UbYc9tGwNeDZAKIiEEfd%2FQiKWXYfQnwep48PkunIN5%2FhYoa5MsjfG6jMhQAX22al5F%2F%2Fpuq6X7ei4emvlW3KAUbUMiY%2Bx4ViHMbWOcmrwkMPPFFqOsW8%2BkFK%2B1C40tt7Z3%2BaY1', swid='{634597F9-8435-46D1-9314-B554E8B4BB2A}')


# team_owners = [team.owner for team in league.teams]
# print(team_owners)
# team_names = [team.team_name for team in league.teams]
# print(team_names)
# print(settings = league.settings4)
# print(count)
# 
# league = "Pennoni Younglings 2023"
# league = "EBC League 2023"
league = "Family League 2023"
file = league + ".xlsx"
df = pd.read_excel(file, sheet_name="Louie Power Index")
print(df)
record_split = df['Record'].iloc[0].split('-')

# Convert to ints
record_nums = [int(num) for num in record_split] 

# Sum 
record_sum = sum(record_nums)

print(record_sum)
print("--- %s seconds ---" % (time.time() - start_time))