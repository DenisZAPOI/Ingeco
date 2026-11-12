"""
Practical guides "Comment faire ?" (module M5 of the cahier des charges, table
`fiche_pratique` asked to the DB team in issue #49).

FAKE DATA until the DB team delivers the table: a fixed list, in memory, with
the signatures the real repository will keep (session first, unused for now).

Unlike the help services, these guides describe real procedures. They stay
general (no amount, no deadline) and name their official source, where the
rules are kept up to date; the client proofreads them (cahier des charges
§15). Official addresses checked on 11/11/2026. No guide asks for nor speaks
of nationality or residence status (§12).

Texts are written in French, and translated where we have a translation
(ADR 018): title, introduction, steps and "to bring" always in one language.
"""

from dataclasses import dataclass, replace
from datetime import date

from sqlalchemy.orm import Session

from .help_service_repository import CATEGORIES


@dataclass(frozen=True)
class PracticalGuide:
    id: int
    category: str
    title: str
    intro: str
    steps: tuple[str, ...]
    # What to take along; empty when nothing special is needed.
    to_bring: tuple[str, ...]
    # The official page that keeps the rules up to date; None when there is
    # no reliable national page (then a step names the local place to ask).
    source_name: str | None
    source_url: str | None
    updated_on: date
    # The language of the texts ("fr" when untranslated).
    language: str = "fr"


@dataclass(frozen=True)
class GuideText:
    title: str
    intro: str
    steps: tuple[str, ...]
    to_bring: tuple[str, ...]
    source_name: str | None


