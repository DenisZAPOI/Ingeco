"""
Job offers (module M2 of the cahier des charges, table `offre_emploi` asked
to the DB team in issue #48).

FAKE DATA until the DB team delivers the table: a fixed list, in memory. The
signatures are those the real repository will keep (the session comes first,
unused for now), so the switch changes nothing above this file.

Every offer is fictitious (cahier des charges §5: no real data): invented
employers, placed at public places of the pilot zone, never at someone's home.
Offers stay in the three served communes until the table `commune` lists the
others (issue #52): "Comment y aller ?" then works on every offer.

Texts are written in French, and translated into the other languages of the
app where we have a translation (ADR 018). An offer is read in one language;
a text missing in it is given in French, and the offer says which language
it is in. In base: a table of translations (issue #48), joined the same way.
"""

from dataclasses import dataclass, replace
from datetime import datetime, timezone

from sqlalchemy.orm import Session

# Values of the filters (issue #48: type_contrat, plage_horaire).
CONTRACT_TYPES = ("permanent", "fixed_term", "temp", "apprenticeship", "seasonal")
SCHEDULES = ("day", "shifted", "night")

_CAYENNE, _REMIRE, _MATOURY = 1, 2, 3


@dataclass(frozen=True)
class JobOffer:
    id: int
    title: str
    employer: str
    description: str
    contract_type: str
    schedule: str
    part_time: bool
    beginner_welcome: bool
    no_diploma_required: bool
    address: str
    lat: float
    lng: float
    commune_id: int
    published_at: datetime
    active: bool = True
    # The language of title, employer and description ("fr" when untranslated).
    language: str = "fr"


@dataclass(frozen=True)
class OfferText:
    title: str
    employer: str
    description: str


def _published(day: int) -> datetime:
    return datetime(2026, 11, day, 12, 0, tzinfo=timezone.utc)


