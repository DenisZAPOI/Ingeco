-- 014 : offres d'emploi fictives et leurs traductions
-- 12/11/2026, Kurtys TSHIBOLA (équipe BD), issue #48
-- Retour arrière : DELETE FROM offre_emploi_traduction; DELETE FROM offre_emploi;
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

INSERT INTO offre_emploi (id_offre, intitule, employeur, description, type_contrat, plage_horaire, temps_partiel, debutant_accepte, sans_diplome, adresse, lat, lng, id_commune, publiee_le, active) VALUES
(1, 'Employé(e) de rayon', 'Supermarché du Collery (fictif)', 'Vous mettez les produits en rayon et vous aidez les clients à trouver ce qu''ils cherchent. Pas besoin d''expérience : on vous forme sur place les deux premières semaines.', 'cdd', 'journee', FALSE, TRUE, TRUE, 'Centre commercial Collery, Matoury', 4.884000, -52.317000, 3, '2026-11-09 12:00:00', TRUE),
(2, 'Agent(e) d''entretien', 'Propreté Guyane Services (fictif)', 'Nettoyage de bureaux tôt le matin, avant l''arrivée des salariés. Horaires : 5 h – 8 h, du lundi au vendredi. Le matériel est fourni.', 'cdi', 'horaires_decales', TRUE, TRUE, TRUE, 'Préfecture, rue Fiedmont, Cayenne', 4.938500, -52.335000, 1, '2026-11-08 12:00:00', TRUE),
(3, 'Manutentionnaire au port', 'Logistique du Dégrad (fictif)', 'Chargement et déchargement des conteneurs. Travail physique, chaussures de sécurité fournies. Débutants acceptés.', 'interim', 'journee', FALSE, TRUE, TRUE, 'Zone d''activités de Dégrad-des-Cannes, Rémire-Montjoly', 4.859000, -52.276000, 2, '2026-11-08 12:00:00', TRUE),
(4, 'Agent(e) de piste', 'Assistance Aéroport Cayenne (fictif)', 'Vous aidez au chargement des bagages et au guidage des avions. Travail en équipe, de jour comme de nuit selon le planning.', 'cdd', 'nuit', FALSE, TRUE, FALSE, 'Aéroport Félix Éboué, Matoury', 4.819700, -52.360400, 3, '2026-11-07 12:00:00', TRUE),
(5, 'Vendeur(se) au marché', 'Les Fruits de Cayenne (fictif)', 'Vente de fruits et légumes sur l''étal, le mercredi, le vendredi et le samedi matin. Vous accueillez les clients et vous rendez la monnaie.', 'saisonnier', 'journee', TRUE, TRUE, TRUE, 'Marché de Cayenne, rue Lalouette', 4.936300, -52.329700, 1, '2026-11-07 12:00:00', TRUE),
(6, 'Aide-soignant(e) de nuit', 'Centre de soins des Flamboyants (fictif)', 'Vous aidez les patients pour la toilette, les repas et le coucher. Diplôme d''aide-soignant demandé.', 'cdi', 'nuit', FALSE, FALSE, FALSE, 'Hôpital de Cayenne (centre hospitalier), avenue des Flamboyants', 4.931000, -52.319000, 1, '2026-11-06 12:00:00', TRUE),
(7, 'Apprenti(e) cuisinier(ère)', 'Restaurant Les Palmistes (fictif)', 'Formation en alternance : deux jours au centre de formation, trois jours en cuisine. Vous apprenez à préparer les entrées et les desserts.', 'alternance', 'horaires_decales', FALSE, TRUE, TRUE, 'Place des Palmistes, Cayenne', 4.938900, -52.332600, 1, '2026-11-06 12:00:00', TRUE),
(8, 'Agent(e) d''accueil', 'Mairie de Rémire-Montjoly (offre fictive)', 'Vous accueillez le public, vous répondez au téléphone et vous orientez les personnes. Être à l''aise à l''oral ; parler créole ou portugais est un plus.', 'cdd', 'journee', FALSE, FALSE, TRUE, 'Mairie de Rémire-Montjoly', 4.916500, -52.270000, 2, '2026-11-05 12:00:00', TRUE),
(9, 'Plongeur(se) en restauration', 'Snack de la Plage (fictif)', 'Vaisselle et rangement de la cuisine, le soir et le week-end. Aucune expérience demandée.', 'saisonnier', 'horaires_decales', TRUE, TRUE, TRUE, 'Plage de Montjoly, Rémire-Montjoly', 4.923000, -52.279000, 2, '2026-11-05 12:00:00', TRUE),
(10, 'Chauffeur(se)-livreur(se)', 'Livraisons Express Matoury (fictif)', 'Livraison de colis chez les clients de Matoury et de Cayenne. Permis B demandé, véhicule fourni.', 'cdi', 'journee', FALSE, FALSE, TRUE, 'Mairie de Matoury', 4.847000, -52.331000, 3, '2026-11-04 12:00:00', TRUE),
(11, 'Agent(e) de sécurité', 'Sécurité Guyane Plus (fictif)', 'Surveillance d''un centre commercial, rondes et accueil. Carte professionnelle demandée.', 'cdd', 'nuit', FALSE, FALSE, FALSE, 'Centre commercial Collery, Matoury', 4.884000, -52.317000, 3, '2026-11-03 12:00:00', TRUE),
(12, 'Aide à domicile', 'Association Bien Chez Soi (fictif)', 'Vous aidez des personnes âgées pour les courses, le ménage et les repas, à Cayenne. Débutants acceptés, une formation est prévue.', 'cdi', 'journee', TRUE, TRUE, TRUE, 'Gare routière, Cayenne', 4.935400, -52.327700, 1, '2026-11-03 12:00:00', TRUE),
(13, 'Caissier(ère)', 'Supermarché du Collery (fictif)', 'Vous encaissez les achats et vous accueillez les clients. Horaires en roulement, le samedi inclus.', 'cdd', 'horaires_decales', TRUE, TRUE, TRUE, 'Centre commercial Collery, Matoury', 4.884000, -52.317000, 3, '2026-11-02 12:00:00', TRUE),
(14, 'Ouvrier(ère) du bâtiment', 'Bâtir Rémire (fictif)', 'Aide sur les chantiers : préparation, port de matériaux, nettoyage. Chaussures et casque fournis. Débutants acceptés.', 'interim', 'journee', FALSE, TRUE, TRUE, 'Zone d''activités de Dégrad-des-Cannes, Rémire-Montjoly', 4.859000, -52.276000, 2, '2026-11-02 12:00:00', TRUE),
(15, 'Serveur(se) en salle', 'Restaurant Les Palmistes (fictif)', 'Offre pourvue.', 'saisonnier', 'horaires_decales', FALSE, TRUE, TRUE, 'Place des Palmistes, Cayenne', 4.938900, -52.332600, 1, '2026-11-01 12:00:00', FALSE);

