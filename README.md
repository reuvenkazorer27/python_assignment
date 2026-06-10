# מטלת סיכום – חיזוי דירוג סרטים (IMDb)

**קורס:** למידת מכונה / כריה וניתוח נתונים מתקדם

| | |
|---|---|
| **שם** | ראובן קזורר |
| **שם** | אלון רוזנפלד |

**קישור למאגר:** [https://github.com/reuvenkazorer27/python_assignment](https://github.com/reuvenkazorer27/python_assignment)

---

## מבנה המאגר

הפרויקט מחולק לשני חלקים, כל אחד בתיקייה נפרדת:

### 📁 [`PART1/`](PART1/) — חלק 1: איסוף נתונים

איסוף סט נתונים מקיף של סרטי קולנוע מ-IMDb (Non-Commercial Datasets) ומ-Wikipedia (web scraping), כולל ניקוי, סינון וחיבור הנתונים לקובץ `dataset.csv` שמשמש בסיס לחלק 2.

**קבצים עיקריים:** `notebook.ipynb`, `dataset.csv`, `wiki_cache.json` / `wiki_miss.json`, `imdb_data/`

ראו [`PART1/README.md`](PART1/README.md) לפירוט מלא של שיטת האיסוף ומבנה הנתונים.

### 📁 [`PART2/`](PART2/) — חלק 2: חיזוי דירוג סרטים

בניית מודל Machine Learning לחיזוי `averageRating` על בסיס סט הנתונים מחלק 1, כולל הנדסת פיצ'רים מתקדמת (LOO Bayesian encoding עם סינון זמני למניעת Data Leakage), VIF, Pipeline (imputation/scaling/OHE), Elastic Net ו-Random Forest, Error Analysis ו-Fairness Analysis.

**קבצים עיקריים:** `notebook_part2.ipynb`, `model.pkl`, `actor_quality.pkl`, `requirements.txt`

ראו [`PART2/README.md`](PART2/README.md) לפירוט מלא של הפיצ'רים, המתודולוגיה והתוצאות.

---

## הרצה

כל חלק רץ באופן עצמאי מתוך התיקייה שלו:

```bash
# חלק 1
cd PART1
jupyter notebook notebook.ipynb

# חלק 2
cd PART2
pip install -r requirements.txt
jupyter notebook notebook_part2.ipynb
```

> חלק 2 משתמש בקבצי IMDb (`title.principals.tsv.gz`, `name.basics.tsv.gz`) מתוך `PART1/imdb_data/` עבור פיצ'רי צוות (`director_quality`, `lead_star_quality`, `actor_prime`).
