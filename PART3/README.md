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
| **Start Year** (`startYear`) | שנת יציאה | מספר שלם בין 1888 ל-2100, לדוגמה `2024` | `genre_momentum`, `actor_prime` |
| **Country** (`Country`) | מדינת הפקה | טקסט חופשי, לדוגמה `United States` | `country_group` (US / East_Asia / Other) |
| **Lead Actors IDs** (`lead_actors_ids`) | מזהי IMDb (`nconst`) של עד 5 שחקנים מובילים, מופרדים בפסיקים - אופציונלי | לדוגמה `nm0000138, nm0000093` | `actor_quality`, `actor_quality_spread`, `has_actors`, `lead_star_quality` |

> את מזהי ה-`nconst` ניתן למצוא בכתובת ה-URL של עמוד השחקן ב-IMDb, לדוגמה: `imdb.com/name/nm0000138`.

> הפיצ'רים `director_quality` ו-`lead_star_quality` בחלק 2 חושבו ממפות שנבנו מקובצי IMDb כבדים
> (`title.principals.tsv.gz`, `name.basics.tsv.gz`). לצורך הפעלת השירות לא נטענו קבצים אלה,
> ולכן הערכים ל-`director_quality` (ול-`lead_star_quality` כשהשחקן הראשון אינו מוכר) מתבססים על
> ממוצע הדירוג הכללי (`GLOBAL_MEAN_RATING`) - שאר הפיצ'רים מחושבים מהדאטאסט המלא של חלק 1-2.

---

## 6. שמות חברי הצוות

- ראובן קזורר
- אלון רוזנפלד
