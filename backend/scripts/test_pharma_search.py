import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.iot_filter import get_compliant_warehouses

def test_pharma_search():
    product = "Produits Pharmaceutiques"
    results = get_compliant_warehouses(product)
    
    print(f"\n--- Résultats pour {product} ---")
    if not results:
        print("Aucun entrepôt trouvé (Filtrage strict réussi).")
    else:
        for r in results:
            print(f"ID: {r['id']} | Nom: {r['nom']} | Temp Moy: {r['avg_temp']}°C | Hum Moy: {r['avg_hum']}%")
            if r['id'] == "ENT001":
                print("⚠️  ATTENTION : Hub 1 est toujours présent.")

if __name__ == "__main__":
    test_pharma_search()
