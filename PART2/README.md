# מטלת סיכום – חלק 2: חיזוי דירוג סרטים (IMDb)

---

## תיאור קצר של המודל

הפרויקט בונה מודל למידת מכונה שמנבא את דירוג ה-IMDb הממוצע (`averageRating`) של סרט, על סמך נתוני הסרט שנאספו בחלק 1 (כמו ז'אנר, אורך, שחקנים, במאי, מדינת הפקה ועוד).

הנוטבוק `notebook_part2.ipynb` כולל את כל שלבי העבודה: ניקוי והכנת הנתונים, יצירת מאפיינים (features) חדשים מתוך הנתונים הקיימים, בדיקת קשרים בין המשתנים, אימון וכיוונון של שני מודלים שונים (Elastic Net ו-Random Forest), השוואה ביניהם ובחירה במודל הטוב מביניהם, וניתוח שגיאות והוגנות של המודל הנבחר. המודל הסופי נשמר בקובץ `model.pkl`.

לאורך כל התהליך הקפדנו למנוע **Data Leakage**: כל מאפיין שמבוסס על דירוגי סרטים אחרים מחושב רק מתוך סרטים שיצאו *לפני* הסרט המדובר, כך שהמודל לא "רואה" מידע שלא היה זמין במציאות בזמן יציאת הסרט.

---

## קבצים

| קובץ | תיאור |
|------|--------|
| `notebook_part2.ipynb` | קוד מלא — prepare_data, Feature Engineering, VIF, Elastic Net, Random Forest, Error Analysis, Fairness Analysis |
| `model.pkl.zip` | המודל המאומן הטוב ביותר (Elastic Net או Random Forest, לפי השוואת הביצועים) מאומן על כלל הנתונים — קובץ דחוס; יש לחלץ ל-`model.pkl` לפני שימוש |
| `actor_quality.pkl` | מפת איכות שחקנים (LOO Bayesian encoding) — נדרש בזמן inference |
| `requirements.txt` | רשימת דרישות (תלויות) |

---

## דרישות (requirements.txt)

```
numpy==1.26.4
pandas==2.3.3
scikit-learn==1.4.2
matplotlib==3.9.0
seaborn==0.13.2
joblib==1.3.2
statsmodels==0.14.2
scipy==1.13.0
ppscore==1.3.1
```

התקנה:

```bash
pip install -r requirements.txt
```

---

## הוראות הרצה

1. ודאו ש-`dataset.csv` (~70MB, לא כלול ב-repo) נמצא באותה תיקייה כמו הנוטבוק — ניתן להפיק אותו מחדש מ-`PART1/notebook.ipynb`.
2. עבור פיצ'רי הצוות (`director_quality`, `lead_star_quality`, `actor_prime`) נדרשים גם שני קבצי IMDb נוספים שכבר הורדו בחלק 1:
   - **`title.principals.tsv.gz`** — טבלת הצוות של כל סרט (תפקיד וסדר קרדיט). ממנה מזהים את **הבמאי** (`category == 'director'`) ואת **השחקן הראשי** (`ordering == 1`) של כל סרט.
   - **`name.basics.tsv.gz`** — טבלת פרטי אנשים, כולל שנת לידה. משמשת לחישוב `actor_prime` (קרבת השחקנים לגיל שיא הקריירה).
3. התקינו את הדרישות (ראו לעיל) והריצו:

```bash
jupyter notebook notebook_part2.ipynb
```

הריצו את כל התאים לפי הסדר (**Run All** / **Kernel → Restart & Run All**). בסוף הריצה נשמרים `model.pkl` ו-`actor_quality.pkl`.

> המודל המאומן המצורף ל-repo ארוז כ-`model.pkl.zip` (בגלל מגבלת גודל קובץ ב-GitHub). יש לחלץ אותו (`unzip model.pkl.zip` או חילוץ ידני) כדי לקבל את `model.pkl` לפני טעינה עם `joblib.load`.
