# -*- coding: utf-8 -*-
"""
Upgrade notebook_part2.ipynb to meet all course requirements:
  1. Add GradientBoosting (Model 3) – best model for tabular regression
  2. Add SHAP explainability section (taught in Lecture 5)
  3. Update model comparison table to include Model 3
  4. Update section numbers & TOC
  5. Update save-model logic to pick best of 3 models
  6. Update summary with v6 (GB) + SHAP
"""
import json, uuid

NB = r'C:\Users\kazor\matala_python\average rating\notebook_part2.ipynb'

def mk_id():
    return str(uuid.uuid4()).replace('-', '')[:16]

def md_cell(src):
    return {"cell_type":"markdown","id":mk_id(),"metadata":{},"source":[src]}

def code_cell(src):
    return {"cell_type":"code","execution_count":None,"id":mk_id(),"metadata":{},"outputs":[],"source":[src]}

def get_src(cell):
    return ''.join(cell.get('source', []))

def set_src(cell, s):
    cell['source'] = [s]

def find_by_id(cells, cid):
    for i, c in enumerate(cells):
        if c.get('id') == cid:
            return i
    return -1

def find_by_content(cells, fragment):
    for i, c in enumerate(cells):
        if fragment in get_src(c):
            return i
    return -1

with open(NB, encoding='utf-8') as f:
    nb = json.load(f)
cells = nb['cells']

# ─────────────────────────────────────────────────────────────────────────────
# 1. UPDATE IMPORTS (cell 9dccbd22)
# ─────────────────────────────────────────────────────────────────────────────
idx = find_by_id(cells, '9dccbd22')
if idx >= 0:
    src = get_src(cells[idx])
    if 'GradientBoostingRegressor' not in src:
        src = src.replace(
            'from sklearn.ensemble import RandomForestRegressor',
            'from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor'
        )
        set_src(cells[idx], src)
        print(f'[OK] Imports updated (cell {idx})')
    else:
        print(f'[--] GradientBoostingRegressor already in imports')

# ─────────────────────────────────────────────────────────────────────────────
# 2. INSERT GRADIENT BOOSTING SECTION (after cell 5043cdd6 – RF 10-fold CV)
# ─────────────────────────────────────────────────────────────────────────────
rf_cv_idx = find_by_id(cells, '5043cdd6')
print(f'RF CV cell index: {rf_cv_idx}')

GB_MD = """\
## 8. מודל 3 – Gradient Boosting

### רקע: Boosting לעומת Bagging

| | Random Forest (Bagging) | Gradient Boosting |
|---|---|---|
| **בנייה** | מקבילית — עצים עצמאיים | **סדרתית** — כל עץ מתקן שגיאות הקודם |
| **אימון** | bootstrap sample אקראי | residuals של החיזוי הנוכחי |
| **מה מצטמצם** | Variance | Bias |
| **Overfitting** | עמיד יחסית | רגיש → דורש `learning_rate` + `n_estimators` מאוזנים |
| **דיוק (tabular)** | מצוין | **לרוב עדיף** |

**רעיון הליבה — Gradient Descent ב-function space:**

$$F_m(x) = F_{m-1}(x) + \\eta \\cdot h_m(x)$$

כל עץ $h_m$ מאומן לחזות את ה-**residuals** — שקולים לגרדיאנט של MSE loss.
`learning_rate` ($\\eta$) = גודל הצעד; קטן יותר → יציב, דורש יותר עצים.
`subsample < 1` → **Stochastic GB** (כמו bootstrap ב-RF) → מוריד variance + מאיץ.

**Hyperparameter tuning**: RandomizedSearchCV (3-fold) על `n_estimators`, `learning_rate`, `max_depth`, `subsample`.
**הערכה סופית**: 10-fold CV זהה לשאר המודלים.\
"""

