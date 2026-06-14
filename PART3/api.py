"""
api.py - שרת Flask לחיזוי דירוג סרטים (PART 3)

נקודות קצה:
    GET  /         - מחזיר את דף index.html (טופס הקלט)
    POST /predict  - מקבל JSON עם נתוני סרט, מריץ prepare_data() ואז
                      model.predict(), ומחזיר JSON: {"predicted_rating": <ערך>}
"""

import os
import zipfile

import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request

import assets_data_prep as dp


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── טעינת המודל המאומן (חולץ מ-zip אם צריך, בגלל מגבלת הגודל של GitHub) ────
MODEL_PATH = os.path.join(BASE_DIR, 'trained_model.pkl')
MODEL_ZIP_PATH = os.path.join(BASE_DIR, 'trained_model.pkl.zip')

if not os.path.exists(MODEL_PATH) and os.path.exists(MODEL_ZIP_PATH):
    print('Extracting trained_model.pkl from trained_model.pkl.zip ...')
    with zipfile.ZipFile(MODEL_ZIP_PATH) as zf:
        zf.extractall(BASE_DIR)

print('Loading trained_model.pkl ...')
model = joblib.load(MODEL_PATH)

# ── טעינת מפות הפיצ'רים (actor_quality, genre_momentum וכו') לתוך ──────────
#    ה-globals של prepare_data ב-assets_data_prep.py
FEATURE_MAPS_PATH = os.path.join(BASE_DIR, 'feature_maps.pkl')
print('Loading feature_maps.pkl ...')
dp.load_feature_maps(FEATURE_MAPS_PATH)

print('Ready.')

app = Flask(__name__)


# ── שדות קלט נדרשים מהטופס ──────────────────────────────────────────────────
REQUIRED_FIELDS = ['primaryTitle', 'genres', 'runtimeMinutes', 'startYear', 'Country']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(silent=True)
        if data is None:
            # fallback - טופס רגיל (לא JSON)
            data = request.form.to_dict()
        if data is None:
            data = {}
    except Exception:
        data = {}

    # ── 1. בדיקת שדות חסרים ─────────────────────────────────────────────────
    missing = [
        f for f in REQUIRED_FIELDS
        if f not in data or data[f] is None or data[f] == '' or data[f] == []
    ]
    if missing:
        return jsonify({'error': f'שדות חסרים בקלט: {", ".join(missing)}'}), 400

    # ── 2. בדיקת תקינות ערכים ────────────────────────────────────────────────
    try:
        runtime_minutes = float(data['runtimeMinutes'])
        start_year = int(float(data['startYear']))
    except (ValueError, TypeError):
        return jsonify({
            'error': 'runtimeMinutes ו-startYear חייבים להיות מספרים תקינים'
        }), 400

    if runtime_minutes <= 0:
        return jsonify({'error': 'runtimeMinutes חייב להיות מספר חיובי'}), 400
    if not (1888 <= start_year <= 2100):
        return jsonify({'error': 'startYear חייב להיות שנה תקינה (לדוגמה 2024)'}), 400

    primary_title = str(data['primaryTitle']).strip()
    if not primary_title:
        return jsonify({'error': 'primaryTitle לא יכול להיות ריק'}), 400

    country = str(data['Country']).strip()
    if not country:
        return jsonify({'error': 'Country לא יכול להיות ריק'}), 400

    # genres - יכול להגיע כרשימה (JSON array) או כמחרוזת מופרדת בפסיקים
    genres = data['genres']
    if isinstance(genres, str):
        genres = [g.strip() for g in genres.split(',') if g.strip()]
    if not isinstance(genres, list):
        return jsonify({'error': 'genres חייב להיות רשימה של ז\'אנרים'}), 400
    if not genres:
        return jsonify({'error': 'יש לבחור לפחות ז\'אנר אחד'}), 400

    # lead_actors_ids - שדה אופציונלי: רשימת מזהי IMDb (nconst) מופרדים בפסיקים
    actor_ids_raw = data.get('lead_actors_ids', '')
    if isinstance(actor_ids_raw, str):
        actor_ids = [a.strip() for a in actor_ids_raw.split(',') if a.strip()]
    elif isinstance(actor_ids_raw, list):
        actor_ids = [str(a).strip() for a in actor_ids_raw if str(a).strip()]
    else:
        actor_ids = []

    for a in actor_ids:
        if not a.startswith('nm'):
            return jsonify({
                'error': f'מזהה שחקן לא תקין: "{a}" - מזהה IMDb חייב להתחיל ב-"nm" (לדוגמה nm0000138)'
            }), 400

    # ── 3+4. בניית DataFrame, prepare_data ו-model.predict ───────────────────
    try:
        row = {
            'tconst': 'tt_new_film',
            'primaryTitle': primary_title,
            'genres': str(genres),
            'runtimeMinutes': runtime_minutes,
            'startYear': start_year,
            'Country': country,
            'Language': np.nan,
            'lead_actors_ids': str(actor_ids),
        }
        df = pd.DataFrame([row])

        X = dp.prepare_data(df)
        prediction = model.predict(X)[0]
        predicted_rating = round(float(prediction), 1)
        # הדירוג מוגבל לטווח 1-10 (IMDb averageRating)
        predicted_rating = max(1.0, min(10.0, predicted_rating))

    except Exception as e:
        return jsonify({'error': f'שגיאה פנימית בעת חישוב התחזית: {e}'}), 500

    return jsonify({'predicted_rating': predicted_rating})


if __name__ == '__main__':
    app.run(debug=True)
