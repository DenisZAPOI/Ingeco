"""Orientation questionnaire and action plan (module M1, cahier des charges §7.1).

The rules of the plan first (table of the validated mockup), then the routes:
anyone may get a plan without an account, only a rider's plan is kept.
"""

import pytest
from sqlalchemy import select

from app.models import AnswerRow, PlanStepRow, QuestionnaireRow
from app.services.orientation_rules import (
    MAX_STEPS,
    MIN_STEPS,
    STEP_CODES,
    Answers,
    build_plan,
    from_rows,
    to_rows,
)
from tests.helpers import in_session
from tests.test_auth import DRIVER_PHONE, csrf_headers, login

# Jordan, 22, no driving licence (scenario A of the cahier des charges, §8).
JORDAN = {
    "situation": "sans_emploi",
    "project": "travail_vite",
    "experiences": ["agriculture", "benevolat"],
    "experienceText": "J'aide mon oncle à l'abattis le week-end",
    "availability": ["matin", "apres_midi"],
    "needs": ["trajet"],
    "french": "oui",
    "digitalEquipment": ["smartphone"],
}


def save(client, answers=None):
    return client.post("/orientation/questionnaires", json=answers or JORDAN, headers=csrf_headers(client))


def mark(client, position, done=True):
    return client.put(f"/orientation/plan/steps/{position}", json={"done": done}, headers=csrf_headers(client))


# --- Rules of the plan -----------------------------------------------------------


def test_jordans_plan_offers_jobs_then_a_ride_then_a_human():
    plan = build_plan(Answers(situation="sans_emploi", project="travail_vite", needs=("trajet",), french="oui"))

    assert plan == ["offres", "trajet", "entretien"]


@pytest.mark.parametrize(
    ("project", "first"),
    [("travail_vite", "offres"), ("formation", "formation"), ("creer", "creer"), ("ne_sait_pas", "conseiller")],
)
def test_the_project_chooses_the_first_step(project, first):
    assert build_plan(Answers(project=project))[0] == first


def test_without_a_project_someone_without_a_job_is_shown_the_offers():
    assert build_plan(Answers(situation="sans_emploi"))[0] == "offres"


def test_every_need_leads_to_its_own_step_in_a_fixed_order():
    plan = build_plan(Answers(needs=("logement", "garde")))

    assert plan[:2] == ["garde", "logement"]


def test_an_adapted_vehicle_is_a_ride_step_once():
    assert build_plan(Answers(needs=("trajet", "vehicule_adapte"))).count("trajet") == 1


def test_someone_not_at_ease_in_french_is_offered_french_lessons():
    assert "francais_auto" in build_plan(Answers(french="non"))
    assert "francais_auto" in build_plan(Answers(french="un_peu"))
    assert "francais_auto" not in build_plan(Answers(french="oui"))
    # Question skipped: nothing is assumed.
    assert "francais_auto" not in build_plan(Answers())
    # Asked for already: not twice.
    assert "francais_auto" not in build_plan(Answers(french="non", needs=("francais",)))


def test_the_languages_spoken_are_not_accepted(client):
    # They hint at an origin (cahier des charges §12, audit RGPD R6).
    response = client.post("/orientation/plan", json=JORDAN | {"languages": ["ht"]})

    assert response.status_code == 400


def test_someone_without_a_connected_device_is_offered_internet_access():
    assert "numerique_auto" in build_plan(Answers(digital_equipment=("rien",)))
    assert "numerique_auto" not in build_plan(Answers(digital_equipment=("smartphone",)))
    # Question skipped: nothing is assumed.
    assert "numerique_auto" not in build_plan(Answers())


def test_a_skipped_questionnaire_still_gives_three_steps_with_a_human_contact():
    assert build_plan(Answers()) == ["entretien", "conseiller", "offres"]
    assert build_plan(Answers(project="travail_vite")) == ["offres", "entretien", "conseiller"]


def test_a_plan_never_has_more_than_five_steps():
    many = Answers(project="travail_vite", needs=("trajet", "garde", "logement", "demarches", "numerique", "francais"))

    assert len(build_plan(many)) == MAX_STEPS


def test_every_step_produced_is_a_known_code():
    plan = build_plan(Answers(project="creer", needs=("equipement",), french="non", digital_equipment=("email",)))

    assert set(plan) <= set(STEP_CODES)