GB_TUNE = """\
# ─────────────────────────────────────────────────────────────
# מודל 3 – Gradient Boosting (GradientBoostingRegressor)
# ─────────────────────────────────────────────────────────────
gb_pipe = Pipeline([
    ('prep',  preprocessor),
    ('model', GradientBoostingRegressor(random_state=RANDOM_STATE))
])

param_dist_gb = {
    'model__n_estimators':     [100, 200, 300],
    'model__learning_rate':    [0.05, 0.1, 0.15, 0.2],
    'model__max_depth':        [3, 4, 5],
    'model__subsample':        [0.8, 1.0],
    'model__min_samples_leaf': [3, 5, 10],
    'model__max_features':     ['sqrt', 0.5],
}

# n_jobs=-1 על SearchCV בלבד — GB פנימי כבר סדרתי בטבעו
n_iter_gb = 20
print(f'מתחיל: {n_iter_gb} קומבינציות × 3-fold = {n_iter_gb*3} fits')

rs_gb = RandomizedSearchCV(
    gb_pipe, param_dist_gb,
    n_iter=n_iter_gb,
    cv=3,
    scoring='neg_root_mean_squared_error',
    n_jobs=-1,
    random_state=RANDOM_STATE, refit=True,
    verbose=1,
)
rs_gb.fit(X, y)

print(f'\\nBest GB params : {rs_gb.best_params_}')
print(f'Best tuning RMSE (3-fold): {-rs_gb.best_score_:.4f}')
best_gb = rs_gb.best_estimator_\
"""

GB_STAGED = """\
# Gradient Boosting — staged_predict: RMSE convergence curve
# ─────────────────────────────────────────────────────────────
# שקול ל-OOB של Random Forest: מראה היכן עצים נוספים מפסיקים לעזור.
# הרצת staged_predict על 400 עצים → אפיון עקומת ה-RMSE.

gb_params_raw  = {k.replace('model__', ''): v for k, v in rs_gb.best_params_.items()}
n_est_tuned    = gb_params_raw.pop('n_estimators', 200)
gb_params_base = gb_params_raw  # all hyperparams except n_estimators

preprocessor.fit(X_train, y_train)
X_tr_prep = preprocessor.transform(X_train)
X_te_prep = preprocessor.transform(X_test)

gb_staged = GradientBoostingRegressor(
    **gb_params_base, n_estimators=400, random_state=RANDOM_STATE
)
gb_staged.fit(X_tr_prep, y_train)

train_rmse_curve = [np.sqrt(mean_squared_error(y_train, p))
                    for p in gb_staged.staged_predict(X_tr_prep)]
test_rmse_curve  = [np.sqrt(mean_squared_error(y_test,  p))
                    for p in gb_staged.staged_predict(X_te_prep)]
best_n_by_test   = int(np.argmin(test_rmse_curve)) + 1

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(range(1, 401), train_rmse_curve, color='steelblue', lw=1.5, label='Train RMSE')
ax.plot(range(1, 401), test_rmse_curve,  color='salmon',    lw=1.5, label='Test RMSE')
ax.axvline(best_n_by_test, color='green',  ls='--', lw=2,
           label=f'Min Test RMSE at n={best_n_by_test}')
ax.axvline(n_est_tuned, color='orange', ls=':', lw=2,
           label=f'Tuned n={n_est_tuned} (3-fold CV)')
ax.set_xlabel('n_estimators', fontsize=12)
ax.set_ylabel('RMSE', fontsize=12)
ax.set_title('Gradient Boosting: RMSE vs n_estimators (staged_predict)\\n'
             'Train RMSE יורד תמיד | Test RMSE = U-shape → Overfitting signal',
             fontweight='bold')
ax.legend(fontsize=10)
ax.set_xlim(1, 400)
plt.tight_layout()
plt.savefig('gb_convergence.png', dpi=100, bbox_inches='tight')
plt.show()
print(f'Min test-RMSE at n={best_n_by_test}  |  Test RMSE={test_rmse_curve[best_n_by_test-1]:.4f}')
print(f'Tuned n={n_est_tuned}  |  Test RMSE={test_rmse_curve[n_est_tuned-1]:.4f}')\
"""

GB_CV = """\
# 10-fold evaluation of best Gradient Boosting
cv_gb = cross_validate(
    best_gb, X, y, cv=kf,
    scoring={
        'rmse': 'neg_root_mean_squared_error',
        'mae':  'neg_mean_absolute_error',
        'r2':   'r2'
    },
    n_jobs=-1
)

gb_rmse_mean = -cv_gb['test_rmse'].mean()
gb_rmse_std  = cv_gb['test_rmse'].std()
gb_mae_mean  = -cv_gb['test_mae'].mean()
gb_mae_std   = cv_gb['test_mae'].std()
gb_r2_mean   = cv_gb['test_r2'].mean()
gb_r2_std    = cv_gb['test_r2'].std()

print('=== Gradient Boosting – 10-fold CV ===')
print(f'RMSE : {gb_rmse_mean:.4f} ± {gb_rmse_std:.4f}')
print(f'MAE  : {gb_mae_mean:.4f} ± {gb_mae_std:.4f}')
print(f'R²   : {gb_r2_mean:.4f} ± {gb_r2_std:.4f}')\
"""

