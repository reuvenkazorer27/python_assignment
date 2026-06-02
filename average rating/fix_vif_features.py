# -*- coding: utf-8 -*-
"""
Fix notebook_part2.ipynb:
  1. Bug fix: y_train.values -> y_train  (PPS cell)
  2. VIF threshold: > 5 -> > 10  (user wants max VIF=10)
  3. Remove known_actor_ratio (correlated with actor_quality)
  4. Replace log_runtime with runtime_category_ordinal (0-3, lower VIF)
  5. Add new features:
       - decade_ordinal        (0=<1950 .. 10=2020s) — era effects
       - votes_per_film_age    log(votes+1) / max(film_age,1)  recency-adj popularity
       - is_classic            pre-1970 AND many votes
       - is_very_recent        2015+ film
"""
import json

NB = r'C:\Users\kazor\matala_python\average rating\notebook_part2.ipynb'

with open(NB, encoding='utf-8') as f:
    nb = json.load(f)
cells = nb['cells']

def get(c): return ''.join(c.get('source', []))
def put(c, s): c['source'] = [s]

def by_id(cid):
    for c in cells:
        if c.get('id') == cid:
            return c
    return None

# ─────────────────────────────────────────────────────────────────────────────
# 1. FIX BUG: y_train.values -> y_train  (PPS cell)
# ─────────────────────────────────────────────────────────────────────────────
pps = by_id('pps_code')
if pps:
    src = get(pps).replace("y_train.values", "y_train")
    put(pps, src)
    print('[OK] Fixed y_train.values -> y_train')

# ─────────────────────────────────────────────────────────────────────────────
# 2. VIF CELL: threshold >5 -> >10
# ─────────────────────────────────────────────────────────────────────────────
vif_cell = by_id('c4b8974c')
if vif_cell:
    src = (get(vif_cell)
           .replace('"HIGH >5" if v > 5 else "ok"', '"HIGH >10" if v > 10 else "ok"')
           .replace("'HIGH >5' if v > 5 else 'ok'", "'HIGH >10' if v > 10 else 'ok'"))
    put(vif_cell, src)
    print('[OK] VIF threshold updated to >10')

# ─────────────────────────────────────────────────────────────────────────────
# 3. VIF MARKDOWN: update threshold text
# ─────────────────────────────────────────────────────────────────────────────
vif_md = by_id('0107d51e')
if vif_md:
    src = (get(vif_md)
           .replace('VIF > 5', 'VIF > 10')
           .replace('VIF ≤ 5', 'VIF ≤ 10')
           .replace('**VIF ≤ 5**', '**VIF ≤ 10**')
           .replace('threshold: VIF > 5', 'threshold: VIF > 10')
           .replace('סף: VIF > 5', 'סף: VIF > 10'))
    put(vif_md, src)
    print('[OK] VIF markdown threshold updated')

# ─────────────────────────────────────────────────────────────────────────────
# 4. NUMERIC_COLS: remove known_actor_ratio + log_runtime,
#                  add runtime_category_ordinal + decade_ordinal + votes_per_film_age
# ─────────────────────────────────────────────────────────────────────────────
cols_cell = by_id('4f703749')
if cols_cell:
    src = get(cols_cell)

    # Remove known_actor_ratio from NUMERIC_COLS
    src = src.replace(
        "    'known_actor_ratio',\n",
        ""
    )
    # Remove log_runtime from NUMERIC_COLS (keep is_long_film in BINARY_COLS)
    src = src.replace(
        "    'log_runtime',             # log(1+דקות) — יחס לוגריתמי, עדיף לElastic Net\n",
        ""
    )
    src = src.replace(
        "    'log_runtime',              # log(1+דקות) — better linearity than raw minutes for Elastic Net\n",
        ""
    )
    # Add new numeric features before num_lead_actors
    src = src.replace(
        "    'num_lead_actors',         # כמות שחקנים ראשיים\n",
        "    'runtime_category',        # 0=קצר(60-90) 1=בינוני(90-120) 2=ארוך(120-180) 3=אפי(180+)\n"
        "    'decade_ordinal',          # עשור הפקה (0=<1950 .. 10=2020+) — אפקטים של תקופה\n"
        "    'votes_per_film_age',      # log_numVotes/max(film_age,1) — פופולריות מנורמלת לגיל\n"
        "    'num_lead_actors',         # כמות שחקנים ראשיים\n"
    )
    # Handle alternate formatting
    src = src.replace(
        "    'num_lead_actors',          # כמות שחקנים ראשיים (אנסמבל vs יחיד)\n",
        "    'runtime_category',        # 0=קצר(60-90) 1=בינוני(90-120) 2=ארוך(120-180) 3=אפי(180+)\n"
        "    'decade_ordinal',          # עשור הפקה (0=<1950 .. 10=2020+) — אפקטים של תקופה\n"
        "    'votes_per_film_age',      # log_numVotes/max(film_age,1) — פופולריות מנורמלת לגיל\n"
        "    'num_lead_actors',          # כמות שחקנים ראשיים (אנסמבל vs יחיד)\n"
    )
    # Add new binary features
    src = src.replace(
        "    'numVotes_high',           # >1,000 מדרגים — סרט עם ציון אמין",
        "    'numVotes_high',           # >1,000 מדרגים — סרט עם ציון אמין\n"
        "    'is_classic',              # לפני 1970 + >5,000 מדרגים — סרט קלאסי\n"
        "    'is_very_recent',          # 2015+ — קולנוע עכשווי"
    )
    src = src.replace(
        "    'numVotes_high',           # >1,000 מדרגים — סרט עם ציון אמין (r=+0.093)",
        "    'numVotes_high',           # >1,000 מדרגים — סרט עם ציון אמין (r=+0.093)\n"
        "    'is_classic',              # לפני 1970 + >5,000 מדרגים — סרט קלאסי\n"
        "    'is_very_recent',          # 2015+ — קולנוע עכשווי"
    )
    put(cols_cell, src)
    print('[OK] NUMERIC_COLS / BINARY_COLS updated')

