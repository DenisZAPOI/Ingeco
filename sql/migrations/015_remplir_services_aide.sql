-- 015 : services d'aide fictifs, langues parlées et traductions
-- 12/11/2026, Kurtys TSHIBOLA (équipe BD), issue #49
-- Retour arrière : DELETE FROM service_aide_traduction; DELETE FROM service_aide_langue; DELETE FROM service_aide;
--
-- Contenus FICTIFS du démonstrateur (cahier des charges §5 : aucune donnée
-- réelle) : employeurs, services et numéros inventés, lieux publics de la
-- zone du pilote, jamais un domicile. Repris tels quels du jeu factice
-- écrit par les développeurs au sprint 1 (BACKEND/app/repository/), avec
-- les mêmes identifiants : le passage de la mémoire à la base ne change
-- rien à l'écran. Traductions anglaise et portugaise (ADR 018) ; les
-- créoles seront ajoutés par des locuteurs, l'API retombe en attendant sur
-- le français.
--
-- Données de contenu, pas de test : elles ne contiennent aucun compte et
-- restent en place quand demo-data.sql remet la démo à zéro. Une offre ou
-- un service se retire en passant active / actif à FALSE.

INSERT INTO service_aide (id_service, nom, categorie, description, horaires, adresse, lat, lng, id_commune, telephone, accessible_pmr, mis_a_jour_le, actif) VALUES
(1, 'Halte-garderie Les Petits Ibis (fictif)', 'garde', 'Garde d''enfants de 3 mois à 6 ans, à la demi-journée. Pratique pour aller à un entretien d''embauche ou à une formation. Inscription sur place.', 'Du lundi au vendredi, 7 h 30 – 17 h 30', 'Place des Palmistes, Cayenne', 4.938900, -52.332600, 1, '+33536490001', TRUE, '2026-11-02', TRUE),
(2, 'Relais petite enfance de Matoury (fictif)', 'garde', 'On vous aide à trouver une assistante maternelle près de chez vous, et on vous explique les aides pour payer la garde.', 'Lundi, mardi et jeudi, 8 h – 12 h', 'Mairie de Matoury', 4.847000, -52.329000, 3, '+33536490002', TRUE, '2026-10-28', TRUE),
(3, 'Point info logement (fictif)', 'logement', 'Des conseils pour trouver un logement, faire une demande de logement social ou régler un problème avec votre propriétaire.', 'Du lundi au vendredi, 8 h – 12 h ; mercredi, 14 h – 17 h', 'Avenue du Général de Gaulle, Cayenne', 4.937200, -52.326000, 1, '+33536490003', TRUE, '2026-11-05', TRUE),
(4, 'Association Toit solidaire (fictif)', 'logement', 'Pour les jeunes de 18 à 30 ans : aide pour préparer un dossier de location et pour garder son logement.', 'Mardi et jeudi, 9 h – 16 h', 'Mairie de Rémire-Montjoly', 4.916500, -52.270000, 2, '+33536490004', FALSE, '2026-10-20', TRUE),
(5, 'Point d''accès aux droits (fictif)', 'droits', 'Des juristes répondent gratuitement à vos questions : travail, famille, logement, courriers que vous ne comprenez pas.', 'Lundi, mercredi et vendredi, 8 h 30 – 12 h 30', 'Place Léopold Héder, Cayenne', 4.939500, -52.335500, 1, '+33536490005', TRUE, '2026-11-04', TRUE),
(6, 'Espace droits sociaux de Matoury (fictif)', 'droits', 'On vous aide à savoir à quelles aides vous avez droit (RSA, prime d''activité, aide au logement) et à faire la demande.', 'Du lundi au vendredi, 8 h – 12 h', 'Mairie de Matoury', 4.847000, -52.329000, 3, '+33536490006', TRUE, '2026-10-30', TRUE),
(7, 'Centre de santé du Bourg (fictif)', 'sante', 'Consultations chez un médecin généraliste, sans dépassement d''honoraires. On vous aide aussi à ouvrir vos droits à l''Assurance maladie. Rendez-vous sur place.', 'Du lundi au samedi, 7 h 30 – 13 h', 'Avenue des Flamboyants, Cayenne', 4.931000, -52.319000, 1, '+33536490007', TRUE, '2026-11-06', TRUE),
(8, 'Point écoute jeunes (fictif)', 'sante', 'Un lieu pour parler de votre santé, de votre moral ou de vos soucis, avec une infirmière ou un psychologue. Gratuit et confidentiel, avec ou sans rendez-vous.', 'Mercredi, 13 h – 18 h ; samedi, 9 h – 12 h', 'Mairie de Rémire-Montjoly', 4.916500, -52.270000, 2, '+33536490008', TRUE, '2026-10-25', TRUE),
(9, 'Épicerie solidaire du Collery (fictif)', 'aide_alimentaire', 'Des produits du quotidien à petit prix. Il faut être envoyé par un travailleur social ou une association.', 'Mardi et vendredi, 9 h – 13 h', 'Centre commercial Collery, Matoury', 4.884000, -52.317000, 3, '+33536490009', TRUE, '2026-11-03', TRUE),
(10, 'Distribution alimentaire Main tendue (fictif)', 'aide_alimentaire', 'Colis alimentaires gratuits, sans rendez-vous. Venez avec un sac.', 'Mardi et jeudi, 8 h – 11 h', 'Marché de Cayenne, rue Lalouette', 4.936300, -52.329700, 1, '+33536490010', FALSE, '2026-11-01', TRUE),
(11, 'Espace numérique de la médiathèque (fictif)', 'numerique', 'Ordinateurs et internet gratuits. Un conseiller vous aide à créer une adresse mail ou à faire une démarche en ligne.', 'Du mardi au samedi, 9 h – 17 h', 'Rue Lalouette, Cayenne', 4.935500, -52.329000, 1, '+33536490011', TRUE, '2026-11-07', TRUE),
(12, 'Point numérique de Rémire (fictif)', 'numerique', 'Ateliers pour apprendre à se servir d''un téléphone ou d''un ordinateur, en petit groupe. Débutants bienvenus.', 'Lundi et mercredi, 14 h – 17 h', 'Mairie de Rémire-Montjoly', 4.916500, -52.270000, 2, '+33536490012', TRUE, '2026-10-22', TRUE),
(13, 'Maison des démarches de Matoury (fictif)', 'demarches', 'Aide pour vos démarches : impôts, retraite, allocations familiales, permis de conduire, carte grise. Sans rendez-vous le matin.', 'Du lundi au vendredi, 8 h – 16 h', 'Mairie de Matoury', 4.847000, -52.329000, 3, '+33536490013', TRUE, '2026-11-04', TRUE),
(14, 'Écrivain public de Cayenne (fictif)', 'demarches', 'Aide pour écrire une lettre, remplir un formulaire ou comprendre un courrier.', 'Mercredi et vendredi, 9 h – 12 h', 'Place Léopold Héder, Cayenne', 4.939500, -52.335500, 1, '+33536490014', FALSE, '2026-10-29', TRUE),
(15, 'Ressourcerie Guyane Réemploi (fictif)', 'equipement', 'Meubles, électroménager et vêtements d''occasion, à petit prix.', 'Du mercredi au samedi, 9 h – 17 h', 'Zone d''activités de Dégrad-des-Cannes, Rémire-Montjoly', 4.859000, -52.276000, 2, '+33536490015', TRUE, '2026-10-26', TRUE),
(16, 'Vestiaire emploi (fictif)', 'equipement', 'Une tenue pour un entretien d''embauche ou des chaussures de sécurité, prêtées ou données gratuitement. Il faut être envoyé par une structure d''accompagnement.', 'Lundi et jeudi, 9 h – 12 h', 'Préfecture, rue Fiedmont, Cayenne', 4.938500, -52.335000, 1, '+33536490016', TRUE, '2026-11-05', TRUE);

