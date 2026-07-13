---  
title: French Tax Income
emoji: 👀
colorFrom: gray
colorTo: pink
sdk: gradio
sdk_version: 6.20.0
python_version: '3.12'
app_file: app.py
pinned: false
short_description: ' Calcul de l''impôt sur le revenu d''un contribuable en France'  
---  

*** Calcul de l'impôt sur le revenu d'un contribuable en France**  

l'interface utilisateur est réalisée avec Gradio et accessible avec Hugging Face Spaces 


Les règles de déclaration fiscale sont celles de l'année 2026 (revenu perçu en 2025)  
Le code peut être adapté aux années ultérieures  
  
Le code tient compte des éléments suivants:  
le simulateur est simplifié par rapport à l'officiel mais il en est très proche  
-quotient familial  
-invalidité des personnes à charge  
-invalidité du contribuable et/ou des contribuables mariés  
-plafond du quotient familial  
-situation de famille  
-décôte pour les faibles revenus (distinction entre célibataire et marié)  
-CEHR: contribution exceptionnelle des hauts revenus (tant que le déficit public est supérieur à 3 % du PIB, la CEHR sera appliquée par l'administration sur les plus hauts revenus)  
-choix entre frais réels professionnels ou réduction des 10%  
-pas de maximum sur les frais réels déductibles conformémént à la documentation officielle  
-barème progressif de l’impôt par tranche de revenu:  
Jusqu'à 11 600 €: 0 %  
De 11 601 € à 29 579 €: 11 %  
De 29 580 € à 84 577 €: 30 %  
De 84 578 € à 181 917 €: 41 %  
Supérieure à 181 917 €: 45 %  

Le code ne tient pas compte des crédits d'impôts et niches fiscales qui sont spécifiques individuellement.  
Le code ne tient pas compte des revenus externes(loyers,revenus mobiliers,...)  

sur le plan technique, Python 3.12 a été utilisé            