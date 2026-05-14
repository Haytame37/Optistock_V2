import sys
import os
sys.path.append(os.getcwd())
from core.maintenance import reorder_user_ids

print("--- Début du réordonnancement des IDs ---")
success = reorder_user_ids()
if success:
    print("✅ Réordonnancement terminé avec succès.")
else:
    print("❌ Échec du réordonnancement.")
