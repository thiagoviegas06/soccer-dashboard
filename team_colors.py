# Primary team colors for Premier League clubs
# Based on official team branding and historical colors

primary_color_map = {
    "Arsenal": "#EF0107",           # Bright red
    "Aston Villa": "#540D1C",       # Claret
    "Birmingham": "#0052CC",        # Royal blue
    "Blackburn": "#0C3C26",         # Navy blue
    "Blackpool": "#FF8C00",         # Tangerine orange
    "Bolton": "#36166B",            # Navy blue
    "Bournemouth": "#C41E3A",       # Crimson red
    "Bradford": "#BA0021",          # Claret red
    "Brentford": "#E30413",         # Red
    "Brighton": "#0057B8",          # Albion blue
    "Burnley": "#6B0C23",           # Claret
    "Cardiff": "#0066FF",           # Cardiff blue
    "Charlton": "#C1121F",          # Red
    "Chelsea": "#003DA5",           # Royal blue
    "Coventry": "#82B1DE",          # Sky blue
    "Crystal Palace": "#1B50BE",    # Royal blue
    "Derby": "#0B0B0B",             # Black
    "Everton": "#003399",           # Royal blue
    "Fulham": "#000000",            # Black
    "Huddersfield": "#0C1A53",      # Navy blue
    "Hull": "#262C2C",              # Amber/Gold
    "Ipswich": "#0066CC",           # Suffolk blue
    "Leeds": "#1E50DC",             # Elland Road blue
    "Leicester": "#003DA5",         # Royal blue
    "Liverpool": "#C8102E",         # Liverpool red
    "Luton": "#FF6A00",             # Orange
    "Man City": "#6CABDD",          # Sky blue
    "Man United": "#DA291C",        # Manchester red
    "Middlesbrough": "#E31E24",     # Red
    "Newcastle": "#241F20",         # Black
    "Norwich": "#00B2A9",           # Canary yellow
    "Nott'm Forest": "#E31C23",     # Red
    "Portsmouth": "#1D3B7D",        # Navy blue
    "QPR": "#003DA5",               # Royal blue
    "Reading": "#003DA5",           # Royal blue
    "Sheffield United": "#C41E3A",  # Red
    "Southampton": "#C8102E",       # Red
    "Stoke": "#C41E3A",             # Red
    "Sunderland": "#C8102E",        # Red
    "Swansea": "#FFFFFF",           # White (with black trim)
    "Tottenham": "#132257",         # Navy blue
    "Watford": "#FBEE23",           # Yellow
    "West Brom": "#122C6F",         # Navy blue
    "West Ham": "#7A263A",          # Claret
    "Wigan": "#003DA5",             # Royal blue
    "Wolves": "#FFD700",            # Gold
}

# Fallback color pool — distributed across hue spectrum with moderate brightness
# Colors have reduced lightness (~50-60%) for better visibility and less eye strain
# Hues are spaced ~45° apart for clear separation across the color wheel
fallback_colors = [
    "#CC0000",  # Red (0°)
    "#CC6600",  # Orange (30°)
    "#CCCC00",  # Yellow (60°)
    "#00CC00",  # Green (120°)
    "#00CCCC",  # Cyan (180°)
    "#0000CC",  # Blue (240°)
    "#6600CC",  # Violet (270°)
    "#CC00CC",  # Magenta (300°)
    "#DD3300",  # Orange-Red (15°)
    "#99CC00",  # Yellow-Green (90°)
    "#1B8A7A",  # Sea Green (150°)
    "#1A5ECC",  # Dodger Blue (210°)
    "#6B1BA6",  # Blue Violet (255°)
    "#CC0066",  # Deep Pink (330°)
    "#2BA61B",  # Lime Green (120°)
    "#B30000",  # Crimson (0°)
]


def _hex_to_hsl(hex_color):
    """Convert hex color to HSL (Hue, Saturation, Lightness)."""
    r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    r, g, b = r / 255.0, g / 255.0, b / 255.0

    max_c = max(r, g, b)
    min_c = min(r, g, b)
    l = (max_c + min_c) / 2.0

    if max_c == min_c:
        h = s = 0.0
    else:
        d = max_c - min_c
        s = d / (2.0 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)

        if max_c == r:
            h = (60 * ((g - b) / d + (6 if g < b else 0))) % 360
        elif max_c == g:
            h = (60 * ((b - r) / d + 2)) % 360
        else:
            h = (60 * ((r - g) / d + 4)) % 360

    return h, s, l


