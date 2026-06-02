# 📋 היסטוריית Commits — `master` & `reuven`

> **פרויקט**: מטלת סיכום חלק 2 — חיזוי דירוג סרטים ב-IMDb  
> **סטודנטים**: ראובן קזורר 328605290 · אלון רוזנפלד 322718560  
> **קורס**: למידת מכונה — ד"ר חן חג'ג'

---

## 🌿 מבנה הענפים

| ענף | Commit HEAD | מצב |
|-----|------------|-----|
| `master` | `894cfe0` | ✅ עדכני |
| `reuven` | `894cfe0` | ✅ **זהה ל-master** — כל קומיט ב-master נדחף גם ל-reuven |
| `Alon` | `9b624c9` | 📌 גרסת הגשה ראשונית (לפני כל השיפורים) |
| `main` | `089ecf7` | 📌 Merge של חלק 1 + חלק 2 הראשוני |

> **`reuven` ו-`master` זהים לחלוטין**: כל קומיט שנדחף ל-`master` נדחף מיד גם ל-`reuven` (`git push origin master:reuven`). ההיסטוריה הבאה חלה על שניהם.

---

## סיכום מספרי

| פרמטר | ערך |
|--------|-----|
| סה"כ קומיטים | **37** (master = reuven) |
| תקופה | 10.05.2026 – 02.06.2026 |
| ענפים פעילים | `master` · `reuven` (זהים) |

---

## 🗂️ קומיטים לפי נושא

### 🏁 שלב 1 — מטלה 1: איסוף נתונים (מאי 2026)

---

#### `4f5f7a5` · 10.05.2026
**מטלה 1 – איסוף נתוני סרטים**
- הגשת מטלה 1 הראשונית — סקריפט Python לאיסוף נתוני סרטים מ-IMDb ו-Wikipedia
- ראובן קזורר 328605290 · אלון רוזנפלד 322718560

---

#### `372024d` · 10.05.2026
**עדכון cache — ויקיפדיה לאחר ריצה נוספת**
- עדכון קבצי `wiki_cache.json` ו-`wiki_miss.json` לאחר הרצה נוספת של האיסוף

---

#### `2ef5ffd` · 10.05.2026
**עדכון נתוני כיסוי אמיתיים לאחר ריצת threading + CSS ייצוא PDF**
- עדכון נתוני כיסוי ב-notebook.ipynb לאחר ריצה עם threading
- שיפור CSS לייצוא PDF

---

### 🚀 שלב 2 — מטלה 2: בניית המודל הראשוני (25.05.2026)

---

#### `9b624c9` · 25.05.2026
**מטלה 2 – חיזוי דירוג סרטים**
- הגשת מטלה 2 הראשונית עם:
  - `notebook_part2.ipynb` — מחברת מלאה עם Elastic Net + Random Forest
  - `actor_quality.pkl` — מפת איכות שחקנים (LOO Bayesian encoding)
  - `model.pkl` — המודל השמור
  - קבצי ויזואליזציה: `error_analysis_scatter.png`, `fairness_analysis.png`, `feature_importance.png`, `model_comparison.png`

---

#### `6ed4d0d` · 25.05.2026
**Fix fairness bar chart: align 'Overall (test)' label**
- תיקון גרף Fairness Analysis — התאמת תוית 'Overall (test)' לנתונים הנכונים

---

#### `910072c` · 25.05.2026
**Fix two bugs: fairness chart label mismatch + remove student names**
- תיקון נוסף בגרף Fairness
- הסרת שמות הסטודנטים מתוך קוד המחברת (פרטיות)

---

### 🔧 שלב 3 — שיפור ביצועים ותיקוני באגים (27-28.05.2026)

---

#### `f4bc5c8` · 27.05.2026
**Feature engineering v4: drop budget_log, add 4 high-coverage features**
- הסרת `budget_log` (86% חסר — MNAR — מוטה)
- הוספת 4 פיצ'רים חדשים בכיסוי 100%: `is_sequel`, `is_long_film`, `genre_prestige`, `primary_genre_is_prestige`

---

#### `ba1014a` · 27.05.2026
**Tune models for lower RMSE: actor smoothing, RF search space, EN alpha grid**
- כיוון `smoothing=5` (במקום 10) לאנקודינג LOO של שחקנים
- הרחבת מרחב חיפוש של Random Forest
- עדכון grid של alpha ב-Elastic Net