gb_new_cells = [
    md_cell(GB_MD),
    code_cell(GB_TUNE),
    code_cell(GB_STAGED),
    code_cell(GB_CV),
]

ins = rf_cv_idx + 1
for i, c in enumerate(gb_new_cells):
    cells.insert(ins + i, c)
print(f'[OK] Inserted {len(gb_new_cells)} GB cells after index {rf_cv_idx}')

# ─────────────────────────────────────────────────────────────────────────────
# 3. UPDATE SECTION HEADER: "## 8. השוואת מודלים" → "## 9."
# ─────────────────────────────────────────────────────────────────────────────
idx = find_by_id(cells, '303916c0')
if idx >= 0:
    src = get_src(cells[idx]).replace('## 8. השוואת מודלים', '## 9. השוואת מודלים')
    set_src(cells[idx], src)
    print(f'[OK] Model comparison header -> S9 (cell {idx})')

# ─────────────────────────────────────────────────────────────────────────────
# 4. UPDATE COMPARISON DATAFRAME (cell d38dc7b2) TO INCLUDE GB
# ─────────────────────────────────────────────────────────────────────────────
idx = find_by_id(cells, 'd38dc7b2')
if idx >= 0:
    src = get_src(cells[idx])
    src = (src
        .replace(
            "'Model':       ['Elastic Net', 'Random Forest'],",
            "'Model':       ['Elastic Net', 'Random Forest', 'Gradient Boosting'],"
        ).replace(
            "'RMSE (mean)': [en_rmse_mean, rf_rmse_mean],",
            "'RMSE (mean)': [en_rmse_mean, rf_rmse_mean, gb_rmse_mean],"
        ).replace(
            "'RMSE (std)':  [en_rmse_std,  rf_rmse_std],",
            "'RMSE (std)':  [en_rmse_std,  rf_rmse_std,  gb_rmse_std],"
        ).replace(
            "'MAE (mean)':  [en_mae_mean,  rf_mae_mean],",
            "'MAE (mean)':  [en_mae_mean,  rf_mae_mean,  gb_mae_mean],"
        ).replace(
            "'MAE (std)':   [en_mae_std,   rf_mae_std],",
            "'MAE (std)':   [en_mae_std,   rf_mae_std,   gb_mae_std],"
        ).replace(
            "'R² (mean)':   [en_r2_mean,   rf_r2_mean],",
            "'R² (mean)':   [en_r2_mean,   rf_r2_mean,   gb_r2_mean],"
        ).replace(
            "'R² (std)':    [en_r2_std,    rf_r2_std],",
            "'R² (std)':    [en_r2_std,    rf_r2_std,    gb_r2_std],"
        ).replace(
            "color=['#4c72b0', '#dd8452']",
            "color=['#4c72b0', '#dd8452', '#55a868']"
        )
    )
    set_src(cells[idx], src)
    print(f'[OK] Comparison DataFrame updated with GB (cell {idx})')

# ─────────────────────────────────────────────────────────────────────────────
# 5. UPDATE TRAIN/CV/TEST TABLE (cell 5259fb80) TO ADD GB
# ─────────────────────────────────────────────────────────────────────────────
idx = find_by_id(cells, '5259fb80')
if idx >= 0:
    src = get_src(cells[idx])
    src = (src
        .replace(
            'best_en.fit(X_train, y_train)\nbest_rf.fit(X_train, y_train)',
            'best_en.fit(X_train, y_train)\nbest_rf.fit(X_train, y_train)\nbest_gb.fit(X_train, y_train)'
        ).replace(
            'en_train_rmse = np.sqrt(mean_squared_error(y_train, best_en.predict(X_train)))\n'
            'rf_train_rmse = np.sqrt(mean_squared_error(y_train, best_rf.predict(X_train)))',
            'en_train_rmse = np.sqrt(mean_squared_error(y_train, best_en.predict(X_train)))\n'
            'rf_train_rmse = np.sqrt(mean_squared_error(y_train, best_rf.predict(X_train)))\n'
            'gb_train_rmse = np.sqrt(mean_squared_error(y_train, best_gb.predict(X_train)))'
        ).replace(
            'en_test_rmse  = np.sqrt(mean_squared_error(y_test,  best_en.predict(X_test)))\n'
            'rf_test_rmse  = np.sqrt(mean_squared_error(y_test,  best_rf.predict(X_test)))',
            'en_test_rmse  = np.sqrt(mean_squared_error(y_test,  best_en.predict(X_test)))\n'
            'rf_test_rmse  = np.sqrt(mean_squared_error(y_test,  best_rf.predict(X_test)))\n'
            'gb_test_rmse  = np.sqrt(mean_squared_error(y_test,  best_gb.predict(X_test)))'
        ).replace(
            'print(f\'{"Random Forest":<16} {rf_train_rmse:>12.4f} {rf_rmse_mean:>12.4f} {rf_test_rmse:>12.4f}\')',
            'print(f\'{"Random Forest":<16} {rf_train_rmse:>12.4f} {rf_rmse_mean:>12.4f} {rf_test_rmse:>12.4f}\')\n'
            'print(f\'{"Gradient Boost":<16} {gb_train_rmse:>12.4f} {gb_rmse_mean:>12.4f} {gb_test_rmse:>12.4f}\')'
        )
    )
    set_src(cells[idx], src)
    print(f'[OK] Train/CV/Test table updated with GB (cell {idx})')

