# מטלת סיכום – חלק 3: אפליקציית Flask לחיזוי דירוג סרטים

---

## 1. תיאור קצר של הפרויקט

אפליקציית **Flask** שעוטפת את מודל החיזוי שנבנה בחלק 2 (`PART2`) בשירות web פשוט.
המשתמש מזין בדף הבית פרטי סרט (שם, ז'אנרים, אורך, שנת יציאה, מדינת הפקה ושחקנים מובילים),
לוחץ על **Predict Rating**, והאפליקציה מחזירה חיזוי לדירוג ה-IMDb הממוצע (`averageRating`)
של הסרט - בין 1 ל-10 - בלי לרענן את הדף (באמצעות `fetch`).

מבנה האפליקציה:

| קובץ | תיאור |
|------|--------|
| `index.html` (ב-`templates/`) | דף הבית - טופס קלט וכפתור Predict, הצגת התוצאה ב-AJAX |
| `api.py` | שרת Flask - נקודות הקצה `/` ו-`/predict` |
| `assets_data_prep.py` | פונקציית `prepare_data()` ועוזריה - הועתקו מחלק 2 ללא שינוי בלוגיקה |
| `trained_model.pkl.zip` | המודל המאומן מחלק 2 (Random Forest), serialized עם `joblib` - קובץ דחוס; יש לחלץ אותו (האפליקציה מחלצת זאת אוטומטית בהפעלה הראשונה) |
| `feature_maps.pkl` | מפות איכות (actor_quality, genre_momentum וכו') שחושבו בחלק 2 על כלל הדאטאסט, ונדרשות על ידי `prepare_data()` |
| `requirements.txt` | רשימת הספריות הנדרשות (גרסאות) |

---

## 2. הוראות התקנה

יצירת סביבה וירטואלית והתקנת הדרישות:

```bash
cd PART3
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt
```

---

## 3. הוראות הפעלה

```bash
python api.py
```

בהפעלה הראשונה השרת יחלץ את `trained_model.pkl` מתוך `trained_model.pkl.zip` (אם עדיין לא חולץ), יטען
את המודל ואת `feature_maps.pkl`, ויעלה.

---

## 4. כתובת גישה לאפליקציה

```
http://localhost:5000
```

פתחו את הכתובת בדפדפן, מלאו את הטופס ולחצו על **Predict Rating**.

---

## 5. שדות הקלט וטווחי הערכים

| שדה בטופס | תיאור | טווח / פורמט | פיצ'רים שמושפעים ב-`prepare_data()` |
|---|---|---|---|
| **Movie Title** (`primaryTitle`) | שם הסרט | טקסט חופשי, לדוגמה `The Dark Knight Rises` | `is_sequel` |
| **Genres** (`genres`) | ז'אנרים - יש לבחור לפחות אחד | רשימת תיבות סימון מתוך: Drama, Action, Comedy, Thriller, Horror, Documentary, Biography, History, War, Music, Sci-Fi | `genre_Documentary/Horror/Thriller/Biography/Drama/Action`, `prestige_count`, `negative_count`, `genre_momentum` |
| **Runtime Minutes** (`runtimeMinutes`) | אורך הסרט בדקות | מספר חיובי, לדוגמה `148` | `log_runtime`, `is_long_film` |
| **Start Year** (`startYear`) | שנת יציאה | מספר שלם בין 1888 ל-2100, לדוגמה `2024` | `genre_momentum` (לפי הז'אנר הראשון שנבחר) |
| **Country** (`Country`) | מדינת הפקה | טקסט חופשי, לדוגמה `United States` | `country_group` (US / East_Asia / Other) |
| **Lead Actors IDs** (`lead_actors_ids`) | מזהי IMDb (`nconst`) של עד 5 שחקנים מובילים, מופרדים בפסיקים - אופציונלי | לדוגמה `nm0000138, nm0000093` | `actor_quality`, `actor_quality_spread`, `has_actors` |

> את מזהי ה-`nconst` ניתן למצוא בכתובת ה-URL של עמוד השחקן ב-IMDb, לדוגמה: `imdb.com/name/nm0000138`.

> הפיצ'רים `director_quality`, `lead_star_quality` ו-`actor_prime` בחלק 2 חושבו ממפות שנבנו מקובצי
> IMDb כבדים (`title.principals.tsv.gz`, `name.basics.tsv.gz` - במאי הסרט, השחקן הראשי לפי
> סדר קרדיט, ושנות לידה של שחקנים). לצורך הפעלת השירות לא נטענו קבצים אלה, ולכן שלושת הפיצ'רים
> האלה מקבלים ערך קבוע לכל סרט: `director_quality` ו-`lead_star_quality` מקבלים את ממוצע הדירוג
> הכללי (`GLOBAL_MEAN_RATING` ≈ 6.07), ו-`actor_prime` מקבל `0.0`. שאר 16 הפיצ'רים (`actor_quality`,
> `actor_quality_spread`, `has_actors`, `genre_momentum`, `prestige_count`, `negative_count`,
> `log_runtime`, `is_long_film`, `is_sequel`, `country_group` וכל עמודות `genre_*`) מחושבים
> דינמית מתוך שדות הטופס ומהמפות (`feature_maps.pkl`) שחושבו מהדאטאסט המלא של חלק 1-2.

---

## 6. תשובת ה-API ושקיפות הפיצ'רים

נקודת הקצה `POST /predict` מחזירה JSON בפורמט:

```json
{
  "predicted_rating": 6.4,
  "features": {
    "actor_quality": 6.07,
    "prestige_count": 0.0,
    "negative_count": 1.0,
    "log_runtime": 5.0,
    "actor_quality_spread": 0.0,
    "genre_momentum": 6.21,
    "director_quality": 6.07,
    "lead_star_quality": 6.07,
    "actor_prime": 0.0,
    "genre_Documentary": 0.0,
    "genre_Horror": 0.0,
    "genre_Thriller": 0.0,
    "genre_Biography": 0.0,
    "genre_Drama": 1.0,
    "genre_Action": 1.0,
    "is_long_film": 1.0,
    "is_sequel": 0.0,
    "has_actors": 0.0,
    "country_group": "US"
  }
}
```

`predicted_rating` הוא החיזוי הראשי (כנדרש במטלה). השדה `features` הוא תוספת שקיפות -
מציג את **19 הפיצ'רים** המדויקים שחושבו ע"י `prepare_data()` והוזנו ל-`model.predict()`
לקבלת התחזית. בדף הבית, לחיצה על "📊 19 הפיצ'רים שחושבו..." מתחת לתוצאה פותחת אזור
שמציג את כל הערכים האלה (בעברית, עם ✅/❌ לפיצ'רים בינאריים).

---

## 7. שמות חברי הצוות

- ראובן קזורר
- אלון רוזנפלד
