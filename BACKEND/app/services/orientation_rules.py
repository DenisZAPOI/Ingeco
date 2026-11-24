"""
Orientation questionnaire and action plan (module M1, cahier des charges §7.1).

Pure rules, without Flask nor database, so that every rule has its test.

The answers are CODES, the ones of migration 017 and issue #50 ('sans_emploi',
'besoin'…): the database stores them as they are, and the front-end shows
their labels in the user's language. A need is written as a need, never as a
diagnosis nor an administrative situation (§12).

The plan is a PROPOSAL computed by simple rules written in advance, the table
of the validated mockup (docs/maquettes/questionnaire-orientation.html). It
never refuses anything to anyone, and a person can always change it (GDPR
art. 22): every plan offers a human contact.
"""

from dataclasses import dataclass
from typing import Literal, get_args

# --- Questions and their answers (codes of migration 017) ----------------------
# In the order of the questionnaire. The DTOs and the generated front types
# use these Literal types: one list of codes for the whole app.
Situation = Literal["sans_emploi", "petits_boulots", "en_emploi", "en_formation", "reprise"]
Project = Literal["travail_vite", "formation", "creer", "ne_sait_pas"]
Experience = Literal[
    "agriculture",
    "peche",
    "artisanat",
    "garde_enfants",
    "aide_personne",
    "menage",
    "batiment",
    "cuisine",
    "vente",
    "benevolat",
    "aucune",
]
Availability = Literal["matin", "apres_midi", "soir", "nuit", "week_end"]
Need = Literal[
    "trajet",
    "vehicule_adapte",
    "garde",
    "logement",
    "demarches",
    "numerique",
    "francais",
    "equipement",
    "aucun",
]
# "Êtes-vous à l'aise en français ?" The languages spoken are not asked: only
# French counts for the plan, and the others hint at an origin (cahier des
# charges §12, audit RGPD R6).
FrenchLevel = Literal["oui", "un_peu", "non"]
DigitalEquipment = Literal["smartphone", "ordinateur", "internet_maison", "email", "rien"]
StepCode = Literal[
    "offres",
    "formation",
    "creer",
    "conseiller",
    "trajet",
    "garde",
    "logement",
    "demarches",
    "numerique",
    "francais",
    "equipement",
    "francais_auto",
    "numerique_auto",
    "entretien",
]

SITUATIONS: tuple[str, ...] = get_args(Situation)
PROJECTS: tuple[str, ...] = get_args(Project)
EXPERIENCES: tuple[str, ...] = get_args(Experience)
AVAILABILITIES: tuple[str, ...] = get_args(Availability)
NEEDS: tuple[str, ...] = get_args(Need)
FRENCH_LEVELS: tuple[str, ...] = get_args(FrenchLevel)
EQUIPMENT: tuple[str, ...] = get_args(DigitalEquipment)
STEP_CODES: tuple[str, ...] = get_args(StepCode)

# "Nothing of all that": ticked alone, never with another answer of its question.
NO_EXPERIENCE = "aucune"
NO_NEED = "aucun"
NO_EQUIPMENT = "rien"

# Codes of the questions in reponse_questionnaire.code_question.
Q_SITUATION = "situation"
Q_PROJECT = "projet"
Q_EXPERIENCES = "experiences"
Q_AVAILABILITY = "disponibilites"
Q_NEEDS = "besoins"
Q_FRENCH = "francais"
Q_EQUIPMENT = "equipement_numerique"
# The free text of the experiences is stored as this answer of Q_EXPERIENCES:
# the primary key needs an answer code, and the text has no code of its own.
FREE_EXPERIENCE = "autre"
EXPERIENCE_TEXT_MAX_LENGTH = 500

ALONE_ONLY = "« {} » ne peut pas être coché avec une autre réponse."

# --- Steps of the plan (etape_plan.code_etape) ------------------------------------
MIN_STEPS = 3
MAX_STEPS = 5

STEP_OFFERS = "offres"
STEP_TRAINING = "formation"
STEP_CREATE = "creer"
STEP_ADVISER = "conseiller"
STEP_RIDE = "trajet"
STEP_FRENCH_LESSONS = "francais_auto"
STEP_INTERNET_ACCESS = "numerique_auto"
STEP_INTERVIEW = "entretien"

# The first step, from the project.
_PROJECT_STEPS = {
    "travail_vite": STEP_OFFERS,
    "formation": STEP_TRAINING,
    "creer": STEP_CREATE,
    "ne_sait_pas": STEP_ADVISER,
}
# Needs that lead to a ride; the others each lead to their own step, in this order.
_RIDE_NEEDS = ("trajet", "vehicule_adapte")
_NEEDS_WITH_A_STEP = ("garde", "logement", "demarches", "numerique", "francais", "equipement")
# Not at ease in French: French lessons are proposed.
_FRENCH_LESSONS_LEVELS = ("un_peu", "non")
_CONNECTED_DEVICES = ("smartphone", "ordinateur")
# Useful to anyone, never a decision about the person: they fill a plan up to 3 steps.
# The offers come last: the questionnaire starts from « Je cherche un travail »,
# and without them a skipped questionnaire would get only 2 steps (gap of the
# mockup's table).
_FILLERS = (STEP_INTERVIEW, STEP_ADVISER, STEP_OFFERS)


