"""
assets_data_prep.py
====================

prepare_data() ועוזריו - הועתקו מתוך notebook_part2.ipynb (חלק 2) ללא שינוי
בלוגיקה הפנימית של חישוב הפיצ'רים.

ה-dictionaries הגלובליים (ACTOR_QUALITY_MAP, ACTOR_HISTORY, GENRE_MOMENTUM_MAP,
DIRECTOR_MAP, LEAD_STAR_MAP, NCONST_BIRTH_YEAR, GLOBAL_MEAN_RATING) חושבו בחלק 2
מתוך דאטאסט הסרטים השלם, ונשמרו ב-feature_maps.pkl. הפונקציה load_feature_maps()
טוענת אותם ל-globals האלה לפני קריאה ל-prepare_data (בדיוק כמו ש-Part 2 מאכלס
אותם לפני שמריצים prepare_data על df_train/df_test).

לסרט חדש (שלא נמצא בדאטאסט) לא קיים tconst ב-LOO_SCORES / *_LOO_SCORES /
TCONST_TO_*, כך ש-prepare_data עובר אוטומטית למסלולי ה"Test" (full map /
fallback ל-GLOBAL_MEAN_RATING) - בדיוק כמו שהיה קורה לסרט מ-df_test.
"""

import re
import ast
import numpy as np
import pandas as pd
import joblib


# ── Globals (כמו בחלק 2, סעיף 5 - prepare_data + Feature Engineering) ──────
ACTOR_QUALITY_MAP:    dict  = {}
ACTOR_HISTORY:        dict  = {}  # actor -> [(year, rating)] - for temporal spread
GENRE_LOO_SCORES:     dict  = {}  # tconst -> LOO genre momentum (train films)
GENRE_MOMENTUM_MAP:   dict  = {}  # (genre, year) -> full-train avg (test films)
DIRECTOR_LOO_SCORES:  dict  = {}  # tconst -> LOO director quality
DIRECTOR_MAP:         dict  = {}  # nconst -> full-train director quality
LEAD_STAR_LOO_SCORES: dict  = {}  # tconst -> LOO lead star quality
LEAD_STAR_MAP:        dict  = {}  # nconst -> full-train lead star quality
LOO_SCORES:           dict  = {}
GLOBAL_MEAN_RATING:   float = 6.07

# tconst/nconst lookups built in Part 2 from IMDb crew data (title.principals /
# name.basics). סרט חדש לעולם לא יימצא במפות אלו -> prepare_data ייפול אוטומטית
# ל-DIRECTOR_MAP / LEAD_STAR_MAP / NCONST_BIRTH_YEAR (כלומר ל-GLOBAL_MEAN_RATING / 0.0
# כשאלו ריקים).
TCONST_TO_DIRECTOR:  dict = {}
TCONST_TO_LEAD_STAR: dict = {}
NCONST_BIRTH_YEAR:   dict = {}

_PRESTIGE_SET = {'Documentary', 'Biography', 'History', 'War', 'Music'}
_NEGATIVE_SET = {'Horror', 'Thriller', 'Action', 'Comedy', 'Sci-Fi'}
ALL_GENRES    = ['Documentary', 'Horror', 'Thriller', 'Biography', 'Drama', 'Action']
EAST_ASIA     = {'Japan', 'South Korea', 'Hong Kong', 'China', 'Taiwan'}

_SEQUEL_PATTERN = (
    r'(?:^|\s)(?:2|3|4|5|6|7|8|9|10'
    r'|ii|iii|iv|vi|vii|viii|ix'
    r'|part\s*[2-9]|chapter\s*[2-9]|volume\s*[2-9]'
    r'|returns?|reloaded|revolutions?|resurrection'
    r'|strikes\s+back|rises?|forever|continues?'
    r'|next\s+chapter|second\s+part)(?:\s|$)'
)