INSERT INTO service_aide_langue (id_service, code_langue) VALUES
(1, 'fr'),
(1, 'gcr'),
(1, 'pt-BR'),
(2, 'fr'),
(2, 'gcr'),
(3, 'fr'),
(3, 'gcr'),
(3, 'ht'),
(3, 'pt-BR'),
(4, 'fr'),
(4, 'en'),
(5, 'fr'),
(5, 'gcr'),
(5, 'ht'),
(5, 'pt-BR'),
(5, 'en'),
(6, 'fr'),
(6, 'gcr'),
(6, 'pt-BR'),
(7, 'fr'),
(7, 'gcr'),
(7, 'ht'),
(7, 'pt-BR'),
(8, 'fr'),
(8, 'gcr'),
(8, 'en'),
(9, 'fr'),
(9, 'gcr'),
(9, 'pt-BR'),
(10, 'fr'),
(10, 'ht'),
(10, 'pt-BR'),
(11, 'fr'),
(11, 'gcr'),
(11, 'en'),
(12, 'fr'),
(12, 'pt-BR'),
(13, 'fr'),
(13, 'gcr'),
(13, 'ht'),
(13, 'pt-BR'),
(14, 'fr'),
(14, 'gcr'),
(14, 'ht'),
(15, 'fr'),
(15, 'pt-BR'),
(16, 'fr'),
(16, 'gcr'),
(16, 'en');

