"""Canonical owner identity for teams ESPN reports with several co-owners.

ESPN returns a list of owners per team, and the code base historically took
``team.owners[0]``. When a team is co-owned that pick is arbitrary, so a
season's stats can land on someone who was not really running the team - and
because owner identity drives Lifetime Record and all-time head-to-head, one
misattributed year splits a franchise's history across two people.

Add an entry to PREFERRED_CO_OWNER to say who should get credit for a
co-owned team-year. Everything user-facing resolves owners through
``resolve_owner()`` / ``owner_id_for()``, so one entry fixes every view.

Example: Pennoni Younglings 2024's "Philadelphia Bills Mafia" was listed as
Henry Morris + Robbie Wilston. Robbie was the real owner (he ran it alone in
2025), so 2024 belongs to him: Henry's franchise history is 2022-2023 and
Robbie's is 2024-2025, and everyone else's all-time head-to-head splits the
same way.
"""

# (league name without year, season) -> display name to credit when that
# league-year has a co-owned team. Applies only to teams whose owner list
# actually contains this person; every other team is unaffected.
PREFERRED_CO_OWNER = {
    ("Pennoni Younglings", 2024): "Robbie Wilston",
}

# (league name, season, team name) -> owner ID, for CSV/Excel data already
# written to disk with the wrong co-owner's ID baked in. Keyed on team name
# because that is what the persisted files carry.
TEAM_OWNER_ID_OVERRIDES = {
    ("Pennoni Younglings", 2024, "Philadelphia Bills Mafia"):
        "{A279F58E-795F-4115-B9F5-8E795F7115FC}",   # Robbie Wilston
}


def _display_name(owner):
    if not isinstance(owner, dict):
        return str(owner)
    first = owner.get("firstName", "") or ""
    last = owner.get("lastName", "") or ""
    return f"{first} {last}".strip()


def league_key(league):
    """(league name without the ' 22/23' suffix, year) for a League object."""
    name = league.settings.name.replace(" 22/23", "").strip()
    year = getattr(league, "year", None)
    return name, (int(year) if year is not None else None)


def resolve_owner(league, team):
    """The owner dict that should get credit for this team-season.

    Falls back to ESPN's first-listed owner when there is no override or the
    team has a single owner.
    """
    owners = getattr(team, "owners", None) or []
    if not owners:
        return {}
    preferred = PREFERRED_CO_OWNER.get(league_key(league))
    if preferred and len(owners) > 1:
        for owner in owners:
            if _display_name(owner) == preferred:
                return owner
    return owners[0]


def owner_id_for(league, team):
    """Owner ID that should get credit for this team-season."""
    return resolve_owner(league, team).get("id")


def owner_display_name(league, team):
    """Display name that should get credit for this team-season."""
    return _display_name(resolve_owner(league, team))


def apply_owner_id_overrides(df, league_name, year,
                             team_col="Team", id_col="Owner ID"):
    """Correct baked-in owner IDs in a persisted DataFrame (in place-safe)."""
    if id_col not in df.columns or team_col not in df.columns:
        return df
    df = df.copy()
    for (lg, yr, team), owner_id in TEAM_OWNER_ID_OVERRIDES.items():
        if lg == league_name and int(yr) == int(year):
            mask = df[team_col].astype(str).str.strip() == team
            df.loc[mask, id_col] = owner_id
    return df