@dataclass(frozen=True)
class Answers:
    """One filling of the questionnaire. Every question may be skipped."""

    situation: str | None = None
    project: str | None = None
    experiences: tuple[str, ...] = ()
    experience_text: str | None = None
    availability: tuple[str, ...] = ()
    needs: tuple[str, ...] = ()
    french: str | None = None
    digital_equipment: tuple[str, ...] = ()


def check_alone(chosen: list[str], alone: str) -> list[str]:
    """`alone` ("nothing of all that") is never ticked with another answer.
    Duplicates are dropped, the order is kept."""
    unique = list(dict.fromkeys(chosen))
    if alone in unique and len(unique) > 1:
        raise ValueError(ALONE_ONLY.format(alone))
    return unique


def build_plan(answers: Answers) -> list[str]:
    """The codes of the 3 to 5 steps, in order (table of the validated mockup)."""
    steps: list[str] = []

    first = _first_step(answers)
    if first:
        steps.append(first)

    if any(need in answers.needs for need in _RIDE_NEEDS):
        steps.append(STEP_RIDE)
    steps.extend(need for need in _NEEDS_WITH_A_STEP if need in answers.needs)

    if _needs_french_lessons(answers):
        steps.append(STEP_FRENCH_LESSONS)
    if _needs_internet_access(answers):
        steps.append(STEP_INTERNET_ACCESS)

    for filler in _FILLERS:
        if len(steps) >= MIN_STEPS:
            break
        if filler not in steps:
            steps.append(filler)
    return steps[:MAX_STEPS]


def _first_step(answers: Answers) -> str | None:
    """From the project; without one, the job offers for someone out of work."""
    if answers.project is not None:
        return _PROJECT_STEPS.get(answers.project)
    if answers.situation == "sans_emploi":
        return STEP_OFFERS
    return None


def _needs_french_lessons(answers: Answers) -> bool:
    """Not at ease in French: French lessons, even unasked."""
    already_asked = "francais" in answers.needs
    return not already_asked and answers.french in _FRENCH_LESSONS_LEVELS


def _needs_internet_access(answers: Answers) -> bool:
    """Neither a phone with internet nor a computer: access to internet, even unasked."""
    already_asked = "numerique" in answers.needs
    has_connected_device = any(device in answers.digital_equipment for device in _CONNECTED_DEVICES)
    return not already_asked and bool(answers.digital_equipment) and not has_connected_device


def to_rows(answers: Answers) -> list[tuple[str, str, str | None]]:
    """(question, answer, text) rows of reponse_questionnaire, one per ticked answer."""
    rows: list[tuple[str, str, str | None]] = []
    if answers.situation:
        rows.append((Q_SITUATION, answers.situation, None))
    if answers.project:
        rows.append((Q_PROJECT, answers.project, None))
    rows += [(Q_EXPERIENCES, code, None) for code in answers.experiences]
    if answers.experience_text:
        rows.append((Q_EXPERIENCES, FREE_EXPERIENCE, answers.experience_text))
    rows += [(Q_AVAILABILITY, code, None) for code in answers.availability]
    rows += [(Q_NEEDS, code, None) for code in answers.needs]
    if answers.french:
        rows.append((Q_FRENCH, answers.french, None))
    rows += [(Q_EQUIPMENT, code, None) for code in answers.digital_equipment]
    return rows


def from_rows(rows: list[tuple[str, str, str | None]]) -> Answers:
    """The answers back from their rows, each list in the order of the questionnaire."""
    by_question: dict[str, list[str]] = {}
    text = None
    for question, answer, answer_text in rows:
        if question == Q_EXPERIENCES and answer == FREE_EXPERIENCE:
            text = answer_text
        else:
            by_question.setdefault(question, []).append(answer)

    def ordered(question: str, choices: tuple[str, ...]) -> tuple[str, ...]:
        chosen = by_question.get(question, [])
        return tuple(code for code in choices if code in chosen)

    def single(question: str) -> str | None:
        chosen = by_question.get(question)
        return chosen[0] if chosen else None

    return Answers(
        situation=single(Q_SITUATION),
        project=single(Q_PROJECT),
        experiences=ordered(Q_EXPERIENCES, EXPERIENCES),
        experience_text=text,
        availability=ordered(Q_AVAILABILITY, AVAILABILITIES),
        needs=ordered(Q_NEEDS, NEEDS),
        french=single(Q_FRENCH),
        digital_equipment=ordered(Q_EQUIPMENT, EQUIPMENT),
    )