# Texts in French: content, not interface (ADR 013). One short sentence per
# step, simple words: they are also read aloud by the phone.
_GUIDES = (
    PracticalGuide(
        1,
        "childcare",
        "Faire garder son enfant pendant un entretien",
        "Vous avez un entretien ou une formation, et personne pour garder votre enfant ? "
        "Voici comment trouver une solution.",
        (
            "Demandez à la crèche ou à la halte-garderie la plus proche si elle accueille des enfants "
            "pour quelques heures.",
            "Cherchez une assistante maternelle près de chez vous sur le site monenfant.fr, "
            "ou demandez la liste à votre mairie.",
            "Parlez-en à votre conseiller (France Travail, mission locale) : une aide pour payer la garde "
            "existe parfois.",
            "Réservez la garde dès que vous connaissez la date de l'entretien.",
        ),
        ("Le carnet de santé de l'enfant", "Une pièce d'identité"),
        "monenfant.fr (Caisse d'allocations familiales)",
        "https://monenfant.fr/",
        date(2026, 11, 11),
    ),
    PracticalGuide(
        2,
        "housing",
        "Demander un logement social",
        "Un logement social a un loyer plus bas. Il faut en faire la demande.",
        (
            "Faites la demande en ligne sur le site officiel, ou au guichet d'un bailleur social "
            "ou de votre mairie.",
            "Notez bien votre numéro de demande : il sert pour toutes vos démarches.",
            "Ajoutez les documents demandés.",
            "Renouvelez votre demande chaque année tant que vous n'avez pas de logement, "
            "sinon elle est supprimée.",
            "Si votre situation change (un enfant, un travail), mettez votre demande à jour.",
        ),
        ("Une pièce d'identité", "Votre dernier avis d'impôt", "Vos derniers justificatifs de revenus"),
        "Demande de logement social en ligne (site officiel)",
        "https://www.demande-logement-social.gouv.fr/",
        date(2026, 11, 11),
    ),
    PracticalGuide(
        3,
        "rights",
        "Savoir à quelles aides vous avez droit",
        "En quelques minutes, un simulateur officiel vous dit à quelles aides vous pouvez avoir droit.",
        (
            "Ouvrez le site Mes droits sociaux, ou 1jeune1solution si vous avez moins de 30 ans.",
            "Répondez aux questions sur votre famille, votre logement et vos revenus.",
            "Regardez la liste des aides proposées : le simulateur dit où faire chaque demande.",
            "Si vous avez besoin d'aide pour remplir, allez dans un point d'accès aux droits "
            "ou une maison des démarches.",
        ),
        ("Vos revenus des derniers mois", "Le montant de votre loyer"),
        "Mes droits sociaux (site officiel)",
        "https://www.mesdroitssociaux.gouv.fr/",
        date(2026, 11, 11),
    ),
    PracticalGuide(
        4,
        "health",
        "Ouvrir vos droits à l'Assurance maladie",
        "Avec l'Assurance maladie, vos soins sont remboursés. Si vos droits ne sont pas encore ouverts, "
        "voici les étapes.",
        (
            "Créez votre compte sur le site ameli, ou allez à un accueil de la caisse de sécurité sociale.",
            "Envoyez les documents demandés.",
            "Si vos revenus sont faibles, demandez aussi la Complémentaire santé solidaire : "
            "elle paie le reste de vos soins.",
            "Une fois vos droits ouverts, demandez votre carte Vitale.",
        ),
        ("Une pièce d'identité", "Un RIB", "Un justificatif de domicile"),
        "ameli.fr (Assurance maladie)",
        "https://www.ameli.fr/",
        date(2026, 11, 11),
    ),
    PracticalGuide(
        5,
        "food",
        "Obtenir une aide alimentaire",
        "Si vous n'avez pas assez pour manger, des colis, des repas ou des épiceries solidaires existent "
        "près de chez vous.",
        (
            "Allez au CCAS (centre communal d'action sociale) de votre mairie : on vous dira où trouver "
            "de l'aide.",
            "Certaines distributions sont sans rendez-vous : regardez les services « Aide alimentaire » "
            "de cette application.",
            "Pour une épicerie solidaire, il faut souvent être envoyé par un travailleur social.",
            "N'attendez pas d'avoir tous vos papiers pour demander de l'aide.",
        ),
        ("Un sac",),
        None,
        None,
        date(2026, 11, 11),
    ),
    PracticalGuide(
        6,
        "digital",
        "Créer une adresse mail",
        "Une adresse mail sert pour beaucoup de démarches, et pour répondre aux offres d'emploi.",
        (
            "Choisissez un service de messagerie gratuit, sur votre téléphone ou sur un ordinateur.",
            "Choisissez une adresse simple, avec votre prénom et votre nom.",
            "Choisissez un mot de passe que vous seul connaissez, et gardez-le dans un endroit sûr.",
            "Envoyez-vous un premier message pour vérifier que tout marche.",
            "Si vous bloquez, un espace numérique peut vous aider gratuitement.",
        ),
        ("Votre téléphone",),
        "Solidarité numérique (site de l'État)",
        "https://lesbases.anct.gouv.fr/bases/solidarite-numerique",
        date(2026, 11, 11),
    ),
    PracticalGuide(
        7,
        "paperwork",
        "S'inscrire à France Travail",
        "S'inscrire à France Travail vous donne un conseiller, et l'accès aux offres, aux formations "
        "et à certaines aides.",
        (
            "Inscrivez-vous en ligne sur le site de France Travail.",
            "Répondez aux questions sur votre situation et sur le métier que vous cherchez.",
            "Prenez le rendez-vous proposé à la fin de l'inscription.",
            "Le jour du rendez-vous, venez avec vos documents. Pensez à réserver votre trajet "
            "dans cette application.",
            "Si vous ne pouvez pas vous inscrire en ligne, allez dans une agence France Travail "
            "ou une maison des démarches.",
        ),
        ("Une pièce d'identité", "Votre carte Vitale", "Un CV si vous en avez un"),
        "France Travail : l'inscription en ligne",
        "https://www.francetravail.fr/candidat/vos-droits-et-demarches/vos-demarches-aupres-de-pole-emp/"
        "linscription-et-le-rendez-vous-e.html",
        date(2026, 11, 11),
    ),
    PracticalGuide(
        8,
        "equipment",
        "Trouver une tenue pour un entretien",
        "Pour un entretien, une tenue propre et simple suffit. Si vous n'en avez pas, des solutions "
        "gratuites ou à petit prix existent.",
        (
            "Demandez à votre conseiller s'il connaît un vestiaire solidaire : une tenue peut vous être "
            "prêtée ou donnée.",
            "Allez voir dans une ressourcerie : vêtements et chaussures d'occasion, à petit prix.",
            "Pour des chaussures de sécurité ou du matériel de travail, cherchez une aide sur le site "
            "Mes aides France Travail.",
            "Essayez votre tenue la veille de l'entretien.",
        ),
        (),
        "Mes aides France Travail",
        "https://mes-aides.francetravail.fr/",
        date(2026, 11, 11),
    ),
)


