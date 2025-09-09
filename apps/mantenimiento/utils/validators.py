from datetime import datetime, timezone
import re


def is_valid_xabcd(codigo: str) -> bool:
    """Valida un código de ubicación XABCD según reglas definidas."""
    return bool(re.fullmatch(r"^\d{1,2}[0-9][A-Z][0-9]{2}$", codigo or ""))


def ensure_future(dt) -> None:
    """Lanza ValueError si la fecha/hora está en el pasado."""
    if dt is None:
        return
    now = datetime.now(timezone.utc)
    if getattr(dt, 'tzinfo', None) is None:
        raise ValueError('La fecha debe incluir zona horaria (UTC).')
    if dt < now:
        raise ValueError('La fecha/hora debe estar en el futuro.')