# Texts in French: content, not interface (ADR 013). Short sentences, simple
# words: the people who read them are not all at ease with reading.
_OFFERS = (
    JobOffer(
        1,
        "Employé(e) de rayon",
        "Supermarché du Collery (fictif)",
        "Vous mettez les produits en rayon et vous aidez les clients à trouver ce qu'ils cherchent. "
        "Pas besoin d'expérience : on vous forme sur place les deux premières semaines.",
        "fixed_term", "day", False, True, True,
        "Centre commercial Collery, Matoury", 4.8840, -52.3170, _MATOURY, _published(9),
    ),
    JobOffer(
        2,
        "Agent(e) d'entretien",
        "Propreté Guyane Services (fictif)",
        "Nettoyage de bureaux tôt le matin, avant l'arrivée des salariés. "
        "Horaires : 5 h – 8 h, du lundi au vendredi. Le matériel est fourni.",
        "permanent", "shifted", True, True, True,
        "Préfecture, rue Fiedmont, Cayenne", 4.9385, -52.3350, _CAYENNE, _published(8),
    ),
    JobOffer(
        3,
        "Manutentionnaire au port",
        "Logistique du Dégrad (fictif)",
        "Chargement et déchargement des conteneurs. Travail physique, chaussures de sécurité fournies. "
        "Débutants acceptés.",
        "temp", "day", False, True, True,
        "Zone d'activités de Dégrad-des-Cannes, Rémire-Montjoly", 4.8590, -52.2760, _REMIRE, _published(8),
    ),
    JobOffer(
        4,
        "Agent(e) de piste",
        "Assistance Aéroport Cayenne (fictif)",
        "Vous aidez au chargement des bagages et au guidage des avions. "
        "Travail en équipe, de jour comme de nuit selon le planning.",
        "fixed_term", "night", False, True, False,
        "Aéroport Félix Éboué, Matoury", 4.8197, -52.3604, _MATOURY, _published(7),
    ),
    JobOffer(
        5,
        "Vendeur(se) au marché",
        "Les Fruits de Cayenne (fictif)",
        "Vente de fruits et légumes sur l'étal, le mercredi, le vendredi et le samedi matin. "
        "Vous accueillez les clients et vous rendez la monnaie.",
        "seasonal", "day", True, True, True,
        "Marché de Cayenne, rue Lalouette", 4.9363, -52.3297, _CAYENNE, _published(7),
    ),
    JobOffer(
        6,
        "Aide-soignant(e) de nuit",
        "Centre de soins des Flamboyants (fictif)",
        "Vous aidez les patients pour la toilette, les repas et le coucher. "
        "Diplôme d'aide-soignant demandé.",
        "permanent", "night", False, False, False,
        "Hôpital de Cayenne (centre hospitalier), avenue des Flamboyants", 4.9310, -52.3190, _CAYENNE, _published(6),
    ),
    JobOffer(
        7,
        "Apprenti(e) cuisinier(ère)",
        "Restaurant Les Palmistes (fictif)",
        "Formation en alternance : deux jours au centre de formation, trois jours en cuisine. "
        "Vous apprenez à préparer les entrées et les desserts.",
        "apprenticeship", "shifted", False, True, True,
        "Place des Palmistes, Cayenne", 4.9389, -52.3326, _CAYENNE, _published(6),
    ),
    JobOffer(
        8,
        "Agent(e) d'accueil",
        "Mairie de Rémire-Montjoly (offre fictive)",
        "Vous accueillez le public, vous répondez au téléphone et vous orientez les personnes. "
        "Être à l'aise à l'oral ; parler créole ou portugais est un plus.",
        "fixed_term", "day", False, False, True,
        "Mairie de Rémire-Montjoly", 4.9165, -52.2700, _REMIRE, _published(5),
    ),
    JobOffer(
        9,
        "Plongeur(se) en restauration",
        "Snack de la Plage (fictif)",
        "Vaisselle et rangement de la cuisine, le soir et le week-end. Aucune expérience demandée.",
        "seasonal", "shifted", True, True, True,
        "Plage de Montjoly, Rémire-Montjoly", 4.9230, -52.2790, _REMIRE, _published(5),
    ),
    JobOffer(
        10,
        "Chauffeur(se)-livreur(se)",
        "Livraisons Express Matoury (fictif)",
        "Livraison de colis chez les clients de Matoury et de Cayenne. Permis B demandé, véhicule fourni.",
        "permanent", "day", False, False, True,
        "Mairie de Matoury", 4.8470, -52.3310, _MATOURY, _published(4),
    ),
    JobOffer(
        11,
        "Agent(e) de sécurité",
        "Sécurité Guyane Plus (fictif)",
        "Surveillance d'un centre commercial, rondes et accueil. Carte professionnelle demandée.",
        "fixed_term", "night", False, False, False,
        "Centre commercial Collery, Matoury", 4.8840, -52.3170, _MATOURY, _published(3),
    ),
    JobOffer(
        12,
        "Aide à domicile",
        "Association Bien Chez Soi (fictif)",
        "Vous aidez des personnes âgées pour les courses, le ménage et les repas, à Cayenne. "
        "Débutants acceptés, une formation est prévue.",
        "permanent", "day", True, True, True,
        "Gare routière, Cayenne", 4.9354, -52.3277, _CAYENNE, _published(3),
    ),
    JobOffer(
        13,
        "Caissier(ère)",
        "Supermarché du Collery (fictif)",
        "Vous encaissez les achats et vous accueillez les clients. Horaires en roulement, le samedi inclus.",
        "fixed_term", "shifted", True, True, True,
        "Centre commercial Collery, Matoury", 4.8840, -52.3170, _MATOURY, _published(2),
    ),
    JobOffer(
        14,
        "Ouvrier(ère) du bâtiment",
        "Bâtir Rémire (fictif)",
        "Aide sur les chantiers : préparation, port de matériaux, nettoyage. "
        "Chaussures et casque fournis. Débutants acceptés.",
        "temp", "day", False, True, True,
        "Zone d'activités de Dégrad-des-Cannes, Rémire-Montjoly", 4.8590, -52.2760, _REMIRE, _published(2),
    ),
    # Kept to show that an offer taken offline disappears from the list.
    JobOffer(
        15,
        "Serveur(se) en salle",
        "Restaurant Les Palmistes (fictif)",
        "Offre pourvue.",
        "seasonal", "shifted", False, True, True,
        "Place des Palmistes, Cayenne", 4.9389, -52.3326, _CAYENNE, _published(1),
        active=False,
    ),
)


