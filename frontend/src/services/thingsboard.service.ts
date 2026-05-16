
// --- SERVICE THINGSBOARD DYNAMIQUE POUR OPTISTOCK ---

const THINGSBOARD_HOST = "demo.thingsboard.io";

/**
 * Récupère les dernières données de télémétrie depuis ThingsBoard
 * @param accessToken Le token spécifique de l'appareil (fourni par l'admin)
 */
/**
 * Récupère les dernières données de télémétrie depuis le PROXY local
 * @param warehouseId L'ID de l'entrepôt pour lequel on veut les données
 */
export async function getLiveTelemetry(warehouseId: string) {
  try {
    // On appelle notre propre Backend qui fait le relai avec ThingsBoard
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/iot/live/${warehouseId}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`Erreur Proxy Backend: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Erreur lors de la récupération de la télémétrie via Proxy:", error);
    return null;
  }
}
