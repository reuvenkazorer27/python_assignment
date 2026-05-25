# מטלת סיכום – חלק 2: חיזוי דירוג סרטים (IMDb)


---

## תיאור הפרויקט

בניית מודל Machine Learning לחיזוי `averageRating` של סרטים על בסיס נתוני IMDb, תוך שמירה קפדנית על מניעת Data Leakage (ביצועים מדווחים רק על מידע שהיה זמין לפני יציאת הסרט).

## קבצים

| קובץ | תיאור |
|------|--------|
| `notebook_part2.ipynb` | קוד מלא — prepare_data, Elastic Net, Random Forest, Error Analysis, Fairness Analysis |
| `model.pkl` | המודל המאומן הטוב ביותר (Random Forest) מאומן על כלל הנתונים |
| `actor_quality.pkl` | מפת איכות שחקנים (LOO Bayesian encoding) — נדרש בזמן inference |
| `requirements.txt` | גרסאות ספריות |

## תוצאות

| מודל | Train RMSE | CV RMSE (10-fold) | Test RMSE (20%) |
|------|-----------|-------------------|-----------------|
| Elastic Net | ~1.18 | 1.1918 ± 0.0080 | ~1.19 |
| **Random Forest** | ~0.65 | **1.1472 ± 0.0085** | **~1.15** |

## שימוש ב-Inference

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

## הרצת הנוטבוק

```bash
pip install -r requirements.txt
# הניחו את dataset.csv באותה תיקייה
jupyter notebook notebook_part2.ipynb
```

> `dataset.csv` אינו כלול ב-repo (70MB). יש להניחו ידנית לפני הרצה.

## AI Usage Log

חלק זה מתעד שימוש ב-LLM (Claude Sonnet) לצורך סיוע בפיתוח:
- הנדסת פיצ'רים: עזרה בזיהוי בעיות parsing של ז'אנרים ו-LOO encoding לשחקנים
- Debug: איתור שגיאות ב-Pipeline ומניעת Data Leakage
- Code review: בדיקת עמידה בדרישות המדריך (Fairness Analysis, Error Analysis)
- כל החלטות המתודולוגיות (בחירת מודל, פיצ'רים, CV) התקבלו על-ידי הסטודנטים
