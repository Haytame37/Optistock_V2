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
        "type_stockage_logistique": "froid",
        "temperature": {
            "min": 7.0,
            "max": 10.0,
            "marge_bas": -1.5,  # Seuil critique < 5.5
            "marge_haut": 1.5,  # Seuil critique > 11.5
            "temps_resistance_bas_min_h": 2.0,
            "temps_resistance_haut_min_h": 12.0
        },
        "humidite": {
            "min": 90.0,
            "max": 95.0,
            "marge_bas": -1,
            "marge_haut": 1,
            "temps_resistance_bas_min_h": 72.0,
            "temps_resistance_haut_min_h": 48.0
        }
    },
    "Produits Laitiers": {
        "type_stockage_logistique": "froid",
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
        "type_stockage_logistique": "sec",
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
    "Produits Pharmaceutiques": {
        "type_stockage_logistique": "pharma",
        "temperature": {
            "min": 15.0,
            "max": 25.0,
            "marge_bas": 0.0,
            "marge_haut": 0.0,
            "temps_resistance_bas_min_h": 0.5,
            "temps_resistance_haut_min_h": 0.5
        },
        "humidite": {
            "min": 35.0,
            "max": 50.0,
            "marge_bas": 0.0,
            "marge_haut": 0.0,
            "temps_resistance_bas_min_h": 1.0,
            "temps_resistance_haut_min_h": 1.0
        }
    },
    "Composants Électroniques": {
        "type_stockage_logistique": "sec",
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
    },
    "Materiaux de Construction": {
        "type_stockage_logistique": "mixte",
        "ignore_environment": True,
        "temperature": {
            "min": -100.0,
            "max": 200.0,
            "marge_bas": 0.0,
            "marge_haut": 0.0,
            "temps_resistance_bas_min_h": 1000.0,
            "temps_resistance_haut_min_h": 1000.0
        },
        "humidite": {
            "min": 0.0,
            "max": 100.0,
            "marge_bas": 0.0,
            "marge_haut": 0.0,
            "temps_resistance_bas_min_h": 1000.0,
            "temps_resistance_haut_min_h": 1000.0
        }
    }
}


def get_product_storage_type(product_name: str) -> str:
    """
    Retourne le type de stockage logistique associe a un produit.
    Fallback : 'mixte' si le produit n'est pas mappe explicitement.
    """
    product = PRODUCT_CONDITIONS.get(product_name, {})
    return product.get("type_stockage_logistique", "mixte")


def ignores_environment_conditions(product_name: str) -> bool:
    """
    Indique si un produit ne doit pas etre filtre ni penalise
    par la temperature ou l'humidite.
    """
    product = PRODUCT_CONDITIONS.get(product_name, {})
    return bool(product.get("ignore_environment", False))
