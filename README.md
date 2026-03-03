# Outil-D-cisionnel-de-Gestion-du-Syst-me-lectrique-en-Situation-de-Conjoncture
Le dispositif vise à garantir la stabilité du réseau, minimiser les délestages, protéger les populations et les industriels, et renforcer la résilience du système électrique national. 
2. Architecture Technique du Modèle
Hypothèses structurelles :
•	- MG1 VRA : 72 MW maximum (4 groupes).
•	- MG1 TCN : 55 MW maximum (3 groupes).
•	Capacité Maximum du parc de production solaire de Pobè : 63 MW
•	- Capacité ligne IKEJA–SAKETE : 225 MW.
•	- Priorité économique VRA : MG1 → Import VRA → Transfert de charge si nécessaire sur TCN → Délestage (dernier recours pour sauvegarder le réseau)
•	- Priorité économique TCN : Solaire → Import PARAS/TRANSCORP → MG1 → Délestage (dernier recours pour sauvegarder le réseau).
•	- Transfert inter-îlot en situation de crise.
3. Situations de Conjoncture Intégrées au Modèle
•	Perte PARAS
•	Panne/indisponibilité du Groupe MG1
•	Limitation VRA
•	Limitation TCN
•	Chute Drastique Solaire
•	Blackout VRA
•	Blackout TCN
•	Depacement Import VRA
•	Depacement Import TCN
4. Schéma Décisionnel du Moteur Directeur
1.	Étape 1 : Équilibre local par activation des réserves MG1.
2.	Étape 2 : Optimisation économique des sources disponibles.
3.	Étape 3 : Mobilisation réserve résiduelle via transfert inter-îlot (crise uniquement).
4.	Étape 4 : Délestage maîtrisé en ultime recours.