INSERT INTO service_aide_traduction (id_service, code_langue, nom, description, horaires) VALUES
(1, 'en', 'Les Petits Ibis day nursery (fictitious)', 'Childcare for children from 3 months to 6 years old, by the half day. Handy to go to a job interview or a training course. Sign up on site.', 'Monday to Friday, 7:30 am – 5:30 pm'),
(1, 'pt-BR', 'Creche Les Petits Ibis (fictícia)', 'Cuidado de crianças de 3 meses a 6 anos, por meio período. Prático para ir a uma entrevista de emprego ou a um curso. Inscrição no local.', 'De segunda a sexta, 7h30 – 17h30'),
(2, 'en', 'Matoury early childhood centre (fictitious)', 'We help you find a childminder near your home, and we explain the financial help to pay for childcare.', 'Monday, Tuesday and Thursday, 8 am – 12 pm'),
(2, 'pt-BR', 'Centro da primeira infância de Matoury (fictício)', 'Ajudamos você a encontrar uma babá credenciada perto de casa e explicamos as ajudas para pagar o cuidado das crianças.', 'Segunda, terça e quinta, 8h – 12h'),
(3, 'en', 'Housing information point (fictitious)', 'Advice to find a home, apply for social housing or sort out a problem with your landlord.', 'Monday to Friday, 8 am – 12 pm; Wednesday, 2 pm – 5 pm'),
(3, 'pt-BR', 'Ponto de informação sobre moradia (fictício)', 'Conselhos para encontrar uma moradia, pedir uma moradia social ou resolver um problema com o proprietário.', 'De segunda a sexta, 8h – 12h; quarta, 14h – 17h'),
(4, 'en', 'Toit solidaire association (fictitious)', 'For young people aged 18 to 30: help to prepare a rental application and to keep your home.', 'Tuesday and Thursday, 9 am – 4 pm'),
(4, 'pt-BR', 'Associação Toit solidaire (fictícia)', 'Para jovens de 18 a 30 anos: ajuda para preparar um pedido de aluguel e para manter a moradia.', 'Terça e quinta, 9h – 16h'),
(5, 'en', 'Legal advice point (fictitious)', 'Lawyers answer your questions for free: work, family, housing, letters you do not understand.', 'Monday, Wednesday and Friday, 8:30 am – 12:30 pm'),
(5, 'pt-BR', 'Ponto de acesso aos direitos (fictício)', 'Juristas respondem gratuitamente às suas perguntas: trabalho, família, moradia, cartas que você não entende.', 'Segunda, quarta e sexta, 8h30 – 12h30'),
(6, 'en', 'Matoury social rights centre (fictitious)', 'We help you find out which benefits you are entitled to (RSA, in-work benefit, housing benefit) and to apply for them.', 'Monday to Friday, 8 am – 12 pm'),
(6, 'pt-BR', 'Espaço de direitos sociais de Matoury (fictício)', 'Ajudamos você a saber a quais benefícios tem direito (RSA, prêmio de atividade, auxílio-moradia) e a fazer o pedido.', 'De segunda a sexta, 8h – 12h'),
(7, 'en', 'Le Bourg health centre (fictitious)', 'Appointments with a general practitioner, with no extra fees. We also help you register with the national health insurance. Appointments on site.', 'Monday to Saturday, 7:30 am – 1 pm'),
(7, 'pt-BR', 'Centro de saúde do Bourg (fictício)', 'Consultas com um clínico geral, sem cobrança extra. Também ajudamos você a abrir seus direitos ao seguro de saúde. Agendamento no local.', 'De segunda a sábado, 7h30 – 13h'),
(8, 'en', 'Youth listening point (fictitious)', 'A place to talk about your health, your mood or your worries, with a nurse or a psychologist. Free and confidential, with or without an appointment.', 'Wednesday, 1 pm – 6 pm; Saturday, 9 am – 12 pm'),
(8, 'pt-BR', 'Ponto de escuta para jovens (fictício)', 'Um lugar para falar da sua saúde, do seu ânimo ou das suas preocupações, com uma enfermeira ou um psicólogo. Gratuito e confidencial, com ou sem agendamento.', 'Quarta, 13h – 18h; sábado, 9h – 12h'),
(9, 'en', 'Collery community grocery (fictitious)', 'Everyday products at low prices. You need to be referred by a social worker or a charity.', 'Tuesday and Friday, 9 am – 1 pm'),
(9, 'pt-BR', 'Mercearia solidária do Collery (fictícia)', 'Produtos do dia a dia a preço baixo. É preciso ser encaminhado por um assistente social ou uma associação.', 'Terça e sexta, 9h – 13h'),
(10, 'en', 'Main tendue food distribution (fictitious)', 'Free food parcels, no appointment needed. Bring a bag.', 'Tuesday and Thursday, 8 am – 11 am'),
(10, 'pt-BR', 'Distribuição de alimentos Main tendue (fictícia)', 'Cestas de alimentos gratuitas, sem agendamento. Traga uma sacola.', 'Terça e quinta, 8h – 11h'),
(11, 'en', 'Media library digital space (fictitious)', 'Free computers and internet. An adviser helps you create an email address or do a procedure online.', 'Tuesday to Saturday, 9 am – 5 pm'),
(11, 'pt-BR', 'Espaço digital da biblioteca (fictício)', 'Computadores e internet gratuitos. Um orientador ajuda você a criar um e-mail ou a fazer um procedimento on-line.', 'De terça a sábado, 9h – 17h'),
(12, 'en', 'Rémire digital point (fictitious)', 'Workshops to learn how to use a phone or a computer, in small groups. Beginners welcome.', 'Monday and Wednesday, 2 pm – 5 pm'),
(12, 'pt-BR', 'Ponto digital de Rémire (fictício)', 'Oficinas para aprender a usar um celular ou um computador, em pequenos grupos. Iniciantes são bem-vindos.', 'Segunda e quarta, 14h – 17h'),
(13, 'en', 'Matoury paperwork centre (fictitious)', 'Help with your paperwork: taxes, pension, family benefits, driving licence, vehicle registration. No appointment needed in the morning.', 'Monday to Friday, 8 am – 4 pm'),
(13, 'pt-BR', 'Casa dos procedimentos de Matoury (fictícia)', 'Ajuda com seus procedimentos: impostos, aposentadoria, auxílios familiares, carteira de motorista, documento do veículo. Sem agendamento pela manhã.', 'De segunda a sexta, 8h – 16h'),
(14, 'en', 'Cayenne public letter writer (fictitious)', 'Help to write a letter, fill in a form or understand a letter you received.', 'Wednesday and Friday, 9 am – 12 pm'),
(14, 'pt-BR', 'Escrevente público de Caiena (fictício)', 'Ajuda para escrever uma carta, preencher um formulário ou entender uma correspondência.', 'Quarta e sexta, 9h – 12h'),
(15, 'en', 'Guyane Réemploi second-hand shop (fictitious)', 'Second-hand furniture, household appliances and clothes, at low prices.', 'Wednesday to Saturday, 9 am – 5 pm'),
(15, 'pt-BR', 'Brechó Guyane Réemploi (fictício)', 'Móveis, eletrodomésticos e roupas usados, a preço baixo.', 'De quarta a sábado, 9h – 17h'),
(16, 'en', 'Job wardrobe (fictitious)', 'An outfit for a job interview or safety shoes, lent or given for free. You need to be referred by a support organisation.', 'Monday and Thursday, 9 am – 12 pm'),
(16, 'pt-BR', 'Guarda-roupa do emprego (fictício)', 'Uma roupa para entrevista de emprego ou sapatos de segurança, emprestados ou doados gratuitamente. É preciso ser encaminhado por uma estrutura de acompanhamento.', 'Segunda e quinta, 9h – 12h');
