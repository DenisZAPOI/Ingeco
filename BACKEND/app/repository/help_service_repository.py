"""
Help services of the directory (module M5 of the cahier des charges, tables
`service_aide` and `service_aide_langue` asked to the DB team in issue #49).

FAKE DATA until the DB team delivers the tables: a fixed list, in memory. The
signatures are those the real repository will keep (the session comes first,
unused for now), so the switch changes nothing above this file.

Every service is fictitious (cahier des charges §5: no real data): invented
names marked "(fictif)", placed at public places of the pilot zone. Their
phone numbers are in the range the ARCEP reserves for fiction (05 36 49 xx xx,
national numbering plan, "Numéros pour œuvres audiovisuelles"): they ring at
nobody's. A health service describes a place to go, never an illness
(cahier des charges §12).

Texts are written in French, and translated into the other languages of the
app where we have a translation (ADR 018), the same way as the job offers.
"""

from dataclasses import dataclass, replace
from datetime import date

from sqlalchemy.orm import Session

# The needs of the directory, in the order of the cahier des charges (§7.5).
# Same values as the ENUM `categorie` asked in issue #49, in English.
CATEGORIES = ("childcare", "housing", "rights", "health", "food", "digital", "paperwork", "equipment")

_CAYENNE, _REMIRE, _MATOURY = 1, 2, 3

# Languages spoken at a service: the codes of the interface (FRONTEND/src/i18n).
_FR, _GCR, _HT, _PT, _EN = "fr", "gcr", "ht", "pt-BR", "en"


@dataclass(frozen=True)
class HelpService:
    id: int
    name: str
    category: str
    description: str
    hours: str
    address: str
    lat: float
    lng: float
    commune_id: int
    # International format; a fictitious number of the ARCEP range.
    phone: str
    wheelchair_accessible: bool
    spoken_languages: tuple[str, ...]
    updated_on: date
    # The language of name, description and hours ("fr" when untranslated).
    language: str = "fr"


@dataclass(frozen=True)
class ServiceText:
    name: str
    description: str
    hours: str


def _phone(number: int) -> str:
    """05 36 49 00 xx, reserved for fiction by the ARCEP."""
    return f"+3353649{number:04d}"


