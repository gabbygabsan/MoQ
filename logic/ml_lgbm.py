import lightgbm as lgb
import numpy as np

# Dummy-Trainingsdaten für Kühlleistung
X_train = np.array([
    [1, 10000, 2500, 1.2, 6.0, 8.0],
    [2, 18000, 3800, 1.1, 8.0, 6.0],
    [4, 25000, 4800, 1.4, 10.0, 5.0],
    [1, 12000, 2600, 1.3, 6.0, 7.0],
    [3, 21000, 4000, 1.2, 9.0, 4.0]
])
y_train = np.array([3.0, 5.2, 7.8, 3.3, 6.1])  # Kühlleistung in kW

# LightGBM Regressor trainieren
model = lgb.LGBMRegressor()
model.fit(X_train, y_train)

def predict_kuehlleistung_lgbm(features: dict) -> float:
    """
    Nimmt ein Feature-Dictionary und gibt die vorhergesagte Kühlleistung in kW zurück.
    """
    try:
        X_input = np.array([[
            features["kavitaeten"],
            features["volume_mm3"],
            features["surface_area_mm2"],
            features["aspect_ratio"],
            features["kanal_durchmesser"],
            features["kanal_abstand"]
        ]])
        prediction = model.predict(X_input)
        return round(float(prediction[0]), 2)
    except Exception as e:
        print("Fehler bei LGBM-Vorhersage:", e)
        return 0.0