INSERT INTO offre_emploi_traduction (id_offre, code_langue, intitule, employeur, description) VALUES
(1, 'en', 'Shelf stacker', 'Collery Supermarket (fictitious)', 'You put products on the shelves and help customers find what they are looking for. No experience needed: you are trained on site for the first two weeks.'),
(1, 'pt-BR', 'Repositor(a)', 'Supermercado do Collery (fictício)', 'Você coloca os produtos nas prateleiras e ajuda os clientes a encontrar o que procuram. Não precisa de experiência: você é treinado(a) no local nas duas primeiras semanas.'),
(2, 'en', 'Cleaner', 'Propreté Guyane Services (fictitious)', 'Cleaning offices early in the morning, before the staff arrive. Hours: 5 am – 8 am, Monday to Friday. Equipment provided.'),
(2, 'pt-BR', 'Auxiliar de limpeza', 'Propreté Guyane Services (fictício)', 'Limpeza de escritórios de manhã cedo, antes da chegada dos funcionários. Horário: 5h – 8h, de segunda a sexta. O material é fornecido.'),
(3, 'en', 'Dock worker', 'Logistique du Dégrad (fictitious)', 'Loading and unloading containers. Physical work, safety shoes provided. Beginners welcome.'),
(3, 'pt-BR', 'Carregador(a) no porto', 'Logistique du Dégrad (fictício)', 'Carga e descarga de contêineres. Trabalho físico, sapatos de segurança fornecidos. Aceita iniciantes.'),
(4, 'en', 'Ramp agent', 'Assistance Aéroport Cayenne (fictitious)', 'You help load luggage and guide planes. Teamwork, day or night depending on the schedule.'),
(4, 'pt-BR', 'Agente de pista', 'Assistance Aéroport Cayenne (fictício)', 'Você ajuda a carregar as bagagens e a guiar os aviões. Trabalho em equipe, de dia ou de noite conforme a escala.'),
(5, 'en', 'Market seller', 'Les Fruits de Cayenne (fictitious)', 'Selling fruit and vegetables at the stall, on Wednesday, Friday and Saturday mornings. You welcome customers and give change.'),
(5, 'pt-BR', 'Vendedor(a) na feira', 'Les Fruits de Cayenne (fictício)', 'Venda de frutas e legumes na barraca, quarta, sexta e sábado de manhã. Você atende os clientes e dá o troco.'),
(6, 'en', 'Night care assistant', 'Flamboyants care centre (fictitious)', 'You help patients with washing, meals and going to bed. A care assistant diploma is required.'),
(6, 'pt-BR', 'Auxiliar de enfermagem noturno(a)', 'Centro de cuidados dos Flamboyants (fictício)', 'Você ajuda os pacientes no banho, nas refeições e na hora de dormir. É exigido o diploma de auxiliar de enfermagem.'),
(7, 'en', 'Apprentice cook', 'Les Palmistes restaurant (fictitious)', 'Work-study training: two days at the training centre, three days in the kitchen. You learn to prepare starters and desserts.'),
(7, 'pt-BR', 'Aprendiz de cozinheiro(a)', 'Restaurante Les Palmistes (fictício)', 'Formação em alternância: dois dias no centro de formação, três dias na cozinha. Você aprende a preparar entradas e sobremesas.'),
(8, 'en', 'Receptionist', 'Rémire-Montjoly town hall (fictitious offer)', 'You welcome the public, answer the phone and direct people. Being at ease speaking is needed; speaking Creole or Portuguese is a plus.'),
(8, 'pt-BR', 'Recepcionista', 'Prefeitura de Rémire-Montjoly (vaga fictícia)', 'Você recebe o público, atende o telefone e orienta as pessoas. Ter facilidade para falar; falar crioulo ou português é um diferencial.'),
(9, 'en', 'Dishwasher', 'Snack de la Plage (fictitious)', 'Washing up and tidying the kitchen, in the evening and at weekends. No experience needed.'),
(9, 'pt-BR', 'Lavador(a) de louça', 'Snack de la Plage (fictício)', 'Lavar a louça e arrumar a cozinha, à noite e nos fins de semana. Não precisa de experiência.'),
(10, 'en', 'Delivery driver', 'Livraisons Express Matoury (fictitious)', 'Delivering parcels to customers in Matoury and Cayenne. Driving licence (B) required, vehicle provided.'),
(10, 'pt-BR', 'Motorista entregador(a)', 'Livraisons Express Matoury (fictício)', 'Entrega de encomendas aos clientes de Matoury e de Caiena. Carteira de motorista B exigida, veículo fornecido.'),
(11, 'en', 'Security guard', 'Sécurité Guyane Plus (fictitious)', 'Guarding a shopping centre, patrols and welcoming visitors. Professional card required.'),
(11, 'pt-BR', 'Vigilante', 'Sécurité Guyane Plus (fictício)', 'Vigilância de um centro comercial, rondas e recepção. Carteira profissional exigida.'),
(12, 'en', 'Home help', 'Bien Chez Soi association (fictitious)', 'You help elderly people with shopping, housework and meals, in Cayenne. Beginners welcome, training is planned.'),
(12, 'pt-BR', 'Cuidador(a) a domicílio', 'Associação Bien Chez Soi (fictício)', 'Você ajuda pessoas idosas nas compras, na limpeza e nas refeições, em Caiena. Aceita iniciantes, há uma formação prevista.'),
(13, 'en', 'Cashier', 'Collery Supermarket (fictitious)', 'You ring up purchases and welcome customers. Rotating hours, Saturdays included.'),
(13, 'pt-BR', 'Operador(a) de caixa', 'Supermercado do Collery (fictício)', 'Você registra as compras e atende os clientes. Horários em rodízio, sábado incluído.'),
(14, 'en', 'Construction worker', 'Bâtir Rémire (fictitious)', 'Helping on building sites: preparation, carrying materials, cleaning. Shoes and helmet provided. Beginners welcome.'),
(14, 'pt-BR', 'Ajudante de obras', 'Bâtir Rémire (fictício)', 'Ajuda nos canteiros de obras: preparação, transporte de materiais, limpeza. Sapatos e capacete fornecidos. Aceita iniciantes.');