# Texts in French: content, not interface (ADR 013). Short sentences, simple
# words: the people who read them are not all at ease with reading.
_SERVICES = (
    HelpService(
        1,
        "Halte-garderie Les Petits Ibis (fictif)",
        "childcare",
        "Garde d'enfants de 3 mois à 6 ans, à la demi-journée. "
        "Pratique pour aller à un entretien d'embauche ou à une formation. Inscription sur place.",
        "Du lundi au vendredi, 7 h 30 – 17 h 30",
        "Place des Palmistes, Cayenne", 4.9389, -52.3326, _CAYENNE,
        _phone(1), True, (_FR, _GCR, _PT), date(2026, 11, 2),
    ),
    HelpService(
        2,
        "Relais petite enfance de Matoury (fictif)",
        "childcare",
        "On vous aide à trouver une assistante maternelle près de chez vous, "
        "et on vous explique les aides pour payer la garde.",
        "Lundi, mardi et jeudi, 8 h – 12 h",
        "Mairie de Matoury", 4.8470, -52.3290, _MATOURY,
        _phone(2), True, (_FR, _GCR), date(2026, 10, 28),
    ),
    HelpService(
        3,
        "Point info logement (fictif)",
        "housing",
        "Des conseils pour trouver un logement, faire une demande de logement social "
        "ou régler un problème avec votre propriétaire.",
        "Du lundi au vendredi, 8 h – 12 h ; mercredi, 14 h – 17 h",
        "Avenue du Général de Gaulle, Cayenne", 4.9372, -52.3260, _CAYENNE,
        _phone(3), True, (_FR, _GCR, _HT, _PT), date(2026, 11, 5),
    ),
    HelpService(
        4,
        "Association Toit solidaire (fictif)",
        "housing",
        "Pour les jeunes de 18 à 30 ans : aide pour préparer un dossier de location "
        "et pour garder son logement.",
        "Mardi et jeudi, 9 h – 16 h",
        "Mairie de Rémire-Montjoly", 4.9165, -52.2700, _REMIRE,
        _phone(4), False, (_FR, _EN), date(2026, 10, 20),
    ),
    HelpService(
        5,
        "Point d'accès aux droits (fictif)",
        "rights",
        "Des juristes répondent gratuitement à vos questions : travail, famille, logement, "
        "courriers que vous ne comprenez pas.",
        "Lundi, mercredi et vendredi, 8 h 30 – 12 h 30",
        "Place Léopold Héder, Cayenne", 4.9395, -52.3355, _CAYENNE,
        _phone(5), True, (_FR, _GCR, _HT, _PT, _EN), date(2026, 11, 4),
    ),
    HelpService(
        6,
        "Espace droits sociaux de Matoury (fictif)",
        "rights",
        "On vous aide à savoir à quelles aides vous avez droit (RSA, prime d'activité, "
        "aide au logement) et à faire la demande.",
        "Du lundi au vendredi, 8 h – 12 h",
        "Mairie de Matoury", 4.8470, -52.3290, _MATOURY,
        _phone(6), True, (_FR, _GCR, _PT), date(2026, 10, 30),
    ),
    HelpService(
        7,
        "Centre de santé du Bourg (fictif)",
        "health",
        "Consultations chez un médecin généraliste, sans dépassement d'honoraires. "
        "On vous aide aussi à ouvrir vos droits à l'Assurance maladie. Rendez-vous sur place.",
        "Du lundi au samedi, 7 h 30 – 13 h",
        "Avenue des Flamboyants, Cayenne", 4.9310, -52.3190, _CAYENNE,
        _phone(7), True, (_FR, _GCR, _HT, _PT), date(2026, 11, 6),
    ),
    HelpService(
        8,
        "Point écoute jeunes (fictif)",
        "health",
        "Un lieu pour parler de votre santé, de votre moral ou de vos soucis, avec une infirmière "
        "ou un psychologue. Gratuit et confidentiel, avec ou sans rendez-vous.",
        "Mercredi, 13 h – 18 h ; samedi, 9 h – 12 h",
        "Mairie de Rémire-Montjoly", 4.9165, -52.2700, _REMIRE,
        _phone(8), True, (_FR, _GCR, _EN), date(2026, 10, 25),
    ),
    HelpService(
        9,
        "Épicerie solidaire du Collery (fictif)",
        "food",
        "Des produits du quotidien à petit prix. Il faut être envoyé par un travailleur social "
        "ou une association.",
        "Mardi et vendredi, 9 h – 13 h",
        "Centre commercial Collery, Matoury", 4.8840, -52.3170, _MATOURY,
        _phone(9), True, (_FR, _GCR, _PT), date(2026, 11, 3),
    ),
    HelpService(
        10,
        "Distribution alimentaire Main tendue (fictif)",
        "food",
        "Colis alimentaires gratuits, sans rendez-vous. Venez avec un sac.",
        "Mardi et jeudi, 8 h – 11 h",
        "Marché de Cayenne, rue Lalouette", 4.9363, -52.3297, _CAYENNE,
        _phone(10), False, (_FR, _HT, _PT), date(2026, 11, 1),
    ),
    HelpService(
        11,
        "Espace numérique de la médiathèque (fictif)",
        "digital",
        "Ordinateurs et internet gratuits. Un conseiller vous aide à créer une adresse mail "
        "ou à faire une démarche en ligne.",
        "Du mardi au samedi, 9 h – 17 h",
        "Rue Lalouette, Cayenne", 4.9355, -52.3290, _CAYENNE,
        _phone(11), True, (_FR, _GCR, _EN), date(2026, 11, 7),
    ),
    HelpService(
        12,
        "Point numérique de Rémire (fictif)",
        "digital",
        "Ateliers pour apprendre à se servir d'un téléphone ou d'un ordinateur, en petit groupe. "
        "Débutants bienvenus.",
        "Lundi et mercredi, 14 h – 17 h",
        "Mairie de Rémire-Montjoly", 4.9165, -52.2700, _REMIRE,
        _phone(12), True, (_FR, _PT), date(2026, 10, 22),
    ),
    HelpService(
        13,
        "Maison des démarches de Matoury (fictif)",
        "paperwork",
        "Aide pour vos démarches : impôts, retraite, allocations familiales, permis de conduire, "
        "carte grise. Sans rendez-vous le matin.",
        "Du lundi au vendredi, 8 h – 16 h",
        "Mairie de Matoury", 4.8470, -52.3290, _MATOURY,
        _phone(13), True, (_FR, _GCR, _HT, _PT), date(2026, 11, 4),
    ),
    HelpService(
        14,
        "Écrivain public de Cayenne (fictif)",
        "paperwork",
        "Aide pour écrire une lettre, remplir un formulaire ou comprendre un courrier.",
        "Mercredi et vendredi, 9 h – 12 h",
        "Place Léopold Héder, Cayenne", 4.9395, -52.3355, _CAYENNE,
        _phone(14), False, (_FR, _GCR, _HT), date(2026, 10, 29),
    ),
    HelpService(
        15,
        "Ressourcerie Guyane Réemploi (fictif)",
        "equipment",
        "Meubles, électroménager et vêtements d'occasion, à petit prix.",
        "Du mercredi au samedi, 9 h – 17 h",
        "Zone d'activités de Dégrad-des-Cannes, Rémire-Montjoly", 4.8590, -52.2760, _REMIRE,
        _phone(15), True, (_FR, _PT), date(2026, 10, 26),
    ),
    HelpService(
        16,
        "Vestiaire emploi (fictif)",
        "equipment",
        "Une tenue pour un entretien d'embauche ou des chaussures de sécurité, prêtées "
        "ou données gratuitement. Il faut être envoyé par une structure d'accompagnement.",
        "Lundi et jeudi, 9 h – 12 h",
        "Préfecture, rue Fiedmont, Cayenne", 4.9385, -52.3350, _CAYENNE,
        _phone(16), True, (_FR, _GCR, _EN), date(2026, 11, 5),
    ),
)


