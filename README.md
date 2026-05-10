# מטלה 1 – איסוף נתוני סרטים

**קורס:** כריה וניתוח נתונים מתקדם  
**חלק:** 1 מתוך 3


**קישור למאגר:** [https://github.com/reuvenkazorer27/python_assignment](https://github.com/reuvenkazorer27/python_assignment)

---

## תיאור הפרויקט

מטלה זו אוספת סט נתונים מקיף של סרטי קולנוע (ללא סדרות) ממקורות הציבוריים של IMDb ומ-Wikipedia.
סט הנתונים ישמש בסיס לבניית מודלי חיזוי ואפליקציית Flask בחלקים הבאים של הפרויקט.

**טווח שמות:** סרטים שכותרתם מתחילה באותיות **Bm עד Bz** (אותיות קטנות).

---

## מקורות הנתונים

| מקור | נתונים |
|------|--------|
| [IMDb Non-Commercial Datasets](https://developer.imdb.com/non-commercial-datasets/) | פרטי סרט, דירוגים, שחקנים |
| Wikipedia (web scraping) | שפה, מדינה, תקציב, הכנסות, עלילה |

קבצי IMDb שנדרשים:
- `title.basics.tsv.gz` – פרטי כותרת
- `title.ratings.tsv.gz` – דירוגי IMDb
- `title.principals.tsv.gz` – שחקנים וצוות
- `name.basics.tsv.gz` – פרטי אנשים

---

## התקנת תלויות

```bash
pip install pandas requests beautifulsoup4 tqdm
```

**דרישות:** Python 3.8 ומעלה

---

## הרצה

```bash
jupyter notebook notebook.ipynb
```

הרץ את כל התאים לפי הסדר (**Run All** / **Kernel → Restart & Run All**).

הקוד מוריד אוטומטית את קבצי IMDb בהרצה הראשונה (דורש חיבור לאינטרנט).  
ריצות עוקבות ישתמשו בקבצים המקומיים ובקבצי ה-cache של Wikipedia.

---

## שיטת האיסוף

### שלב 1 – טעינה וסינון מ-title.basics

קריאת `title.basics.tsv.gz` ויישום הפילטרים הבאים:

| פילטר | ערך | סיבה |
|-------|-----|------|
| `titleType == 'movie'` | בלבד | הוצאת סדרות, מיני-סדרות וכו' |
| `startYear <= 2024` | עד 2024 כולל | הגבלת טווח שנים לפי דרישת המטלה |
| `runtimeMinutes` בין 60 ל-300 | 60–300 דקות | הסרת סרטים קצרים מדי או ארוכים חריגים |
| `primaryTitle` מתחיל ב-Bm עד Bz | 2 אותיות ראשונות | חלוקת עומס בין קבוצות |

### שלב 2 – JOIN עם דירוגים (title.ratings)

**LEFT JOIN** של טבלת הסרטים עם `title.ratings.tsv.gz` על עמודת `tconst`.  
נוספו עמודות: `averageRating`, `numVotes`.  
שימוש ב-LEFT JOIN שומר על כל הסרטים גם אם אין להם דירוג.

### שלב 3 – חילוץ שחקנים מובילים (title.principals)

קריאת `title.principals.tsv.gz` וסינון לרשומות שבהן `category == 'actor'`.  
מיון לפי `ordering` (סדר קרדיט) ולקיחת עד 5 שחקנים ראשונים לכל סרט.  
**LEFT JOIN** על `tconst` → עמודה `lead_actors_ids` (רשימת מזהי nconst).

### שלב 4 – העשרה מ-Wikipedia (web scraping)

כל ה-scraping מבוצע עם **`ThreadPoolExecutor` (5 workers במקביל)** לקיצור זמן הריצה.

לכל סרט מנסים מספר כתובות URL לפי הסדר הבא:

1. `/wiki/{Title} ({Year} film)` – ניסיון ראשון מדויק
2. `/wiki/{Title} (film)` – ללא שנה
3. `/wiki/{Title}` – שם גולמי

אם אחת מהכתובות מחזירה דף **disambiguation** (כשיש כמה סרטים בשם זהה), הקוד עוקב אוטומטית לקישור הסרט שתואם את שנת היציאה. אם אף כתובת לא הצליחה, מבצעים **חיפוש Wikipedia** בכתובת `/w/index.php?search=` עם מונחי "film" ו-"year".

מהדף שנמצא, חילוץ מה-infobox:

| שדה | מקור בדף |
|-----|----------|
| `Language` | שדה Language |
| `Country` | שדה Country |
| `budget` | שדה Budget (המרה למיליוני USD, כולל ממוצע טווחים עם en-dash) |
| `BoxOffice` | שדה Box office |
| `plot` | קטע Plot/Synopsis בדף, ובמידת הצורך – פסקת הפתיחה |

#### מנגנון ה-Cache

| קובץ | תוכן |
|------|------|
| `wiki_cache.json` | tconsts שנמצאו עם לפחות שדה אחד – נטענים מיד בריצות עוקבות |
| `wiki_miss.json` | tconsts שאושר שאינם בויקיפדיה (כל URL החזיר 404) – מדולגים מיד |

כישלונות זמניים (שגיאות רשת) **אינם נשמרים** בcache כדי שיחזרו בריצה הבאה.

---

## קבצי פלט

| קובץ | תוכן |
|------|------|
| `dataset.csv` | סט הנתונים הסופי (6,668 סרטים) |
| `notebook.ipynb` | קוד Python המלא עם הסברים בעברית |
| `wiki_cache.json` | cache של בקשות Wikipedia שהצליחו |
| `wiki_miss.json` | cache של tconsts שאינם בויקיפדיה |
| `imdb_data/` | קבצי IMDb שהורדו (לא כלולים ב-git) |

---

## מבנה dataset.csv

| עמודה | סוג | מקור | תיאור |
|-------|-----|------|-------|
| `tconst` | String | IMDb | מזהה ייחודי של הסרט |
| `primaryTitle` | String | IMDb | שם הסרט |
| `startYear` | Integer | IMDb | שנת יציאה לאקרנים |
| `genres` | List[String] | IMDb | רשימת ז׳אנרים |
| `lead_actors_ids` | List[String] | IMDb | עד 5 מזהי nconst של שחקנים מובילים |
| `runtimeMinutes` | Integer | IMDb | משך הסרט בדקות |
| `averageRating` | Float | IMDb | ממוצע דירוג (1.0–10.0) |
| `Language` | String | Wikipedia | שפה ראשית |
| `Country` | String | Wikipedia | מדינת הפקה |
| `numVotes` | Integer | IMDb | מספר מדרגים |
| `budget` | Float | Wikipedia | תקציב הפקה (מיליוני USD) |
| `BoxOffice` | Float | Wikipedia | הכנסות גלובליות (מיליוני USD) |
| `plot` | String | Wikipedia | תקציר הסרט |

---

## סטטיסטיקות סט הנתונים

| פרמטר | ערך |
|-------|-----|
| סך סרטים | 6,668 |
| טווח שנים | 1905–2024 |
| טווח משך | 60–300 דקות |
| טווח דירוג | 1.1–9.8 |

### כיסוי שדות (% ערכים לא-null)

| שדה | כיסוי | הערה |
|-----|-------|------|
| `tconst` | 100% | מזהה IMDb |
| `primaryTitle` | 100% | שם הסרט |
| `startYear` | 100% | שנת יציאה |
| `genres` | 100% | ז'אנרים |
| `lead_actors_ids` | 100% | שחקנים מובילים |
| `runtimeMinutes` | 100% | משך |
| `averageRating` | 74.1% | חסר בסרטים ישנים ללא מדרגים |
| `numVotes` | 74.1% | זהה ל-averageRating |
| `Language` | 28.0% | רוב הסרטים אינם מופיעים ב-Wikipedia |
| `Country` | 28.1% | זהה לסיבת Language |
| `budget` | 5.0% | מצוין רק בסרטים מסחריים בולטים |
| `BoxOffice` | 6.0% | מצוין רק בסרטים מסחריים בולטים |
| `plot` | 28.6% | נחלץ מקטע Plot/Synopsis או פסקת פתיחה |
