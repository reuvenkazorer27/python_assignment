# מטלת סיכום – חלק 2: חיזוי דירוג סרטים (IMDb)

---

## תיאור קצר של המודל

בניית מודל Machine Learning לחיזוי `averageRating` של סרטים על בסיס נתוני IMDb (סט הנתונים שנאסף בחלק 1).

הנוטבוק `notebook_part2.ipynb` כולל: `prepare_data` + הנדסת פיצ'רים (20 עמודות, כולל פיצ'רי LOO Bayesian temporal), VIF, Pipeline (KNNImputer / RobustScaler / OneHotEncoder), כיוונון Elastic Net (GridSearchCV) ו-Random Forest (RandomizedSearchCV), השוואת מודלים, Feature Importance, Error Analysis ו-Fairness Analysis.

לאורך כל הפיתוח נשמרת מניעה קפדנית של **Data Leakage** — ביצועים מדווחים רק על מידע שהיה זמין לפני יציאת הסרט (סינון זמני + LOO בכל פיצ'ר מבוסס-דירוג).

### תוצאות

| מודל | CV RMSE | Test RMSE | Adj. R² |
|------|---------|-----------|---------|
| **Elastic Net** ✅ | **1.0650** | **1.0680** | 0.3227 |
| Random Forest | 1.0249 | 1.0713 | 0.3727 |

נבחר **Elastic Net** — Test RMSE נמוך יותר ופער overfit זניח (CV≈Test), לעומת Random Forest שמראה overfit (gap≈+0.087). המודל הנבחר נשמר ב-`model.pkl`.

### הפיצ'רים (20 עמודות לפני המודל)

#### נומריים (9) — כולם מחושבים ב-`prepare_data` עם סינון זמני + LOO

| פיצ'ר | r | תיאור |
|--------|:----:|-------|
| 🥇 `genre_momentum` | **+0.40** | ממוצע LOO של דירוג סרטים מאותו ז'אנר ב-3 שנים קודמות |
| 🥈 `actor_quality` | **+0.37** | LOO Bayesian — איכות צוות השחקנים (סרטים מהעבר בלבד) |
| `director_quality` | **~+0.35** | LOO Bayesian על הבמאי (סרטים מהעבר בלבד) |
| `negative_count` | **−0.32** | Horror+Thriller+Action+Comedy+Sci-Fi |
| `lead_star_quality` | **~+0.30** | LOO Bayesian על השחקן הראשי (ordering=1) |
| `prestige_count` | **+0.28** | Documentary+Biography+History+War+Music |
| `log_runtime` | +0.15 | log(1+דקות) |
| `actor_quality_spread` | — | max−mean: כמה הכוכב הבולט שונה משאר ההרכב |
| `actor_prime` | — | קרבת גיל השחקנים לשיא הקריירה (birthYear, ללא דירוגים → ללא leakage) |

#### בינאריים (9)

`genre_Documentary`, `genre_Horror`, `genre_Thriller`, `genre_Biography`, `genre_Drama`, `genre_Action`, `is_long_film`, `is_sequel`, `has_actors`

#### קטגורי → OHE (2 דמי-עמודות)

`country_group` → `drop=['Other']` (קטגוריית ייחוס מפורשת, לא `drop='first'`) → `cg_East_Asia`, `cg_US`

### מניעת Data Leakage

- **סינון זמני**: כל פיצ'ר מבוסס-דירוג (actor/director/lead_star/genre) מחושב רק מסרטים עם `year < year_הסרט_הנוכחי`
- **LOO (Leave-One-Out)**: הסרט עצמו לעולם לא נכלל בחישוב הציון שלו
- **CV ללא דליפה**: `leak_free_cv()` מחשב מחדש את כל מפות האיכות (שחקן/במאי/כוכב/ז'אנר) על ה-train של כל fold בנפרד
- **מגבלה ידועה (snapshot)**: הדאטה נאסף בנקודת זמן אחת, כך שציוני אנשים עשויים לכלול גם דירוגים שנצברו אחרי יציאת הסרט הנוכחי. הסינון הזמני מצמצם זאת משמעותית אך לא מבטל לחלוטין — מתועד גם בנוטבוק (תא תיעוד ייעודי) ובדוח, בהתאם להנחיית המרצה.

---

## קבצים

| קובץ | תיאור |
|------|--------|
| `notebook_part2.ipynb` | קוד מלא — prepare_data, Feature Engineering, VIF, Elastic Net, Random Forest, Error Analysis, Fairness Analysis |
| `model.pkl` | המודל המאומן הטוב ביותר (Elastic Net) מאומן על כלל הנתונים |
| `actor_quality.pkl` | מפת איכות שחקנים (LOO Bayesian encoding) — נדרש בזמן inference |
| `requirements.txt` | רשימת דרישות (תלויות) |

---

## דרישות (requirements.txt)

```
numpy==1.26.4
pandas==2.2.1
scikit-learn==1.4.2
matplotlib==3.9.0
seaborn==0.13.2
joblib==1.3.2
statsmodels==0.14.2
```

התקנה:

```bash
pip install -r requirements.txt
```

---

## הוראות הרצה

1. ודאו ש-`dataset.csv` (~70MB, לא כלול ב-repo) נמצא באותה תיקייה כמו הנוטבוק — ניתן להפיק אותו מחדש מ-`PART1/notebook.ipynb`.
2. עבור פיצ'רי הצוות (`director_quality`, `lead_star_quality`, `actor_prime`) נדרשים גם קבצי IMDb (`title.principals.tsv.gz`, `name.basics.tsv.gz`) בתיקיית `../PART1/imdb_data/`.
3. התקינו את הדרישות (ראו לעיל) והריצו:

```bash
jupyter notebook notebook_part2.ipynb
```

הריצו את כל התאים לפי הסדר (**Run All** / **Kernel → Restart & Run All**). בסוף הריצה נשמרים `model.pkl` ו-`actor_quality.pkl`.

### שימוש ב-Inference (לאחר אימון)

```python
import joblib
import pandas as pd
from notebook_part2 import prepare_data, compute_actor_quality_map

# Load actor quality map
aq = joblib.load('actor_quality.pkl')
ACTOR_QUALITY_MAP  = aq['actor_quality_map']
GLOBAL_MEAN_RATING = aq['global_mean_rating']

# Load model and predict
model = joblib.load('model.pkl')
X_new = prepare_data(df_new_films)
predictions = model.predict(X_new)
```