# Translations of the texts above, by offer then by language. Written by the
# developers, to be proofread like the interface (docs/decisions.md).
_TRANSLATIONS: dict[int, dict[str, OfferText]] = {
    1: {
        "en": OfferText(
            "Shelf stacker",
            "Collery Supermarket (fictitious)",
            "You put products on the shelves and help customers find what they are looking for. "
            "No experience needed: you are trained on site for the first two weeks.",
        ),
        "pt-BR": OfferText(
            "Repositor(a)",
            "Supermercado do Collery (fictício)",
            "Você coloca os produtos nas prateleiras e ajuda os clientes a encontrar o que procuram. "
            "Não precisa de experiência: você é treinado(a) no local nas duas primeiras semanas.",
        ),
    },
    2: {
        "en": OfferText(
            "Cleaner",
            "Propreté Guyane Services (fictitious)",
            "Cleaning offices early in the morning, before the staff arrive. "
            "Hours: 5 am – 8 am, Monday to Friday. Equipment provided.",
        ),
        "pt-BR": OfferText(
            "Auxiliar de limpeza",
            "Propreté Guyane Services (fictício)",
            "Limpeza de escritórios de manhã cedo, antes da chegada dos funcionários. "
            "Horário: 5h – 8h, de segunda a sexta. O material é fornecido.",
        ),
    },
    3: {
        "en": OfferText(
            "Dock worker",
            "Logistique du Dégrad (fictitious)",
            "Loading and unloading containers. Physical work, safety shoes provided. Beginners welcome.",
        ),
        "pt-BR": OfferText(
            "Carregador(a) no porto",
            "Logistique du Dégrad (fictício)",
            "Carga e descarga de contêineres. Trabalho físico, sapatos de segurança fornecidos. "
            "Aceita iniciantes.",
        ),
    },
    4: {
        "en": OfferText(
            "Ramp agent",
            "Assistance Aéroport Cayenne (fictitious)",
            "You help load luggage and guide planes. Teamwork, day or night depending on the schedule.",
        ),
        "pt-BR": OfferText(
            "Agente de pista",
            "Assistance Aéroport Cayenne (fictício)",
            "Você ajuda a carregar as bagagens e a guiar os aviões. "
            "Trabalho em equipe, de dia ou de noite conforme a escala.",
        ),
    },
    5: {
        "en": OfferText(
            "Market seller",
            "Les Fruits de Cayenne (fictitious)",
            "Selling fruit and vegetables at the stall, on Wednesday, Friday and Saturday mornings. "
            "You welcome customers and give change.",
        ),
        "pt-BR": OfferText(
            "Vendedor(a) na feira",
            "Les Fruits de Cayenne (fictício)",
            "Venda de frutas e legumes na barraca, quarta, sexta e sábado de manhã. "
            "Você atende os clientes e dá o troco.",
        ),
    },
    6: {
        "en": OfferText(
            "Night care assistant",
            "Flamboyants care centre (fictitious)",
            "You help patients with washing, meals and going to bed. A care assistant diploma is required.",
        ),
        "pt-BR": OfferText(
            "Auxiliar de enfermagem noturno(a)",
            "Centro de cuidados dos Flamboyants (fictício)",
            "Você ajuda os pacientes no banho, nas refeições e na hora de dormir. "
            "É exigido o diploma de auxiliar de enfermagem.",
        ),
    },
    7: {
        "en": OfferText(
            "Apprentice cook",
            "Les Palmistes restaurant (fictitious)",
            "Work-study training: two days at the training centre, three days in the kitchen. "
            "You learn to prepare starters and desserts.",
        ),
        "pt-BR": OfferText(
            "Aprendiz de cozinheiro(a)",
            "Restaurante Les Palmistes (fictício)",
            "Formação em alternância: dois dias no centro de formação, três dias na cozinha. "
            "Você aprende a preparar entradas e sobremesas.",
        ),
    },
    8: {
        "en": OfferText(
            "Receptionist",
            "Rémire-Montjoly town hall (fictitious offer)",
            "You welcome the public, answer the phone and direct people. "
            "Being at ease speaking is needed; speaking Creole or Portuguese is a plus.",
        ),
        "pt-BR": OfferText(
            "Recepcionista",
            "Prefeitura de Rémire-Montjoly (vaga fictícia)",
            "Você recebe o público, atende o telefone e orienta as pessoas. "
            "Ter facilidade para falar; falar crioulo ou português é um diferencial.",
        ),
    },
    9: {
        "en": OfferText(
            "Dishwasher",
            "Snack de la Plage (fictitious)",
            "Washing up and tidying the kitchen, in the evening and at weekends. No experience needed.",
        ),
        "pt-BR": OfferText(
            "Lavador(a) de louça",
            "Snack de la Plage (fictício)",
            "Lavar a louça e arrumar a cozinha, à noite e nos fins de semana. Não precisa de experiência.",
        ),
    },
    10: {
        "en": OfferText(
            "Delivery driver",
            "Livraisons Express Matoury (fictitious)",
            "Delivering parcels to customers in Matoury and Cayenne. "
            "Driving licence (B) required, vehicle provided.",
        ),
        "pt-BR": OfferText(
            "Motorista entregador(a)",
            "Livraisons Express Matoury (fictício)",
            "Entrega de encomendas aos clientes de Matoury e de Caiena. "
            "Carteira de motorista B exigida, veículo fornecido.",
        ),
    },
    11: {
        "en": OfferText(
            "Security guard",
            "Sécurité Guyane Plus (fictitious)",
            "Guarding a shopping centre, patrols and welcoming visitors. Professional card required.",
        ),
        "pt-BR": OfferText(
            "Vigilante",
            "Sécurité Guyane Plus (fictício)",
            "Vigilância de um centro comercial, rondas e recepção. Carteira profissional exigida.",
        ),
    },
    12: {
        "en": OfferText(
            "Home help",
            "Bien Chez Soi association (fictitious)",
            "You help elderly people with shopping, housework and meals, in Cayenne. "
            "Beginners welcome, training is planned.",
        ),
        "pt-BR": OfferText(
            "Cuidador(a) a domicílio",
            "Associação Bien Chez Soi (fictício)",
            "Você ajuda pessoas idosas nas compras, na limpeza e nas refeições, em Caiena. "
            "Aceita iniciantes, há uma formação prevista.",
        ),
    },
    13: {
        "en": OfferText(
            "Cashier",
            "Collery Supermarket (fictitious)",
            "You ring up purchases and welcome customers. Rotating hours, Saturdays included.",
        ),
        "pt-BR": OfferText(
            "Operador(a) de caixa",
            "Supermercado do Collery (fictício)",
            "Você registra as compras e atende os clientes. Horários em rodízio, sábado incluído.",
        ),
    },
    14: {
        "en": OfferText(
            "Construction worker",
            "Bâtir Rémire (fictitious)",
            "Helping on building sites: preparation, carrying materials, cleaning. "
            "Shoes and helmet provided. Beginners welcome.",
        ),
        "pt-BR": OfferText(
            "Ajudante de obras",
            "Bâtir Rémire (fictício)",
            "Ajuda nos canteiros de obras: preparação, transporte de materiais, limpeza. "
            "Sapatos e capacete fornecidos. Aceita iniciantes.",
        ),
    },
}


def list_active(session: Session, language: str) -> list[JobOffer]:
    """The offers online, the most recent first, in `language` where translated."""
    online = sorted((offer for offer in _OFFERS if offer.active), key=lambda offer: offer.published_at, reverse=True)
    return [_in_language(offer, language) for offer in online]


def find_active(session: Session, offer_id: int, language: str) -> JobOffer | None:
    found = next((offer for offer in _OFFERS if offer.id == offer_id and offer.active), None)
    return _in_language(found, language) if found else None


def _in_language(offer: JobOffer, language: str) -> JobOffer:
    """All three texts in the same language: never a title in English over a
    description in French."""
    text = _TRANSLATIONS.get(offer.id, {}).get(language)
    if text is None:
        return offer
    return replace(offer, title=text.title, employer=text.employer, description=text.description, language=language)