_TRANSLATIONS: dict[int, dict[str, ServiceText]] = {
    1: {
        "en": ServiceText(
            "Les Petits Ibis day nursery (fictitious)",
            "Childcare for children from 3 months to 6 years old, by the half day. "
            "Handy to go to a job interview or a training course. Sign up on site.",
            "Monday to Friday, 7:30 am – 5:30 pm",
        ),
        "pt-BR": ServiceText(
            "Creche Les Petits Ibis (fictícia)",
            "Cuidado de crianças de 3 meses a 6 anos, por meio período. "
            "Prático para ir a uma entrevista de emprego ou a um curso. Inscrição no local.",
            "De segunda a sexta, 7h30 – 17h30",
        ),
    },
    2: {
        "en": ServiceText(
            "Matoury early childhood centre (fictitious)",
            "We help you find a childminder near your home, "
            "and we explain the financial help to pay for childcare.",
            "Monday, Tuesday and Thursday, 8 am – 12 pm",
        ),
        "pt-BR": ServiceText(
            "Centro da primeira infância de Matoury (fictício)",
            "Ajudamos você a encontrar uma babá credenciada perto de casa "
            "e explicamos as ajudas para pagar o cuidado das crianças.",
            "Segunda, terça e quinta, 8h – 12h",
        ),
    },
    3: {
        "en": ServiceText(
            "Housing information point (fictitious)",
            "Advice to find a home, apply for social housing "
            "or sort out a problem with your landlord.",
            "Monday to Friday, 8 am – 12 pm; Wednesday, 2 pm – 5 pm",
        ),
        "pt-BR": ServiceText(
            "Ponto de informação sobre moradia (fictício)",
            "Conselhos para encontrar uma moradia, pedir uma moradia social "
            "ou resolver um problema com o proprietário.",
            "De segunda a sexta, 8h – 12h; quarta, 14h – 17h",
        ),
    },
    4: {
        "en": ServiceText(
            "Toit solidaire association (fictitious)",
            "For young people aged 18 to 30: help to prepare a rental application "
            "and to keep your home.",
            "Tuesday and Thursday, 9 am – 4 pm",
        ),
        "pt-BR": ServiceText(
            "Associação Toit solidaire (fictícia)",
            "Para jovens de 18 a 30 anos: ajuda para preparar um pedido de aluguel "
            "e para manter a moradia.",
            "Terça e quinta, 9h – 16h",
        ),
    },
    5: {
        "en": ServiceText(
            "Legal advice point (fictitious)",
            "Lawyers answer your questions for free: work, family, housing, "
            "letters you do not understand.",
            "Monday, Wednesday and Friday, 8:30 am – 12:30 pm",
        ),
        "pt-BR": ServiceText(
            "Ponto de acesso aos direitos (fictício)",
            "Juristas respondem gratuitamente às suas perguntas: trabalho, família, moradia, "
            "cartas que você não entende.",
            "Segunda, quarta e sexta, 8h30 – 12h30",
        ),
    },
    6: {
        "en": ServiceText(
            "Matoury social rights centre (fictitious)",
            "We help you find out which benefits you are entitled to (RSA, in-work benefit, "
            "housing benefit) and to apply for them.",
            "Monday to Friday, 8 am – 12 pm",
        ),
        "pt-BR": ServiceText(
            "Espaço de direitos sociais de Matoury (fictício)",
            "Ajudamos você a saber a quais benefícios tem direito (RSA, prêmio de atividade, "
            "auxílio-moradia) e a fazer o pedido.",
            "De segunda a sexta, 8h – 12h",
        ),
    },
    7: {
        "en": ServiceText(
            "Le Bourg health centre (fictitious)",
            "Appointments with a general practitioner, with no extra fees. "
            "We also help you register with the national health insurance. Appointments on site.",
            "Monday to Saturday, 7:30 am – 1 pm",
        ),
        "pt-BR": ServiceText(
            "Centro de saúde do Bourg (fictício)",
            "Consultas com um clínico geral, sem cobrança extra. "
            "Também ajudamos você a abrir seus direitos ao seguro de saúde. Agendamento no local.",
            "De segunda a sábado, 7h30 – 13h",
        ),
    },
    8: {
        "en": ServiceText(
            "Youth listening point (fictitious)",
            "A place to talk about your health, your mood or your worries, with a nurse "
            "or a psychologist. Free and confidential, with or without an appointment.",
            "Wednesday, 1 pm – 6 pm; Saturday, 9 am – 12 pm",
        ),
        "pt-BR": ServiceText(
            "Ponto de escuta para jovens (fictício)",
            "Um lugar para falar da sua saúde, do seu ânimo ou das suas preocupações, com uma "
            "enfermeira ou um psicólogo. Gratuito e confidencial, com ou sem agendamento.",
            "Quarta, 13h – 18h; sábado, 9h – 12h",
        ),
    },
    9: {
        "en": ServiceText(
            "Collery community grocery (fictitious)",
            "Everyday products at low prices. You need to be referred by a social worker "
            "or a charity.",
            "Tuesday and Friday, 9 am – 1 pm",
        ),
        "pt-BR": ServiceText(
            "Mercearia solidária do Collery (fictícia)",
            "Produtos do dia a dia a preço baixo. É preciso ser encaminhado por um assistente "
            "social ou uma associação.",
            "Terça e sexta, 9h – 13h",
        ),
    },
    10: {
        "en": ServiceText(
            "Main tendue food distribution (fictitious)",
            "Free food parcels, no appointment needed. Bring a bag.",
            "Tuesday and Thursday, 8 am – 11 am",
        ),
        "pt-BR": ServiceText(
            "Distribuição de alimentos Main tendue (fictícia)",
            "Cestas de alimentos gratuitas, sem agendamento. Traga uma sacola.",
            "Terça e quinta, 8h – 11h",
        ),
    },
    11: {
        "en": ServiceText(
            "Media library digital space (fictitious)",
            "Free computers and internet. An adviser helps you create an email address "
            "or do a procedure online.",
            "Tuesday to Saturday, 9 am – 5 pm",
        ),
        "pt-BR": ServiceText(
            "Espaço digital da biblioteca (fictício)",
            "Computadores e internet gratuitos. Um orientador ajuda você a criar um e-mail "
            "ou a fazer um procedimento on-line.",
            "De terça a sábado, 9h – 17h",
        ),
    },
    12: {
        "en": ServiceText(
            "Rémire digital point (fictitious)",
            "Workshops to learn how to use a phone or a computer, in small groups. "
            "Beginners welcome.",
            "Monday and Wednesday, 2 pm – 5 pm",
        ),
        "pt-BR": ServiceText(
            "Ponto digital de Rémire (fictício)",
            "Oficinas para aprender a usar um celular ou um computador, em pequenos grupos. "
            "Iniciantes são bem-vindos.",
            "Segunda e quarta, 14h – 17h",
        ),
    },
    13: {
        "en": ServiceText(
            "Matoury paperwork centre (fictitious)",
            "Help with your paperwork: taxes, pension, family benefits, driving licence, "
            "vehicle registration. No appointment needed in the morning.",
            "Monday to Friday, 8 am – 4 pm",
        ),
        "pt-BR": ServiceText(
            "Casa dos procedimentos de Matoury (fictícia)",
            "Ajuda com seus procedimentos: impostos, aposentadoria, auxílios familiares, "
            "carteira de motorista, documento do veículo. Sem agendamento pela manhã.",
            "De segunda a sexta, 8h – 16h",
        ),
    },
    14: {
        "en": ServiceText(
            "Cayenne public letter writer (fictitious)",
            "Help to write a letter, fill in a form or understand a letter you received.",
            "Wednesday and Friday, 9 am – 12 pm",
        ),
        "pt-BR": ServiceText(
            "Escrevente público de Caiena (fictício)",
            "Ajuda para escrever uma carta, preencher um formulário ou entender uma correspondência.",
            "Quarta e sexta, 9h – 12h",
        ),
    },
    15: {
        "en": ServiceText(
            "Guyane Réemploi second-hand shop (fictitious)",
            "Second-hand furniture, household appliances and clothes, at low prices.",
            "Wednesday to Saturday, 9 am – 5 pm",
        ),
        "pt-BR": ServiceText(
            "Brechó Guyane Réemploi (fictício)",
            "Móveis, eletrodomésticos e roupas usados, a preço baixo.",
            "De quarta a sábado, 9h – 17h",
        ),
    },
    16: {
        "en": ServiceText(
            "Job wardrobe (fictitious)",
            "An outfit for a job interview or safety shoes, lent or given for free. "
            "You need to be referred by a support organisation.",
            "Monday and Thursday, 9 am – 12 pm",
        ),
        "pt-BR": ServiceText(
            "Guarda-roupa do emprego (fictício)",
            "Uma roupa para entrevista de emprego ou sapatos de segurança, emprestados "
            "ou doados gratuitamente. É preciso ser encaminhado por uma estrutura de acompanhamento.",
            "Segunda e quinta, 9h – 12h",
        ),
    },
}


def list_services(session: Session, language: str) -> list[HelpService]:
    """Every service, by need, in `language` where translated. Same order in
    every language: the list does not move when the phone changes language."""
    order = {category: index for index, category in enumerate(CATEGORIES)}
    by_need = sorted(_SERVICES, key=lambda service: (order[service.category], service.id))
    return [_in_language(service, language) for service in by_need]


def find_by_id(session: Session, service_id: int, language: str) -> HelpService | None:
    found = next((service for service in _SERVICES if service.id == service_id), None)
    return _in_language(found, language) if found else None


def _in_language(service: HelpService, language: str) -> HelpService:
    """Name, description and hours in the same language, never a mix."""
    text = _TRANSLATIONS.get(service.id, {}).get(language)
    if text is None:
        return service
    return replace(service, name=text.name, description=text.description, hours=text.hours, language=language)