# ── עמודות (כמו בחלק 2, אחרי VIF - כל 19 העמודות עברו את הבדיקה) ──────────
NUMERIC_COLS = [
    'actor_quality',        # LOO Bayesian - r=+0.37
    'prestige_count',       # Documentary+Biography+History+War+Music
    'negative_count',       # Horror+Thriller+Action+Comedy+Sci-Fi
    'log_runtime',          # log(1+דקות)
    'actor_quality_spread', # max-mean: כוח הכוכב הבולט
    'genre_momentum',       # 3yr rolling avg of same genre - r=+0.402
    'director_quality',     # LOO director temporal - r~0.35
    'lead_star_quality',    # LOO top-billed actor (ordering=1) - r~0.30
    'actor_prime',          # proximity to peak career age (birthYear, no leakage)
]
BINARY_COLS = [
    'genre_Documentary', 'genre_Horror', 'genre_Thriller',
    'genre_Biography',   'genre_Drama',  'genre_Action',
    'is_long_film', 'is_sequel', 'has_actors',
]
CAT_COLS = ['country_group']  # US / East_Asia / Other -> OHE


# ── helpers (כמו בחלק 2) ────────────────────────────────────────────────────
def _clean_genres(g):
    if pd.isna(g): return []
    g = re.sub(r"[\[\]'\"]", '', str(g))
    return [x.strip() for x in g.split(',') if x.strip() and x.strip() != 'None']

def _country_group(x):
    if pd.isna(x) or not str(x).strip(): return 'Other'
    s = str(x)
    if 'United States' in s or 'USA' in s: return 'US'
    if any(c in s for c in EAST_ASIA): return 'East_Asia'
    return 'Other'

def _parse_actor_list(s):
    """פענוח בטוח של רשימת שחקנים."""
    if pd.isna(s): return []
    try: return ast.literal_eval(s)
    except: return []


