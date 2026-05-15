
// --- SERVICE THINGSBOARD DYNAMIQUE POUR OPTISTOCK ---

const THINGSBOARD_HOST = "demo.thingsboard.io";

/**
 * Récupère les dernières données de télémétrie depuis ThingsBoard
 * @param accessToken Le token spécifique de l'appareil (fourni par l'admin)
 */
export async function getLiveTelemetry(accessToken: string) {
  if (!accessToken) {
    console.error("Aucun Token ThingsBoard fourni pour cet entrepôt.");
    return null;
  }

  try {
    const response = await fetch(`https://${THINGSBOARD_HOST}/api/v1/${accessToken}/telemetry`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`Erreur ThingsBoard: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Erreur lors de la récupération de la télémétrie:", error);
    return null;
  }
}