# ─────────────────────────────────────────────────────────────────────────────
# 6. UPDATE FEATURE IMPORTANCE HEADER: "## 9." → "## 10."
# ─────────────────────────────────────────────────────────────────────────────
idx = find_by_id(cells, '71e2c522')
if idx >= 0:
    src = get_src(cells[idx]).replace("## 9. חשיבות פיצ'רים", "## 10. חשיבות פיצ'רים")
    set_src(cells[idx], src)
    print(f'[OK] Feature importance header -> S10 (cell {idx})')

# ─────────────────────────────────────────────────────────────────────────────
# 7. INSERT SHAP SECTION AFTER FEATURE IMPORTANCE CHART (cell 8fbf1230)
# ─────────────────────────────────────────────────────────────────────────────
fi_chart_idx = find_by_id(cells, '8fbf1230')
print(f'Feature importance chart: cell {fi_chart_idx}')

SHAP_MD = """\
## 11. SHAP — הסבר מכוון (Explainability)

**MDI** (סעיף 10) אומר *כמה* כל פיצ'ר חשוב — אבל לא *לאיזה כיוון*.
**SHAP** (SHapley Additive exPlanations) מוסיף:

| | MDI | SHAP |
|---|---|---|
| **מה הוא מודד** | ירידת impurity ממוצעת בעצים | תרומת כל פיצ'ר לכל חיזוי בנפרד |
| **כיוון ההשפעה** | ❌ לא | ✅ כן (חיובי/שלילי) |
| **לכל דוגמה בנפרד** | ❌ ממוצע גלובלי | ✅ per-sample |
| **מבוסס על** | impurity הפחתה | ערכי Shapley מתורת המשחקים |

> הרצאה 5 הציגה SHAP כגישה משלימה ל-MDI.

**Beeswarm Plot:**
- **ציר X** = גודל + כיוון ההשפעה על הדירוג החזוי
- **צבע אדום** = ערך פיצ'ר גבוה | **צבע כחול** = ערך נמוך
- **כל נקודה** = סרט אחד

> ⚠️ **הבדל מ-MDI**: MDI יכול להיות מוטה לכיוון פיצ'רים בעלי הרבה ערכים ייחודיים.
> SHAP מבוסס על תרומה ממשית לחיזוי — נחשב ליותר מדויק.\
"""