# ─────────────────────────────────────────────────────────────────────────────
# 5. prepare_data: add new feature computations
# ─────────────────────────────────────────────────────────────────────────────
prep_cell = by_id('6e92ea23')
if prep_cell:
    src = get(prep_cell)

    # A. Remove known_actor_ratio from FEATURE_COLS
    src = src.replace(
        "    'known_actor_ratio',        # fraction of cast with quality data\n",
        ""
    )
    src = src.replace(
        "    'known_actor_ratio',      # fraction of lead actors with a quality score (proxy for established cast)\n",
        ""
    )

    # B. Remove log_runtime from FEATURE_COLS
    src = src.replace(
        "    'log_runtime',              # log(1+דקות) — better linearity than raw minutes for Elastic Net\n",
        ""
    )
    src = src.replace(
        "    'log_runtime',             # log(1+דקות) — יחס לוגריתמי — טוב לElastic Net\n",
        ""
    )

    # C. Add new features to FEATURE_COLS (before is_sequel)
    src = src.replace(
        "    'is_sequel',",
        "    'runtime_category',\n"
        "    'decade_ordinal',\n"
        "    'votes_per_film_age',\n"
        "    'is_classic',\n"
        "    'is_very_recent',\n"
        "    'is_sequel',"
    )

    # D. Replace runtime computation block with new ordinal + remove known_actor_ratio computation
    old_runtime_block = (
        "    # Runtime features\n"
        "    runtime_num = pd.to_numeric(d['runtimeMinutes'], errors='coerce').fillna(0)\n"
        "    d['log_runtime']  = np.log1p(runtime_num)      # log(1+דקות): יחס לוגריתמי — טוב לElastic Net\n"
        "    d['is_long_film'] = (runtime_num > 120).astype(int)  # >120 דקות — binary threshold"
    )
    new_runtime_block = (
        "    # Runtime features\n"
        "    runtime_num = pd.to_numeric(d['runtimeMinutes'], errors='coerce').fillna(0)\n"
        "    d['is_long_film'] = (runtime_num > 120).astype(int)  # >120 דקות — binary threshold\n"
        "    # runtime_category: ordinal 0-3 (lower VIF than log_runtime)\n"
        "    d['runtime_category'] = pd.cut(\n"
        "        runtime_num,\n"
        "        bins=[0, 90, 120, 180, 9999],\n"
        "        labels=[0, 1, 2, 3]\n"
        "    ).astype(float).fillna(1.0)"
    )
    if old_runtime_block in src:
        src = src.replace(old_runtime_block, new_runtime_block)
        print('[OK] Runtime block updated')
    else:
        # Try alternate spacing
        src = src.replace(
            "    runtime_num = pd.to_numeric(d['runtimeMinutes'], errors='coerce').fillna(0)\n"
            "    d['log_runtime']  = np.log1p(runtime_num)",
            "    runtime_num = pd.to_numeric(d['runtimeMinutes'], errors='coerce').fillna(0)\n"
            "    d['runtime_category'] = pd.cut(runtime_num, bins=[0,90,120,180,9999], labels=[0,1,2,3]).astype(float).fillna(1.0)"
        )
        print('[OK] Runtime block updated (alternate)')

    # E. Add new features computation after numVotes block
    old_votes_block = (
        "    d['log_numVotes']  = np.log1p(nv)         # log(1+votes) — scale logarithmי\n"
        "    d['numVotes_high'] = (nv > 1_000).astype(int)  # >1,000 מדרגים = ציון אמין"
    )
    new_votes_block = (
        "    d['log_numVotes']  = np.log1p(nv)         # log(1+votes) — scale לוגריתמי\n"
        "    d['numVotes_high'] = (nv > 1_000).astype(int)  # >1,000 מדרגים = ציון אמין\n"
        "\n"
        "    # ── New features (v7) ──────────────────────────────────────────────────\n"
        "    # decade_ordinal: עשור הפקה כמשתנה סדרתי (אפקטים של תקופה)\n"
        "    decade_map = {1920:0, 1930:1, 1940:2, 1950:3, 1960:4, 1970:5,\n"
        "                  1980:6, 1990:7, 2000:8, 2010:9, 2020:10}\n"
        "    decade_raw = (d['startYear'].fillna(2000).astype(int) // 10) * 10\n"
        "    decade_raw = decade_raw.clip(1920, 2020)\n"
        "    d['decade_ordinal'] = decade_raw.map(decade_map).fillna(8).astype(float)\n"
        "\n"
        "    # votes_per_film_age: פופולריות מנורמלת לגיל הסרט (סרטים חדשים עדיין מצברים קולות)\n"
        "    d['votes_per_film_age'] = d['log_numVotes'] / d['film_age'].clip(lower=1)\n"
        "\n"
        "    # is_classic: סרט קלאסי = לפני 1970 + יותר מ-5,000 מדרגים\n"
        "    d['is_classic']    = ((d['startYear'] < 1970) & (nv > 5_000)).astype(int)\n"
        "    # is_very_recent: קולנוע עכשווי (2015+)\n"
        "    d['is_very_recent'] = (d['startYear'] >= 2015).astype(int)"
    )
    if old_votes_block in src:
        src = src.replace(old_votes_block, new_votes_block)
        print('[OK] Votes block + new features added')

    # F. Remove known_actor_ratio computation
    old_ratio = (
        "    d['known_actor_ratio'] = d['lead_actors_ids'].apply(_known_actor_ratio)\n"
    )
    if old_ratio in src:
        src = src.replace(old_ratio, "")
        print('[OK] known_actor_ratio computation removed')

    put(prep_cell, src)
    print('[OK] prepare_data updated')

