"""
Directory of help services (module M5): the list and one service.

Public: anyone may read it, without an account (fictitious services, no
personal data). Booking a trip to a service needs an account, like any booking.
"""

from dataclasses import dataclass

from ..repository import commune_repository, help_service_repository
from ..repository.help_service_repository import HelpService
from ..utils import database
from ..utils.errors import NotFound

SERVICE_NOT_FOUND = "Ce service d'aide n'existe pas."


@dataclass(frozen=True)
class ServiceWithCommune:
    service: HelpService
    commune_name: str


def list_services(language: str) -> list[ServiceWithCommune]:
    with database.session() as session:
        names = {commune.id: commune.name for commune in commune_repository.list_communes(session, served_only=False)}
        return [
            ServiceWithCommune(service, names.get(service.commune_id, ""))
            for service in help_service_repository.list_services(session, language)
        ]


def get_service(service_id: int, language: str) -> ServiceWithCommune:
    with database.session() as session:
        service = help_service_repository.find_by_id(session, service_id, language)
        if service is None:
            raise NotFound(SERVICE_NOT_FOUND)
        commune = commune_repository.find_by_id(session, service.commune_id)
        return ServiceWithCommune(service, commune.name if commune else "")