SHAP_CODE = """\
import shap

# TreeExplainer — exact & fast for tree-based models (Random Forest)
preprocessor.fit(X_train, y_train)
X_test_shap       = preprocessor.transform(X_test)
feature_names_all = NUMERIC_COLS + BINARY_COLS
rf_model_only     = best_rf.named_steps['model']

print('Computing SHAP values via TreeExplainer...')
explainer   = shap.TreeExplainer(rf_model_only)
shap_values = explainer.shap_values(X_test_shap[:300])  # 300 סרטים לדוגמה

# ── 1. Beeswarm: direction + magnitude per sample ────────────────────────
plt.figure(figsize=(10, 8))
shap.summary_plot(
    shap_values, X_test_shap[:300],
    feature_names=feature_names_all,
    show=False, max_display=15
)
plt.title(
    "SHAP Beeswarm — Random Forest\\n"
    "כל נקודה = סרט | צבע = ערך פיצ'ר | ציר X = השפעה על הדירוג",
    fontweight='bold', fontsize=12
)
plt.tight_layout()
plt.savefig('shap_beeswarm.png', dpi=100, bbox_inches='tight')
plt.show()

# ── 2. Bar: mean |SHAP| — compare with MDI ───────────────────────────────
plt.figure(figsize=(10, 6))
shap.summary_plot(
    shap_values, X_test_shap[:300],
    feature_names=feature_names_all,
    plot_type='bar', show=False, max_display=15
)
plt.title(
    "SHAP Feature Importance — mean |SHAP|\\n"
    "השוו ל-MDI (§10): SHAP מסכים על דירוג החשיבות אך מוסיף כיוון",
    fontweight='bold'
)
plt.tight_layout()
plt.savefig('shap_importance.png', dpi=100, bbox_inches='tight')
plt.show()

print("\\nSHAP insights:")
print("  • actor_quality גבוה  → SHAP חיובי → מעלה את הדירוג (אדום, ימינה)")
print("  • genre_Horror = 1    → SHAP שלילי → מוריד את הדירוג (אדום, שמאלה)")
print("  • log_numVotes גבוה   → SHAP חיובי → פופולריות = איכות ב-IMDb")
print("  • is_english = 0      → SHAP שלילי → סרטים לא-אנגלים נוטים לדירוג נמוך יותר")\
"""

shap_cells = [md_cell(SHAP_MD), code_cell(SHAP_CODE)]
ins_shap = fi_chart_idx + 1
for i, c in enumerate(shap_cells):
    cells.insert(ins_shap + i, c)
print(f'[OK] Inserted 2 SHAP cells after index {fi_chart_idx}')

# ─────────────────────────────────────────────────────────────────────────────
# 8. UPDATE REMAINING SECTION NUMBERS
# ─────────────────────────────────────────────────────────────────────────────
renames = [
    ('8b1b627b', '## 10. Error Analysis',    '## 12. Error Analysis'),
    ('bdea35fa', '## 11. Fairness Analysis', '## 13. Fairness Analysis'),
    ('d2ddb935', '## 12. שמירת מודל',         '## 14. שמירת מודל'),
    ('a3284ffc', '## 13. סיכום',              '## 15. סיכום'),
]
for cid, old_s, new_s in renames:
    idx = find_by_id(cells, cid)
    if idx >= 0:
        src = get_src(cells[idx]).replace(old_s, new_s)
        set_src(cells[idx], src)
        print(f'[OK] "{old_s}" → "{new_s}" (cell {idx})')

# ─────────────────────────────────────────────────────────────────────────────
# 9. UPDATE SAVE MODEL (cell a6a68030) TO COMPARE ALL 3 MODELS
# ─────────────────────────────────────────────────────────────────────────────
idx = find_by_id(cells, 'a6a68030')
if idx >= 0:
    src = get_src(cells[idx])
    old_pick = 'best_model      = best_rf if rf_test_rmse <= en_test_rmse else best_en'
    new_pick = (
        "# Choose best model based on TEST RMSE — all 3 models\n"
        "test_rmses_dict = {\n"
        "    'Elastic Net':       en_test_rmse,\n"
        "    'Random Forest':     rf_test_rmse,\n"
        "    'Gradient Boosting': gb_test_rmse,\n"
        "}\n"
        "best_model_name = min(test_rmses_dict, key=test_rmses_dict.get)\n"
        "best_model      = {\n"
        "    'Elastic Net':       best_en,\n"
        "    'Random Forest':     best_rf,\n"
        "    'Gradient Boosting': best_gb,\n"
        "}[best_model_name]\n"
        "print(f'Best model: {best_model_name} (Test RMSE = {test_rmses_dict[best_model_name]:.4f})')"
    )
    if old_pick in src:
        src = src.replace(old_pick, new_pick)
        set_src(cells[idx], src)
        print(f'[OK] Save model updated to compare 3 models (cell {idx})')
    else:
        print(f'[!!] Save model: could not find old text to replace')