def test_answers_survive_their_rows():
    answers = Answers(
        situation="reprise",
        project="formation",
        experiences=("peche", "cuisine"),
        experience_text="Je répare les scooters",
        availability=("soir",),
        needs=("garde",),
        french="un_peu",
        digital_equipment=("smartphone", "email"),
    )

    assert from_rows(to_rows(answers)) == answers


# --- Without an account: nothing kept ------------------------------------------------


def test_a_visitor_gets_a_plan_and_nothing_is_kept(client):
    response = client.post("/orientation/plan", json=JORDAN)

    assert response.status_code == 200
    steps = response.get_json()["steps"]
    assert [step["code"] for step in steps] == ["offres", "trajet", "entretien"]
    assert [step["position"] for step in steps] == [1, 2, 3]
    assert all(step["doneAt"] is None for step in steps)
    assert in_session(lambda session: session.scalars(select(QuestionnaireRow)).all()) == []


def test_every_question_may_be_skipped(client):
    response = client.post("/orientation/plan", json={})

    assert response.status_code == 200
    assert len(response.get_json()["steps"]) == MIN_STEPS


def test_nothing_of_all_that_is_never_ticked_with_another_answer(client):
    response = client.post("/orientation/plan", json={"needs": ["aucun", "trajet"]})

    assert response.status_code == 400


def test_an_unknown_answer_is_refused(client):
    assert client.post("/orientation/plan", json={"situation": "autre_chose"}).status_code == 400


def test_a_forbidden_field_is_refused(client):
    """Cahier des charges §12: no nationality, residence status, health…"""
    assert client.post("/orientation/plan", json={**JORDAN, "nationality": "x"}).status_code == 400


# --- A rider's plan, kept -------------------------------------------------------------


def test_a_rider_keeps_answers_and_plan(client):
    login(client)

    response = save(client)

    assert response.status_code == 201
    plan = response.get_json()
    assert [step["code"] for step in plan["steps"]] == ["offres", "trajet", "entretien"]
    assert plan["answers"] == JORDAN
    texts = in_session(lambda session: session.scalars(select(AnswerRow.text).where(AnswerRow.text.is_not(None))).all())
    assert texts == [JORDAN["experienceText"]]


def test_a_rider_finds_the_plan_again(client):
    login(client)
    assert client.get("/orientation/plan").status_code == 404
    save(client)

    response = client.get("/orientation/plan")

    assert response.status_code == 200
    assert response.get_json()["answers"]["needs"] == ["trajet"]


def test_answering_again_keeps_the_earlier_filling_but_the_last_one_counts(client):
    login(client)
    save(client)
    save(client, {"project": "formation"})

    plan = client.get("/orientation/plan").get_json()

    assert plan["steps"][0]["code"] == "formation"
    assert len(in_session(lambda session: session.scalars(select(QuestionnaireRow)).all())) == 2


def test_a_rider_ticks_a_step_and_ticking_again_keeps_its_date(client):
    login(client)
    save(client)

    first = mark(client, 2).get_json()["steps"][1]["doneAt"]
    again = mark(client, 2).get_json()["steps"][1]["doneAt"]

    assert first is not None and again == first
    assert mark(client, 2, done=False).get_json()["steps"][1]["doneAt"] is None


def test_a_step_outside_the_plan_is_not_found(client):
    login(client)
    save(client)

    assert mark(client, MAX_STEPS).status_code == 404


def test_ticking_without_a_plan_is_not_found(client):
    login(client)

    assert mark(client, 1).status_code == 404


def test_the_plan_never_names_an_offer_nor_a_service(client):
    """The person chooses in the lists herself: the step only leads there."""
    login(client)
    save(client)

    rows = in_session(lambda session: session.scalars(select(PlanStepRow)).all())
    assert all(row.job_offer_id is None and row.help_service_id is None for row in rows)


def test_a_visitor_cannot_keep_a_plan(client):
    assert client.post("/orientation/questionnaires", json=JORDAN).status_code == 401
    assert client.get("/orientation/plan").status_code == 401


def test_a_driver_cannot_keep_a_plan(client):
    login(client, DRIVER_PHONE)

    assert save(client).status_code == 403
    assert client.get("/orientation/plan").status_code == 403
