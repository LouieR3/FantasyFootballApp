def fantasypros_ranks():
    import requests
    from bs4 import BeautifulSoup
    import json
    import pandas as pd
    import re
    # URL_list = [
    #     "https://www.fantasypros.com/nfl/rankings/ros-half-point-ppr-qb.php", 
    #     "https://www.fantasypros.com/nfl/rankings/ros-half-point-ppr-wr.php",
    #     "https://www.fantasypros.com/nfl/rankings/ros-half-point-ppr-rb.php",
    #     "https://www.fantasypros.com/nfl/rankings/ros-half-point-ppr-te.php",
    # ]
    URL = "https://www.fantasypros.com/nfl/rankings/ros-ppr-qb.php"
    URL = "https://www.fantasypros.com/nfl/rankings/ros-ppr-overall.php"
    # for URL in URL_list:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # -----------------------------
    # Fetch page
    # -----------------------------
    html = requests.get(URL, headers=headers).text
    soup = BeautifulSoup(html, "html.parser")

    # -----------------------------
    # Find the script tag containing ecrData
    # -----------------------------
    script_tag = None
    for s in soup.find_all("script"):
        if s.string and "var ecrData" in s.string:
            script_tag = s.string
            break

    if script_tag is None:
        raise Exception("Could not find ecrData in page.")

    # -----------------------------
    # Extract JSON from "var ecrData = { ... };"
    # -----------------------------
    match = re.search(r"var ecrData\s*=\s*(\{.*?\});", script_tag, re.DOTALL)
    json_text = match.group(1)

    # Convert JS → Python dict
    ecrData = json.loads(json_text)

    # Extract players list
    players = ecrData["players"]

    # -----------------------------
    # Convert to DataFrame
    # -----------------------------
    df = pd.DataFrame(players)
    df = df[['player_name', 'player_team_id', 'player_position_id', 'player_owned_avg', 'rank_ecr', 'rank_min', 'rank_max', 'rank_ave', 'rank_std', 'pos_rank']]

    print(df)
    return df

# df = fantasypros_ranks()
# df = df[df['player_name'].str.contains("Mahomes", case=False, na=False)]
# print(df)