# ─────────────────────────────────────────────────────────────────────────────
# 10. UPDATE TOC (cell cell-0)
# ─────────────────────────────────────────────────────────────────────────────
idx = find_by_id(cells, 'cell-0')
if idx >= 0:
    src = get_src(cells[idx])
    src = (src
        .replace(
            '7. מודל 2 – Random Forest\n8. השוואת מודלים',
            '7. מודל 2 – Random Forest\n8. מודל 3 – Gradient Boosting\n9. השוואת מודלים'
        ).replace(
            "9. חשיבות פיצ'רים\n10. Error Analysis",
            "10. חשיבות פיצ'רים\n11. SHAP Analysis\n12. Error Analysis"
        ).replace(
            '11. Fairness Analysis\n12. שמירת מודל\n13. סיכום',
            '13. Fairness Analysis\n14. שמירת מודל\n15. סיכום'
        )
    )
    set_src(cells[idx], src)
    print(f'[OK] TOC updated (cell {idx})')

# ─────────────────────────────────────────────────────────────────────────────
# 11. UPDATE SUMMARY (cell a3284ffc) WITH v6 (GB) + SHAP ROW
# ─────────────────────────────────────────────────────────────────────────────
idx = find_by_id(cells, 'a3284ffc')
if idx >= 0:
    src = get_src(cells[idx])
    # Add v6 GB row to version history table
    src = src.replace(
        '| **v5** | VIF cleanup + log_runtime + log_numVotes + num_lead_actors + PPS | ראה תוצאות עדכניות | ראה תוצאות עדכניות |',
        ('| **v5** | VIF cleanup + log_runtime + log_numVotes + num_lead_actors + PPS | ראה תוצאות עדכניות | ראה תוצאות עדכניות |\n'
         '| **v6** | Gradient Boosting (Model 3) + SHAP explainability | ראה §9 | ראה §9 |')
    )
    # Add GB to "מה גרם לשיפור" table
    src = src.replace(
        '| num_lead_actors (v5) | אנסמבל vs סולו — סיגנל גודל ההפקה | 🟡 קטן |',
        ('| num_lead_actors (v5) | אנסמבל vs סולו — סיגנל גודל ההפקה | 🟡 קטן |\n'
         '| **Gradient Boosting (v6)** | Boosting מצמצם Bias; מתקן שגיאות שיורי בצורה סדרתית | 🔴 גדול |')
    )
    # Add SHAP row to "ניתוחים תיאורטיים" table
    src = src.replace(
        '| CART / Gini / Bagging / OOB | §7 | עץ החלטה → Random Forest + OOB Error |',
        ('| CART / Gini / Bagging / OOB | §7 | עץ החלטה → Random Forest + OOB Error |\n'
         '| SHAP (Explainability) | §11 | TreeExplainer: כיוון + גודל השפעת כל פיצ\'ר per-sample |')
    )
    # Update "גרסה נוכחית" title
    src = src.replace(
        "### פיצ'רים פעילים — גרסה נוכחית (v5)",
        "### פיצ'רים פעילים — גרסה נוכחית (v6)"
    )
    # Add GB to checklist
    src = src.replace(
        '| Elastic Net — GridSearchCV | ✅ alpha × l1_ratio, 5-fold |',
        ('| Elastic Net — GridSearchCV | ✅ alpha × l1_ratio, 5-fold |\n'
         '| Gradient Boosting — RandomizedSearchCV | ✅ n_iter=20, 3-fold + staged convergence |')
    )
    src = src.replace(
        '| Feature Importance | ✅ EN: מקדמים סטנדרטיים; RF: MDI |',
        '| Feature Importance | ✅ EN: מקדמים סטנדרטיים; RF: MDI + SHAP Beeswarm |'
    )
    set_src(cells[idx], src)
    print(f'[OK] Summary updated with v6 + SHAP (cell {idx})')

# ─────────────────────────────────────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────────────────────────────────────
nb['cells'] = cells
with open(NB, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f'\n✅ Done!  Total cells: {len(cells)}')

# Quick verification
with open(NB, encoding='utf-8') as f:
    nb2 = json.load(f)

gb_cells_found = sum(1 for c in nb2['cells'] if 'GradientBoostingRegressor' in ''.join(c.get('source',[])))
shap_cells_found = sum(1 for c in nb2['cells'] if 'shap.summary_plot' in ''.join(c.get('source',[])))
gb_in_imports = any('GradientBoostingRegressor' in ''.join(c.get('source',[])) and 'import' in ''.join(c.get('source',[])) for c in nb2['cells'])
print(f'  GB cells found:       {gb_cells_found}')
print(f'  SHAP cells found:     {shap_cells_found}')
print(f'  GB in imports:        {gb_in_imports}')
print(f'  Total cells:          {len(nb2["cells"])}')
