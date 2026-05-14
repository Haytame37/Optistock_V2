from datetime import datetime, timezone, timedelta

# Fuseau horaire standard pour toute l'application : GMT+1
TIMEZONE_GMT_PLUS_1 = timezone(timedelta(hours=1))

def get_current_time() -> datetime:
    """Retourne l'heure courante au fuseau horaire GMT+1."""
    return datetime.now(TIMEZONE_GMT_PLUS_1)
