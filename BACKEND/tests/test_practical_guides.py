"""GET /practical-guides and GET /practical-guides/<id>: the practical guides
"Comment faire ?" (module M5), on fake data. Public routes."""

from app.repository import help_service_repository, practical_guide_repository

MIN_STEPS, MAX_STEPS = 3, 6
OFFICIAL_SITES = ("gouv.fr", "ameli.fr", "monenfant.fr", "francetravail.fr")
FORBIDDEN_WORDS = ("nationalité", "titre de séjour", "sans-papiers", "diagnostic")


def guides_in(client, accept_language="fr"):
    return client.get("/practical-guides", headers={"Accept-Language": accept_language}).get_json()["items"]


def test_a_visitor_reads_the_guides_without_an_account(client):
    response = client.get("/practical-guides")

    assert response.status_code == 200
    guides = response.get_json()["items"]
    assert len(guides) == len(practical_guide_repository.list_guides(None, "fr"))
    assert {"category", "title", "intro", "steps", "toBring", "source", "updatedOn", "language"} <= guides[0].keys()


def test_every_need_of_the_directory_has_a_guide_in_its_order(client):
    categories = [guide["category"] for guide in guides_in(client)]

    assert categories == list(help_service_repository.CATEGORIES)


def test_every_guide_is_short_and_in_steps(client):
    """Simple language (cahier des charges §7.5): a few short steps."""
    for guide in guides_in(client):
        assert MIN_STEPS <= len(guide["steps"]) <= MAX_STEPS, guide["title"]
        assert all(step.strip() for step in guide["steps"])


def test_a_guide_names_an_official_source_or_says_where_to_ask(client):
    """Real procedures: their rules are kept up to date on the official page."""
    for guide in guides_in(client):
        if guide["source"] is None:
            assert any("mairie" in step for step in guide["steps"]), guide["title"]
        else:
            assert guide["source"]["url"].startswith("https://")
            assert any(site in guide["source"]["url"] for site in OFFICIAL_SITES), guide["source"]["url"]


def test_no_guide_speaks_of_nationality_residence_or_diagnosis(client):
    """Cahier des charges §12."""
    for guide in guides_in(client):
        text = " ".join([guide["title"], guide["intro"], *guide["steps"], *guide["toBring"]]).lower()
        assert not any(word in text for word in FORBIDDEN_WORDS), guide["title"]


def test_one_guide_is_read_by_its_id(client):
    first = guides_in(client)[0]

    response = client.get(f"/practical-guides/{first['id']}")

    assert response.status_code == 200
    assert response.get_json() == first


def test_an_unknown_guide_is_not_found(client):
    response = client.get("/practical-guides/9999")

    assert response.status_code == 404
    assert response.get_json()["detail"] == "Cette fiche n'existe pas."


# --- Language of the contents (ADR 018) ----------------------------------------

def test_the_guides_follow_the_language_of_the_phone(client):
    french = {guide["id"]: guide for guide in guides_in(client, "fr")}

    for language in ("en", "pt-BR"):
        for guide in guides_in(client, language):
            original = french[guide["id"]]
            assert guide["language"] == language
            assert guide["title"] != original["title"], (language, guide["title"])
            # Same number of steps and things to bring: a translation, not another guide.
            assert len(guide["steps"]) == len(original["steps"]), (language, guide["title"])
            assert len(guide["toBring"]) == len(original["toBring"]), (language, guide["title"])
            # The official page stays the same; only its name is translated.
            assert (guide["source"] or {}).get("url") == (original["source"] or {}).get("url")


def test_a_language_without_contents_falls_back_to_french(client):
    french = guides_in(client, "fr")

    for language in ("gcr", "ht"):
        guides = guides_in(client, language)
        assert [guide["title"] for guide in guides] == [guide["title"] for guide in french]
        assert {guide["language"] for guide in guides} == {"fr"}