_TRANSLATIONS: dict[int, dict[str, GuideText]] = {
    1: {
        "en": GuideText(
            "Getting your child looked after during an interview",
            "You have an interview or a training course, and nobody to look after your child? "
            "Here is how to find a solution.",
            (
                "Ask the nearest nursery or day nursery if it takes children for a few hours.",
                "Look for a childminder near your home on the monenfant.fr website, "
                "or ask your town hall for the list.",
                "Talk to your adviser (France Travail, mission locale): there is sometimes help to pay "
                "for childcare.",
                "Book the childcare as soon as you know the date of the interview.",
            ),
            ("Your child's health record", "An identity document"),
            "monenfant.fr (family allowance fund)",
        ),
        "pt-BR": GuideText(
            "Deixar seu filho com alguém durante uma entrevista",
            "Você tem uma entrevista ou um curso, e ninguém para cuidar do seu filho? "
            "Veja como encontrar uma solução.",
            (
                "Pergunte à creche mais próxima se ela recebe crianças por algumas horas.",
                "Procure uma babá credenciada perto de casa no site monenfant.fr, "
                "ou peça a lista na prefeitura.",
                "Fale com seu orientador (France Travail, mission locale): às vezes existe uma ajuda "
                "para pagar o cuidado.",
                "Reserve o cuidado assim que souber a data da entrevista.",
            ),
            ("A caderneta de saúde da criança", "Um documento de identidade"),
            "monenfant.fr (caixa de auxílios familiares)",
        ),
    },
    2: {
        "en": GuideText(
            "Applying for social housing",
            "Social housing has a lower rent. You need to apply for it.",
            (
                "Apply online on the official website, or at the desk of a social landlord or your town hall.",
                "Write down your application number: you need it for everything.",
                "Add the documents you are asked for.",
                "Renew your application every year as long as you have no home, otherwise it is deleted.",
                "If your situation changes (a child, a job), update your application.",
            ),
            ("An identity document", "Your last tax notice", "Your latest proofs of income"),
            "Social housing application online (official website)",
        ),
        "pt-BR": GuideText(
            "Pedir uma moradia social",
            "Uma moradia social tem um aluguel mais baixo. É preciso fazer o pedido.",
            (
                "Faça o pedido on-line no site oficial, ou no balcão de um locador social ou da prefeitura.",
                "Anote bem o número do seu pedido: ele serve para todos os procedimentos.",
                "Adicione os documentos pedidos.",
                "Renove o pedido todo ano enquanto não tiver moradia, senão ele é apagado.",
                "Se sua situação mudar (um filho, um trabalho), atualize o pedido.",
            ),
            ("Um documento de identidade", "Sua última declaração de imposto", "Seus últimos comprovantes de renda"),
            "Pedido de moradia social on-line (site oficial)",
        ),
    },
    3: {
        "en": GuideText(
            "Finding out which benefits you are entitled to",
            "In a few minutes, an official simulator tells you which benefits you may be entitled to.",
            (
                "Open the Mes droits sociaux website, or 1jeune1solution if you are under 30.",
                "Answer the questions about your family, your home and your income.",
                "Look at the list of benefits: the simulator says where to apply for each one.",
                "If you need help to fill it in, go to a legal advice point or a paperwork centre.",
            ),
            ("Your income of the last months", "The amount of your rent"),
            "Mes droits sociaux (official website)",
        ),
        "pt-BR": GuideText(
            "Saber a quais benefícios você tem direito",
            "Em poucos minutos, um simulador oficial diz a quais benefícios você pode ter direito.",
            (
                "Abra o site Mes droits sociaux, ou 1jeune1solution se você tiver menos de 30 anos.",
                "Responda às perguntas sobre sua família, sua moradia e sua renda.",
                "Veja a lista de benefícios: o simulador diz onde fazer cada pedido.",
                "Se precisar de ajuda para preencher, vá a um ponto de acesso aos direitos "
                "ou a uma casa dos procedimentos.",
            ),
            ("Sua renda dos últimos meses", "O valor do seu aluguel"),
            "Mes droits sociaux (site oficial)",
        ),
    },
    4: {
        "en": GuideText(
            "Registering with the national health insurance",
            "With the national health insurance, your care is reimbursed. If you are not registered yet, "
            "here are the steps.",
            (
                "Create your account on the ameli website, or go to a social security office.",
                "Send the documents you are asked for.",
                "If your income is low, also apply for the Complémentaire santé solidaire: "
                "it pays the rest of your care.",
                "Once registered, apply for your carte Vitale (health card).",
            ),
            ("An identity document", "Your bank details (RIB)", "A proof of address"),
            "ameli.fr (national health insurance)",
        ),
        "pt-BR": GuideText(
            "Abrir seus direitos ao seguro de saúde",
            "Com o seguro de saúde (Assurance maladie), seus cuidados são reembolsados. "
            "Se seus direitos ainda não estão abertos, veja as etapas.",
            (
                "Crie sua conta no site ameli, ou vá a um atendimento da caixa de seguridade social.",
                "Envie os documentos pedidos.",
                "Se sua renda for baixa, peça também a Complémentaire santé solidaire: "
                "ela paga o resto dos seus cuidados.",
                "Depois de abrir seus direitos, peça sua carte Vitale (cartão de saúde).",
            ),
            ("Um documento de identidade", "Seus dados bancários (RIB)", "Um comprovante de endereço"),
            "ameli.fr (seguro de saúde)",
        ),
    },
    5: {
        "en": GuideText(
            "Getting food aid",
            "If you do not have enough to eat, food parcels, meals or community groceries exist near you.",
            (
                "Go to the CCAS (social action centre) of your town hall: they will tell you where to find help.",
                "Some distributions need no appointment: look at the \"Food aid\" services of this app.",
                "For a community grocery, you often need to be referred by a social worker.",
                "Do not wait to have all your papers to ask for help.",
            ),
            ("A bag",),
            None,
        ),
        "pt-BR": GuideText(
            "Conseguir ajuda alimentar",
            "Se você não tem o suficiente para comer, existem cestas, refeições ou mercearias solidárias "
            "perto de você.",
            (
                "Vá ao CCAS (centro de ação social) da sua prefeitura: lá dirão onde encontrar ajuda.",
                "Algumas distribuições são sem agendamento: veja os serviços \"Ajuda alimentar\" deste aplicativo.",
                "Para uma mercearia solidária, muitas vezes é preciso ser encaminhado por um assistente social.",
                "Não espere ter todos os seus documentos para pedir ajuda.",
            ),
            ("Uma sacola",),
            None,
        ),
    },
    6: {
        "en": GuideText(
            "Creating an email address",
            "An email address is needed for many procedures, and to answer job offers.",
            (
                "Choose a free email service, on your phone or on a computer.",
                "Choose a simple address, with your first name and your last name.",
                "Choose a password that only you know, and keep it in a safe place.",
                "Send yourself a first message to check that everything works.",
                "If you are stuck, a digital space can help you for free.",
            ),
            ("Your phone",),
            "Solidarité numérique (State website)",
        ),
        "pt-BR": GuideText(
            "Criar um endereço de e-mail",
            "Um e-mail serve para muitos procedimentos e para responder às vagas de emprego.",
            (
                "Escolha um serviço de e-mail gratuito, no seu celular ou em um computador.",
                "Escolha um endereço simples, com seu nome e seu sobrenome.",
                "Escolha uma senha que só você conhece e guarde-a em um lugar seguro.",
                "Envie uma primeira mensagem para você mesmo para verificar se tudo funciona.",
                "Se tiver dificuldade, um espaço digital pode ajudar você gratuitamente.",
            ),
            ("Seu celular",),
            "Solidarité numérique (site do Estado)",
        ),
    },
    7: {
        "en": GuideText(
            "Registering with France Travail",
            "Registering with France Travail (the job centre) gives you an adviser, and access to job offers, "
            "training and some benefits.",
            (
                "Register online on the France Travail website.",
                "Answer the questions about your situation and the job you are looking for.",
                "Take the appointment offered at the end of the registration.",
                "On the day of the appointment, bring your documents. Remember to book your trip in this app.",
                "If you cannot register online, go to a France Travail agency or a paperwork centre.",
            ),
            ("An identity document", "Your carte Vitale (health card)", "A CV if you have one"),
            "France Travail: online registration",
        ),
        "pt-BR": GuideText(
            "Inscrever-se no France Travail",
            "Inscrever-se no France Travail (agência de emprego) dá a você um orientador e acesso às vagas, "
            "aos cursos e a alguns benefícios.",
            (
                "Inscreva-se on-line no site do France Travail.",
                "Responda às perguntas sobre sua situação e a profissão que você procura.",
                "Marque o atendimento proposto no fim da inscrição.",
                "No dia do atendimento, leve seus documentos. Lembre-se de reservar sua viagem neste aplicativo.",
                "Se não puder se inscrever on-line, vá a uma agência do France Travail ou a uma casa dos "
                "procedimentos.",
            ),
            ("Um documento de identidade", "Sua carte Vitale (cartão de saúde)", "Um currículo se você tiver"),
            "France Travail: inscrição on-line",
        ),
    },
    8: {
        "en": GuideText(
            "Finding an outfit for an interview",
            "For an interview, clean and simple clothes are enough. If you have none, free or cheap "
            "solutions exist.",
            (
                "Ask your adviser if they know a community wardrobe: an outfit can be lent or given to you.",
                "Have a look in a second-hand shop: used clothes and shoes, at low prices.",
                "For safety shoes or work equipment, look for help on the Mes aides France Travail website.",
                "Try on your outfit the day before the interview.",
            ),
            (),
            "Mes aides France Travail",
        ),
        "pt-BR": GuideText(
            "Encontrar uma roupa para uma entrevista",
            "Para uma entrevista, uma roupa limpa e simples basta. Se você não tiver, existem soluções "
            "gratuitas ou a preço baixo.",
            (
                "Pergunte ao seu orientador se ele conhece um guarda-roupa solidário: uma roupa pode ser "
                "emprestada ou doada.",
                "Procure em um brechó: roupas e sapatos usados, a preço baixo.",
                "Para sapatos de segurança ou material de trabalho, procure uma ajuda no site "
                "Mes aides France Travail.",
                "Experimente sua roupa na véspera da entrevista.",
            ),
            (),
            "Mes aides France Travail",
        ),
    },
}


def list_guides(session: Session, language: str) -> list[PracticalGuide]:
    """Every guide, in the order of the needs (cahier des charges §7.5)."""
    order = {category: index for index, category in enumerate(CATEGORIES)}
    by_need = sorted(_GUIDES, key=lambda guide: (order[guide.category], guide.id))
    return [_in_language(guide, language) for guide in by_need]


def find_by_id(session: Session, guide_id: int, language: str) -> PracticalGuide | None:
    found = next((guide for guide in _GUIDES if guide.id == guide_id), None)
    return _in_language(found, language) if found else None


def _in_language(guide: PracticalGuide, language: str) -> PracticalGuide:
    """All the texts of a guide in the same language, never a mix."""
    text = _TRANSLATIONS.get(guide.id, {}).get(language)
    if text is None:
        return guide
    return replace(
        guide,
        title=text.title,
        intro=text.intro,
        steps=text.steps,
        to_bring=text.to_bring,
        source_name=text.source_name,
        language=language,
    )