---

#### `ab19f90` · 27.05.2026
**Add 4 high-signal features derived from existing data (100% coverage)**
- הוספת פיצ'רים נוספים נגזרים ב-100% כיסוי

---

#### `491200d` · 28.05.2026
**Fix RF tuning speed: n_iter 40→20, cv 5→3, max 300 trees**
- הקטנת `n_iter` מ-40 ל-20 וה-`cv` מ-5 ל-3 ב-RandomizedSearchCV
- הגבלת מספר עצים ל-300 (מ-300→600 כמעט אין שיפור)
- חיסכון משמעותי בזמן ריצה

---

### 🐛 שלב 4 — תיקוני באגים קריטיים (31.05.2026)

---

#### `f205b87` · 31.05.2026
**Fix RF crash: n_jobs=1 inside RF, -1 only on outer SearchCV**
- **באג קריטי**: שני `n_jobs=-1` מקוננים = 64 תהליכים במקביל → קריסת RAM
- **תיקון**: `RandomForestRegressor(n_jobs=1)` בתוך Pipeline, `n_jobs=-1` רק ב-SearchCV

---

#### `c3cebf4` · 31.05.2026
**Add RF progress output: print total fits + verbose=2 per-fit timing**
- הוספת הדפסת מספר ה-fits הכולל לפני הרצה
- `verbose=2` ב-RandomizedSearchCV — מדפיס כל fit עם מספר וזמן

---

#### `cd3c362` · 31.05.2026
**Fix GitHub preview: restore missing cell IDs on cells 0 and 1**
- תיקון תצוגה שגויה ב-GitHub ("An error occurred")
- שחזור `id: "cell-0"` ו-`id: "cell-1"` שנמחקו בשגיאה

---

### 📚 שלב 5 — תוכן תיאורטי מחומרי הקורס (31.05.2026)

---

#### `8365429` · 31.05.2026
**Add 4 professor-taught concepts: MCAR/MAR/MNAR, VIF, CART/Gini theory, OOB error**
- §2.1: ניתוח ערכים חסרים — MCAR / MAR / MNAR (הרצאה 2)
- §5.1: VIF (Variance Inflation Factor) עם נוסחה + טבלת סף
- §7: תיאוריה של CART / Gini / Bagging / OOB (הרצאה 5)
- תא OOB Error לחישוב חינמי ללא CV נפרד

---

### 📊 שלב 6 — VIF ותיקון מולטיקולינריות (31.05–01.06.2026)

---

#### `6714947` · 31.05.2026
**Fix VIF cell: remove apostrophe syntax error**
- תיקון שגיאת syntax: apostrophe עברית `'` בתוך string בקוד Python

---

#### `22a1e52` · 31.05.2026
**Remove title_word_count (VIF=103): collinear with log_title_len**
- הסרת `title_word_count` (VIF=103) — כפול עם `log_title_len`
- הוספת תא הסבר VIF עם נוסחה

---

#### `bdba835` · 31.05.2026
**VIF cleanup v2: replace max_actor_quality+runtimeMinutes**
- הסרת `max_actor_quality` (VIF=1083) → תחליף: `actor_quality_spread` (max−mean)
- הסרת `runtimeMinutes` (VIF=67) → תחליף: `is_long_film` (בינארי)
- הסרת `runtime_genre_ratio` (VIF מבני) → תחליף: `log_runtime`

---

#### `c5d341b` · 01.06.2026
**Add PPS (Predictive Power Score) analysis — lesson 3 content**
- §5.2: תא תיאוריה של PPS vs Pearson
- Heatmap מלא של PPS (אסימטרי) + Pearson (משולש תחתון)
- דירוג PPS לכל פיצ'ר כלפי המטרה

---

#### `2579c7b` · 01.06.2026
**Fix structural VIF: replace runtime_genre_ratio with log_runtime**
- `runtime_genre_ratio = runtimeMinutes / genre_count` — מולטיקולינריות מבנית-אלגברית
- תחליף: `log_runtime = log(1+minutes)` — אין תלות אלגברית עם `genre_count`

---

### 🎯 שלב 7 — אופטימיזציה לפיצ'רים (01.06.2026)

---

#### `5cde2c6` · 01.06.2026
**Replace log-transformed features with explainable plain features**
- `log_title_len` → `title_word_count` (מספר מילים — יותר אינטואיטיבי)
- `log_runtime` → `runtimeMinutes` (בשלב זה — הוחלף שוב בהמשך)

