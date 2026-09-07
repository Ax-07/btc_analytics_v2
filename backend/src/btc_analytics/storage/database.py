"""Construction du moteur PostgreSQL pour la couche infrastructure."""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def create_db_engine(database_url: str) -> Engine:
    """Créer un moteur SQLAlchemy synchrone sans ouvrir de connexion immédiatement."""
    return create_engine(database_url, pool_pre_ping=True)
