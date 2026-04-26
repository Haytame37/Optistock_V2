"""
utils/product_conditions.py
═══════════════════════════════════════════════════════════════════════════════
Dictionnaire centralisant les conditions de conservation des produits.
Inclus : Cible MIN/MAX, Marges de tolérance et Temps de résistance avant altération.
Les temps sont exprimés en heures pour faciliter les calculs avec les historiques.
═══════════════════════════════════════════════════════════════════════════════
"""

# Temps de résistance exprimés en heures. Longue durée = valeur élevée arbitraire (ex: 1000h)
PRODUCT_CONDITIONS = {
    "Tomates": {
        "temperature": {
            "min": 10.0,
            "max": 15.0,
            "marge_bas": -2.0,  # Seuil critique < 8.0
            "marge_haut": 3.0,  # Seuil critique > 18.0
            "temps_resistance_bas_min_h": 2.0,
            "temps_resistance_bas_h": 4.0,
            "temps_resistance_haut_min_h": 12.0,
            "temps_resistance_haut_h": 24.0
        },
        "humidite": {
            "min": 85.0,
            "max": 90.0,
            "marge_bas": -5.0,
            "marge_haut": 5.0,
            "temps_resistance_bas_min_h": 72.0,
            "temps_resistance_bas_h": 120.0,
            "temps_resistance_haut_min_h": 48.0,
            "temps_resistance_haut_h": 72.0
        }
    },
    "Produits Laitiers": {
        "temperature": {
            "min": 2.0,
            "max": 6.0,
            "marge_bas": -1.0,
            "marge_haut": 2.0,
            "temps_resistance_bas_min_h": 1.0,
            "temps_resistance_bas_h": 2.0,
            "temps_resistance_haut_min_h": 0.5,
            "temps_resistance_haut_h": 2.0
        },
        "humidite": {
            "min": 65.0,
            "max": 80.0,
            "marge_bas": -5.0,
            "marge_haut": 5.0,
            "temps_resistance_bas_min_h": 336.0, # 2 semaines
            "temps_resistance_bas_h": 504.0,
            "temps_resistance_haut_min_h": 120.0, # 5 jours
            "temps_resistance_haut_h": 168.0
        }
    },
    "Parapharmacie": {
        "temperature": {
            "min": 15.0,
            "max": 25.0,
            "marge_bas": -10.0,
            "marge_haut": 2.0,
            "temps_resistance_bas_min_h": 48.0,
            "temps_resistance_bas_h": 72.0,
            "temps_resistance_haut_min_h": 24.0,
            "temps_resistance_haut_h": 48.0
        },
        "humidite": {
            "min": 40.0,
            "max": 60.0,
            "marge_bas": -10.0,
            "marge_haut": 5.0,
            "temps_resistance_bas_min_h": 500.0,
            "temps_resistance_bas_h": 1000.0,
            "temps_resistance_haut_min_h": 120.0,
            "temps_resistance_haut_h": 240.0
        }
    },
    "Composants Électroniques": {
        "temperature": {
            "min": 15.0,
            "max": 30.0,
            "marge_bas": -10.0,
            "marge_haut": 10.0,
            "temps_resistance_bas_min_h": 500.0,
            "temps_resistance_bas_h": 1000.0,
            "temps_resistance_haut_min_h": 1000.0,
            "temps_resistance_haut_h": 2000.0
        },
        "humidite": {
            "min": 1.0,
            "max": 10.0,
            "marge_bas": -0.0,
            "marge_haut": 0.0,
            "temps_resistance_bas_min_h": 500.0,
            "temps_resistance_bas_h": 1000.0,
            "temps_resistance_haut_min_h": 12.0,
            "temps_resistance_haut_h": 24.0
        }
    }
}