---

#### `61a9797` · 01.06.2026
**Add log_numVotes + numVotes_high features for better RMSE/R²**
- `log_numVotes`: log(1 + מספר מדרגים) — popularity signal
- `numVotes_high`: בינארי (>1,000 מדרגים, r=+0.093)
- `num_lead_actors`: מספר שחקנים ראשיים

---

#### `0c8226a` · 02.06.2026
**Fix notebook errors + upgrade features for better Elastic Net (VIF≤5)**
- **תיקון באג קריטי**: `is_long_film` כפול ב-BINARY_COLS
- `runtimeMinutes` → `log_runtime` (לינאריות טובה יותר ל-Elastic Net)
- הוספת `num_lead_actors`

---

#### `34ed998` · 02.06.2026
**Update summary cell (§13) to reflect current v5 feature set**
- עדכון סעיף 13 עם טבלת גרסאות v1–v5
- טבלת פיצ'רים פעילים עם r-values
- טבלת פיצ'רים שהוסרו עם הסיבות
- קריטריוני הגשה מעודכנים

---

### 🚀 שלב 8 — ניסויים ושיפורים (02.06.2026)

---

#### `72133f5` · 02.06.2026
**Add Gradient Boosting (Model 3) + SHAP explainability**
- ניסיון הוספת Gradient Boosting כמודל שלישי
- הוספת SHAP explainability
- *(בוטל בהמשך)*

---

#### `ac0c785` · 02.06.2026
**Fix PPS bug + relax VIF to 10 + add 5 new features for better RMSE**
- תיקון באגים ב-PPS cell
- ניסיון הרחבת ספי VIF וסט פיצ'רים

---

#### `b247520` · 02.06.2026
**Fix PPS code cell (§5.2) — 4 bugs corrected**
- `pivot()` → `pivot_table(aggfunc='mean')` — מונע ValueError
- `y_train` → `y_train.values` — מונע חוסר התאמת index
- `corr()` → `corr(numeric_only=True)` — תאימות pandas 2.x
- `tight_layout()` לפני `suptitle()` — מונע חיתוך כותרת

---

### 🏆 שלב 9 — סט פיצ'רים סופי ומיטובי (02.06.2026)

---

#### `e905140` · 02.06.2026
**Optimal 15-feature set for max R² / min RMSE (VIF≤5)**
- **פיצ'רים חדשים**:
  - `prestige_count` (r=+0.282): ספירת ז'אנרים יוקרתיים
  - `negative_count` (r=−0.315): ספירת ז'אנרים שליליים — חזק מ-Horror בודד!
- **הוסרו** 18 פיצ'רים חלשים (film_age, title_word_count, genre_count...)
- **תוצאה**: 15 פיצ'רים — 5 נומריים + 10 בינאריים

---

#### `6f700d6` · 02.06.2026
**Fix VIF computation + finalize 15 features (5 numeric VIF=1.07-1.16)**
- **גילוי**: VIF מחושב על raw features אינו יציב נומרית (actor_quality std=0.186 → VIF=435 שגוי!)
- **תיקון**: VIF מחושב **אחרי StandardScaler** → VIF אמיתי: **1.07–1.16** לכולם
- `known_actor_ratio` → `has_actors` (בינארי, מפריד קלאסטר LOO)

---

### 🎨 שלב 10 — עיצוב ומראה המחברת (02.06.2026)

---

#### `1eed8cd` · 02.06.2026
**Full notebook markdown refresh — professional & consistent**
- עדכון 20 תאי markdown לעקביות מלאה עם סט הפיצ'רים הנוכחי
- הסרת כל הפניות לפיצ'רים ישנים

---

#### `733408b` · 02.06.2026
**Beautiful notebook design — HTML styling, emojis, color-coded boxes**
- כותרת ראשית עם gradient כהה
- **מערכת צבעים**: כחול (הערות) · ירוק (הצלחה) · צהוב (אזהרות) · אדום (שגיאות) · סגול (תיאוריה)
- אמוג'י לכל סעיף (📂 🔧 📐 🌲 ⚖️ 🏆 🔍 💾)
- קופסאות HTML צבעוניות בכל ממצא מרכזי
- נוסחאות LaTeX · ASCII Pipeline diagram

---

### 🔩 שלב 11 — תיקונים סופיים (02.06.2026)

---