# ─────────────────────────────────────────────────────────────────────────────
# 6. SUMMARY: update threshold and add v7 row
# ─────────────────────────────────────────────────────────────────────────────
summary_cell = by_id('a3284ffc')
if summary_cell:
    src = get(summary_cell)
    src = (src
        .replace('VIF ≤ 5 לכל פיצ\'ר נומרי', 'VIF ≤ 10 לכל פיצ\'ר נומרי')
        .replace('| **v6** | Gradient Boosting (Model 3) + SHAP explainability | ראה §9 | ראה §9 |',
                 '| **v6** | Gradient Boosting (Model 3) + SHAP explainability | ראה §9 | ראה §9 |\n'
                 '| **v7** | VIF ≤ 10 + runtime_category + decade_ordinal + votes_per_film_age + is_classic | ראה §9 | ראה §9 |')
        .replace("'גרסה נוכחית (v6)'", "'גרסה נוכחית (v7)'")
        .replace('גרסה נוכחית (v6)', 'גרסה נוכחית (v7)')
        .replace('VIF ≤ 5 לכולם', 'VIF ≤ 10 לכולם')
    )
    put(summary_cell, src)
    print('[OK] Summary updated with v7')

# ─────────────────────────────────────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────────────────────────────────────
with open(NB, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
print('\nSaved.')

# Verify
with open(NB, encoding='utf-8') as f:
    nb2 = json.load(f)

prep_src = ''.join(by_id('6e92ea23').get('source', []) if False else
    next(c for c in nb2['cells'] if c.get('id')=='6e92ea23').get('source', []))
pps_src  = ''.join(next(c for c in nb2['cells'] if c.get('id')=='pps_code').get('source', []))

print('\nVerification:')
print(f'  y_train.values still present: {"y_train.values" in pps_src}  (must be False)')
print(f'  runtime_category computed:    {"runtime_category" in prep_src}')
print(f'  decade_ordinal computed:      {"decade_ordinal" in prep_src}')
print(f'  votes_per_film_age computed:  {"votes_per_film_age" in prep_src}')
print(f'  is_classic computed:          {"is_classic" in prep_src}')
print(f'  known_actor_ratio removed:    {"known_actor_ratio" not in prep_src}')