# ── prepare_data - הועתק מחלק 2 (notebook_part2.ipynb, cell 'prepare_data') ──
def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Input:  raw DataFrame (מבנה dataset.csv).
    Output: DataFrame עם 19 עמודות מוכן ל-Pipeline (model.pkl / trained_model.pkl).
    """
    d = df.copy()
    d['Country']  = d['Country'].replace('Not Found', np.nan)
    d['Language'] = d['Language'].replace('Not Found', np.nan)

    # Genres
    gl = d['genres'].apply(_clean_genres)
    d['prestige_count'] = gl.apply(lambda gs: sum(1 for g in gs if g in _PRESTIGE_SET))
    d['negative_count'] = gl.apply(lambda gs: sum(1 for g in gs if g in _NEGATIVE_SET))
    for g in ALL_GENRES:
        d[f'genre_{g}'] = gl.apply(lambda gs, _g=g: int(_g in gs))

    # is_sequel - vectorized עם str.contains במקום apply שורה-שורה
    d['is_sequel'] = (
        d['primaryTitle'].fillna('')
          .str.contains(_SEQUEL_PATTERN, flags=re.IGNORECASE, regex=True)
          .astype(int)
    )

    # Runtime
    rt = pd.to_numeric(d['runtimeMinutes'], errors='coerce').fillna(0)
    d['log_runtime']  = np.log1p(rt)
    d['is_long_film'] = (rt > 120).astype(int)

    # ── actor_quality - vectorized ──────────────────────────
    aq = d['tconst'].map(LOO_SCORES)
    missing = aq.isna()

    if missing.any():
        def _aq_fallback(s):
            actors = _parse_actor_list(s)
            if not actors: return GLOBAL_MEAN_RATING
            scores = [ACTOR_QUALITY_MAP.get(a, GLOBAL_MEAN_RATING) for a in actors]
            return float(np.mean(scores))
        aq[missing] = d.loc[missing, 'lead_actors_ids'].apply(_aq_fallback)
    d['actor_quality'] = aq.fillna(GLOBAL_MEAN_RATING)

    # ── actor_quality_spread - temporal (same LOO as actor_quality) ──────
    parsed = d['lead_actors_ids'].apply(_parse_actor_list)
    film_years = d['startYear'].apply(
        lambda x: int(pd.to_numeric(x, errors='coerce') or 0))
    def _spread_temporal(row):
        actors, yr = row['actors'], row['year']
        if len(actors) < 2: return 0.0
        scores = []
        for a in actors:
            past = [(y2, r) for y2, r in ACTOR_HISTORY.get(a, []) if y2 < yr]
            if not past:
                scores.append(GLOBAL_MEAN_RATING)
            else:
                n, s = len(past), sum(r for _, r in past)
                scores.append((s + 5.0 * GLOBAL_MEAN_RATING) / (n + 5.0))
        return float(max(scores) - np.mean(scores))
    spread_df = pd.DataFrame({'actors': parsed, 'year': film_years})
    d['actor_quality_spread'] = spread_df.apply(_spread_temporal, axis=1)

    # ── has_actors - vectorized ──────────────────────────────
    def _has(actors):
        return int(any(a in ACTOR_QUALITY_MAP for a in actors))
    d['has_actors'] = parsed.apply(_has)

    # Country
    d['country_group'] = d['Country'].apply(_country_group)

    # ── director_quality - LOO for train, map for test ────────────
    d['director_quality'] = [
        DIRECTOR_LOO_SCORES.get(tc,
            DIRECTOR_MAP.get(TCONST_TO_DIRECTOR.get(tc), GLOBAL_MEAN_RATING))
        for tc in d['tconst']
    ]

    # ── lead_star_quality - LOO for train, map for test ──────────
    d['lead_star_quality'] = [
        LEAD_STAR_LOO_SCORES.get(tc,
            LEAD_STAR_MAP.get(TCONST_TO_LEAD_STAR.get(tc), GLOBAL_MEAN_RATING))
        for tc in d['tconst']
    ]

    # ── actor_prime - how close lead actors are to peak age ───────
    PRIME_AGE = 42.0
    def _prime_score(actors_str, film_year):
        if pd.isna(actors_str): return 0.0
        try: actors = ast.literal_eval(actors_str)
        except: return 0.0
        ages = [film_year - NCONST_BIRTH_YEAR[a]
                for a in actors if a in NCONST_BIRTH_YEAR]
        if not ages: return 0.0
        return float(np.mean([-abs(age - PRIME_AGE) for age in ages]))
    d['actor_prime'] = [
        _prime_score(actors, int(pd.to_numeric(yr, errors='coerce') or 0))
        for actors, yr in zip(d['lead_actors_ids'], d['startYear'])
    ]

    # ── genre_momentum - LOO for train, map for test ─────────────
    _pg = gl.apply(lambda gs: gs[0] if gs else 'Unknown')
    _yr = d['startYear'].apply(lambda x: int(pd.to_numeric(x, errors='coerce') or 0))
    _tc = d['tconst']
    d['genre_momentum'] = [
        GENRE_LOO_SCORES.get(tc,
            GENRE_MOMENTUM_MAP.get((g, yr), GLOBAL_MEAN_RATING))
        for tc, g, yr in zip(_tc, _pg, _yr)
    ]

    return d[NUMERIC_COLS + BINARY_COLS + CAT_COLS].copy()


# ── load_feature_maps - מאכלס את ה-globals למעלה מתוך feature_maps.pkl ──────
def load_feature_maps(path: str = 'feature_maps.pkl') -> None:
    """
    טוען את ה-dictionaries שחושבו בחלק 2 (על כל הדאטאסט) ל-globals של
    prepare_data, בדיוק כמו ש-Part 2 מריץ compute_*_map() לפני prepare_data.
    """
    global ACTOR_QUALITY_MAP, ACTOR_HISTORY, GENRE_MOMENTUM_MAP
    global DIRECTOR_MAP, LEAD_STAR_MAP, NCONST_BIRTH_YEAR, GLOBAL_MEAN_RATING

    maps = joblib.load(path)
    ACTOR_QUALITY_MAP   = maps.get('ACTOR_QUALITY_MAP', {})
    ACTOR_HISTORY       = maps.get('ACTOR_HISTORY', {})
    GENRE_MOMENTUM_MAP  = maps.get('GENRE_MOMENTUM_MAP', {})
    DIRECTOR_MAP        = maps.get('DIRECTOR_MAP', {})
    LEAD_STAR_MAP       = maps.get('LEAD_STAR_MAP', {})
    NCONST_BIRTH_YEAR   = maps.get('NCONST_BIRTH_YEAR', {})
    GLOBAL_MEAN_RATING  = maps.get('GLOBAL_MEAN_RATING', GLOBAL_MEAN_RATING)