#### `42fb51d` · 02.06.2026
**Critical fix: remove known_actor_ratio from FEATURE_COLS, add has_actors**
- **באג קריטי**: `known_actor_ratio` ב-FEATURE_COLS + `has_actors` ב-BINARY_COLS בלי שנמצא ב-FEATURE_COLS → **KeyError** בהרצה
- **תיקון**: FEATURE_COLS מסונכרן מדויק עם NUMERIC_COLS + BINARY_COLS (15 פיצ'רים)

---

#### `ee071d3` · 02.06.2026
**Fix structure: VIF explanation + section 4 flow + print bug**
- §4: הסבר סדר הפעולות לפי pipeline חן (Train/Test → prepare_data → VIF/PPS)
- §5.1 VIF: הסבר **למה VIF רק על 5 פיצ'רים נומריים** (ולא על בינאריים)
- תיקון print: `has_actors` לא הופיע ברשימת הבינאריים

---

#### `ee48908` · 02.06.2026
**Final fixes: PPS code + summary v5**
- שחזור תיקוני PPS (pivot_table, y_train.values) שנדרסו בעדכון קודם
- הוספת שורת v5 לטבלת הגרסאות בסיכום

---

#### `5a00667` · 02.06.2026
**Convert all Hebrew in code cells to English**
- כל ה-comments, print statements וה-strings בתאי **קוד** — הומרו לאנגלית
- תאי **Markdown** נשארו בעברית (מיועדים למרצה)
- תאים שעודכנו: 6e92ea23, 4f703749, c4b8974c, pps_code, b8e8cb49, 5e3dda65, 5259fb80, 93b718b3

---

### 🧹 שלב 12 — ניקוי המאגר (02.06.2026)

---

#### `94b1383` · 02.06.2026
**Remove temp dev scripts from repo**
- הסרת `fix_vif_features.py` ו-`upgrade_notebook.py` מהמאגר
- קבצי פיתוח שנכנסו בטעות ל-tracking

---

#### `6d102fc` · 02.06.2026
**Update .gitignore: exclude temp dev scripts and PDFs**
- הוספת חוקים ל-.gitignore:
  ```
  add_*.py · fix_*.py · update_*.py · refresh_*.py
  beautify.py · finalize_*.py · full_fix.py · *.pdf
  ```
- מניעת כניסת סקריפטי פיתוח זמניים בעתיד

---

#### `894cfe0` · 02.06.2026
**Add COMMIT_HISTORY.md — full master & reuven history documentation**
- יצירת קובץ זה — תיעוד מלא של 37 הקומיטים
- נדחף ל-`master` ול-`reuven` בו-זמנית

---

## 📈 ציר הזמן — התקדמות ה-R²

| גרסה | commit | שינוי מרכזי | RMSE (RF) | R² (RF) |
|:----:|--------|-------------|:---------:|:-------:|
| v1 | `9b624c9` | genres שבורים, 8 ז'אנרים | 1.192 | 0.212 |
| v2 | `f4bc5c8` | תיקון genre parsing + 20 ז'אנרים | 1.099 | 0.278 |
| v3 | `ba1014a` | actor_quality (LOO Bayesian, r=0.37) | ~1.048 | ~0.344 |
| v4 | `f4bc5c8` | הסרת budget_log (MNAR 86%) | — | — |
| v5 | `e905140` | prestige_count + negative_count (15 פיצ'רים) | ← הרץ | ← הרץ |

**Elastic Net (v5, מאומת)**: Test RMSE = **1.054** · R² = **0.329**

---

## 📁 קבצים במאגר (מצב סופי)

| קובץ | תיאור |
|------|-------|
| `notebook_part2.ipynb` | המחברת הראשית — 45 תאים |
| `actor_quality.pkl` | מפת LOO לאינפרנס |
| `model.pkl` | המודל הטוב ביותר (Pipeline מלא) |
| `error_analysis_scatter.png` | גרף Error Analysis |
| `fairness_analysis.png` | גרף Fairness |
| `feature_importance.png` | גרף חשיבות פיצ'רים |
| `model_comparison.png` | גרף השוואת מודלים |
| `requirements.txt` | חבילות Python נדרשות |
| `README.md` | תיאור הפרויקט |
| `.gitignore` | קבצים שמוחרגים מה-tracking |

---

## 🌿 השוואת ענפים מפורטת

### `master` vs `reuven` — זהים לחלוטין

כל קומיט ב-`master` נדחף מיד גם ל-`reuven`:
```bash
git push origin master          # → master
git push origin master:reuven   # → reuven (אותו commit)
```

| # | Hash | תאריך | הודעה | master | reuven |
|:-:|------|--------|-------|:------:|:------:|
| 37 | `894cfe0` | 02.06 | Add COMMIT_HISTORY.md | ✅ | ✅ |
| 36 | `6d102fc` | 02.06 | Update .gitignore | ✅ | ✅ |
| 35 | `94b1383` | 02.06 | Remove temp dev scripts | ✅ | ✅ |
| 34 | `5a00667` | 02.06 | Convert Hebrew to English | ✅ | ✅ |
| 33 | `ee48908` | 02.06 | Final fixes: PPS + summary v5 | ✅ | ✅ |
| 32 | `ee071d3` | 02.06 | Fix structure: VIF + section 4 | ✅ | ✅ |
| 31 | `42fb51d` | 02.06 | Critical fix: FEATURE_COLS | ✅ | ✅ |
| 30 | `733408b` | 02.06 | Beautiful notebook design | ✅ | ✅ |
| 29 | `1eed8cd` | 02.06 | Full markdown refresh | ✅ | ✅ |
| 28 | `6f700d6` | 02.06 | Fix VIF + finalize 15 features | ✅ | ✅ |
| 27 | `e905140` | 02.06 | Optimal 15-feature set | ✅ | ✅ |
| 26 | `b247520` | 02.06 | Fix PPS code (4 bugs) | ✅ | ✅ |
| 25 | `ac0c785` | 02.06 | Fix PPS + new features | ✅ | ✅ |
| 24 | `72133f5` | 02.06 | Add Gradient Boosting + SHAP | ✅ | ✅ |
| 23 | `34ed998` | 02.06 | Update summary §13 | ✅ | ✅ |
| 22 | `0c8226a` | 02.06 | Fix errors + upgrade EN features | ✅ | ✅ |
| 21 | `61a9797` | 01.06 | Add log_numVotes + numVotes_high | ✅ | ✅ |
| 20 | `5cde2c6` | 01.06 | Explainable plain features | ✅ | ✅ |
| 19 | `2579c7b` | 01.06 | Fix structural VIF → log_runtime | ✅ | ✅ |
| 18 | `c5d341b` | 01.06 | Add PPS analysis (lesson 3) | ✅ | ✅ |
| 17 | `bdba835` | 31.05 | VIF cleanup v2 | ✅ | ✅ |
| 16 | `22a1e52` | 31.05 | Remove title_word_count VIF=103 | ✅ | ✅ |
| 15 | `6714947` | 31.05 | Fix VIF cell syntax error | ✅ | ✅ |
| 14 | `8365429` | 31.05 | Add theory: MCAR/VIF/CART/OOB | ✅ | ✅ |
| 13 | `cd3c362` | 31.05 | Fix GitHub preview | ✅ | ✅ |
| 12 | `c3cebf4` | 31.05 | Add RF progress output | ✅ | ✅ |
| 11 | `f205b87` | 31.05 | Fix RF crash (n_jobs) | ✅ | ✅ |
| 10 | `491200d` | 28.05 | Fix RF tuning speed | ✅ | ✅ |
| 9 | `ab19f90` | 27.05 | Add 4 high-signal features | ✅ | ✅ |
| 8 | `ba1014a` | 27.05 | Tune models for lower RMSE | ✅ | ✅ |
| 7 | `f4bc5c8` | 27.05 | Feature engineering v4 | ✅ | ✅ |
| 6 | `910072c` | 25.05 | Fix 2 bugs + remove names | ✅ | ✅ |
| 5 | `6ed4d0d` | 25.05 | Fix fairness bar chart | ✅ | ✅ |
| 4 | `9b624c9` | 25.05 | מטלה 2 הגשה ראשונית | ✅ | ✅ |
| 3 | `2ef5ffd` | 10.05 | עדכון נתוני כיסוי + CSS | ✅ | ✅ |
| 2 | `372024d` | 10.05 | עדכון cache ויקיפדיה | ✅ | ✅ |
| 1 | `4f5f7a5` | 10.05 | מטלה 1 הגשה ראשונית | ✅ | ✅ |

---

*נוצר מ-`git log` · ענפים `master` ו-`reuven` · 37 קומיטים*