def _color_distance(c1, c2):
    """
    Calculate perceptual color distance using HSL space.
    Hue is weighted 2x more heavily (humans most sensitive to hue).
    """
    h1, s1, l1 = _hex_to_hsl(c1)
    h2, s2, l2 = _hex_to_hsl(c2)

    # Hue is circular (wraps at 360°)
    hue_diff = min(abs(h1 - h2), 360 - abs(h1 - h2))

    # Weighted distance: hue is 2x more important
    distance = ((hue_diff ** 2) * 2 + (s1 - s2) ** 2 + (l1 - l2) ** 2) ** 0.5
    return distance


def detect_plot_color_conflicts(selected_teams, min_distance=60):
    """
    Detect color conflicts within a specific set of teams for a plot.

    Args:
        selected_teams: List of team names to check
        min_distance: Minimum acceptable perceptual distance (HSL space)

    Returns:
        - conflicted_teams: Set of teams whose primary colors conflict
        - conflict_pairs: List of (team1, team2, distance) tuples showing conflicts
    """
    conflicted_teams = set()
    conflict_pairs = []

    # Get primary colors for selected teams
    team_colors = {team: primary_color_map.get(team) for team in selected_teams
                   if team in primary_color_map}

    # Find exact color duplicates
    color_to_teams = {}
    for team, color in team_colors.items():
        if color is not None:
            if color not in color_to_teams:
                color_to_teams[color] = []
            color_to_teams[color].append(team)

    # Mark teams with duplicate colors as conflicted
    for color, teams in color_to_teams.items():
        if len(teams) > 1:
            for team in teams:
                conflicted_teams.add(team)

    # Find perceptually similar colors within this plot
    team_list = list(team_colors.items())
    for i, (team1, color1) in enumerate(team_list):
        if color1 is None:
            continue
        for team2, color2 in team_list[i+1:]:
            if color2 is None:
                continue
            distance = _color_distance(color1, color2)
            if distance < min_distance:
                conflict_pairs.append((team1, team2, distance))
                conflicted_teams.add(team1)
                conflicted_teams.add(team2)

    return conflicted_teams, conflict_pairs


def assign_plot_colors(selected_teams, cached_colors=None, min_distance=60, random_seed=42):
    import random
    random.seed(random_seed)

    if cached_colors is None:
        cached_colors = {}

    # Step 1: Start with cached colors (from other plots)
    color_map = {team: color for team, color in cached_colors.items()
                 if team in selected_teams}
    used_colors = set(color_map.values())

    # Step 2: Try primary colors for teams not in cache
    new_teams = [t for t in selected_teams if t not in color_map]
    for team in new_teams:
        if team in primary_color_map:
            color_map[team] = primary_color_map[team]
            used_colors.add(primary_color_map[team])

    # Step 3: Detect conflicts within THIS plot
    conflicted_teams, conflict_pairs = detect_plot_color_conflicts(selected_teams, min_distance)

    # Step 4: If conflicts exist, reassign only conflicting teams (not cached teams)
    if conflicted_teams:
        # Keep cached colors (they're committed across plots)
        # Only reassign non-cached conflicted teams
        non_cached_conflicted = [t for t in conflicted_teams if t not in cached_colors]

        # Remove conflicting non-cached colors from map
        for team in non_cached_conflicted:
            if team in color_map:
                used_colors.discard(color_map[team])
                del color_map[team]

        # Step 5: Assign fallback colors to non-cached conflicting teams
        remaining_fallbacks = [c for c in fallback_colors if c not in used_colors]

        for team in sorted(non_cached_conflicted):
            if remaining_fallbacks:
                # Find valid candidates that meet min_distance from ALL used colors
                valid_candidates = [
                    c for c in remaining_fallbacks
                    if all(_color_distance(c, u) >= min_distance for u in used_colors)
                ]

                if valid_candidates:
                    chosen = random.choice(valid_candidates)
                else:
                    # No valid candidates: pick one with best distance
                    chosen = max(remaining_fallbacks,
                               key=lambda c: min(_color_distance(c, u) for u in used_colors))

                remaining_fallbacks.remove(chosen)
                color_map[team] = chosen
                used_colors.add(chosen)
            else:
                color_map[team] = "#888888"

    # Step 6: Add any remaining unassigned teams with fallback colors
    remaining_fallbacks = [c for c in fallback_colors if c not in used_colors]
    for team in selected_teams:
        if team not in color_map:
            if remaining_fallbacks:
                chosen = random.choice(remaining_fallbacks)
                remaining_fallbacks.remove(chosen)
                color_map[team] = chosen
                used_colors.add(chosen)
            else:
                color_map[team] = "#888888"

    # Step 7: Update cache with new assignments for next plot
    updated_cache = {**cached_colors, **color_map}

    return color_map, updated_cache
