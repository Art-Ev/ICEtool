<p align="center">
<img src="https://github.com/Art-Ev/ICEtool_sources/blob/main/Main_repo_resources/ICEtool_GardenCity.png" width="650" height="170" title="example" />
</p>

<p align="center">
<a href=""><img src="https://img.shields.io/badge/version-2026.07.0-blue" /></a>
<a href=""><img src="https://img.shields.io/badge/project-experimental-yellow" /></a>
<a href="https://github.com/Art-Ev/ICEtool/blob/main/LICENSE"> <img src="https://img.shields.io/badge/licence-GPL 3.0-green" /></a>
</p>

<div align="center">
<img src="https://github.com/Art-Ev/ICEtool/blob/main/Icons/icon.png" width="110" height="83" title="example" />

[Présentation & actualités (FR)](#présentation),
[Project overview (EN)](#project-overview),
[Sponsors](#sponsors),
[Main contributors](#main-contributors)
</div>

---

## Présentation
**ICEtool** est un plugin open-source pour QGIS dédié à la simulation et à l'évaluation des îlots de chaleur urbains (ICU). 

L'outil a été initialement créé et développé bénévolement par **Arthur Evrard** (ingénieur-enseignant). Sa conception répond à une triple vocation :
1. **Pédagogique & Enseignement :** Servir de support de sensibilisation et de formation pour les étudiants (notamment dans le cadre de cours à l'**INSA de Toulouse**).
2. **Bien Commun & Accessibilité :** Offrir un outil gratuit et transparent aux **collectivités territoriales** pour guider leurs politiques d'aménagement face au changement climatique.
3. **Usage Professionnel :** Mettre à disposition de l'ensemble des **bureaux d'études** (dont Egis, employeur de l'auteur) un levier d'action opérationnel.

### Évolutions & Dynamique de Recherche

Le projet évolue en continu (bénévolement et maintenant aussi grâce au soutien de ses [Sponsors](#sponsors))pour améliorer l'outil autour de 4 axes :
* Expérience utilisateurs
* Prise en compte de nouveaux phénomènes (en conservant la philosophie de l'outil) 
* Calibration pour affiner et garantir la qualité des résultats
* Bases de données (notamment matériaux) livrées avec ICEtool

### 🌟 Version Actuelle (Mise à jour "Été 2026")
La version **2026.7.2** intègre désormais :
* La modélisation fine d'objets anthropiques et d'ombrages structurants (protections solaires des bâtiments, arrêts de bus, panneaux photovoltaïques).
* La prise en compte d'**essences d'arbres distinctes** au sein des simulations (réglage distinct des taux de transparence du feuillage).

### 🔬 Travaux de R&D en cours
Soutenus et cofinancés par différents acteurs (**ADEME, Banque des Territoires, Région Nouvelle-Aquitaine, Egis**), les axes de recherche actuels portent sur :
* **Microclimat & Végétation :** Une modélisation approfondie et fine de l'évapotranspiration des arbres, notamment afin de différencier les différentes essences
* **Indicateur de Confort Thermique & Étalonnage :** Une thèse dédiée à la création d'un indicateur de ressenti humain dans l'espace public, couplée à la calibration des modèles thermiques via des campagnes d'expérimentation (voir [l'article de la Caisse des Dépôts](https://caissedesdepots.fr)).
* **Physique des Matériaux :** La caractérisation thermo-radiative de nouveaux revêtements urbains et leur intégration native dans l'outil, menée dans le cadre du projet de recherche [ICEtool+ avec le LRA de l'ENSA Toulouse](https://archi.fr).

## Genèse & gouvernance du projet

### 1. Genèse : une démarche interne Egis (la procédure "ICE")
L'origine du projet repose sur des travaux internes menés au sein d'**[Egis](https://www.egis-group.com/fr/activites/icetool)** (et sa filiale **[Elioth](https://elioth.com/dice-a-icetool-licu-simplifie/)**), avec pour objectif de créer une méthodologie interne — la [procédure "ICE"](https://gitlab.com/elioth/ice) — pour quantifier les îlots de chaleur urbains et guider les projets d'aménagement.
Ces premiers travaux ont été menés avec **Stéphanie Maalouf**, **Guillaume Meunier**, **Olivier Ledru** & **Arthur Evrard** pour poser les bases physiques et méthodologiques de l'outil.

### 2. Pivot open-source & un engagement bénévole (ICEtool v1)
Afin de rendre ces travaux accessibles à toutes les collectivités, urbanistes & établissements d'enseignement, le projet a été repris sous la forme d'un plugin QGIS :
* **Développement bénévole d'Arthur Evrard**
* **Réécriture complète du code**, optimisation drastique, correction et refonte des algorithmes de calcul, et création d'une interface graphique ergonomique — donnant naissance à la première version publique d'**ICEtool**.

### 3. Ecosystème actuel : un modèle mixte et partenarial
Aujourd'hui, ICEtool évolue grâce à une dynamique mixte combinant temps bénévole, professionnel, recherche publique et contributions institutionnelles :
* **Egis & Elioth :** continuent de soutenir l'outil, de l'intégrer dans leurs démarches d'innovation urbaine et d'alimenter les retours d'expérience du monde professionnel.
* **INSA Toulouse (& laboratoire LMDC) :** agit comme sponsor académique. En tant qu'enseignant à l'INSA, Arthur des travaux d'étudiants qui participent aux mises à jour du plugin.
* **ADEME :** valorise et valide la pertinence de l'outil à travers la publication de dossiers et de guides méthodologiques nationaux sur la résilience thermique des villes
* **Banque des Territoires & Région Nouvelle-Aquitaine :** cofinancent les travaux de R&D en cours.

ICEtool est un projet de recherche appliquée maintenu par Arthur Evrard, soutenu par Egis, et partagé en open-source grâce au soutien de sponsors comme l'INSA Toulouse, l'ADEME ou la Banque de Territoires.

---
## Project overview

ICEtool is an all in one QGIS plugin to easily compute ground temperatures in an urban environment. <br>
This allows you to make and highlight the urban design choices (e.g. vegetation, materials) that reduce urban heat island phenomena.

## History & authorship

**ICEtool was created by Arthur Evrard**, engineer at Egis and lecturer at INSA Toulouse. He combines the roles of **initial designer, lead developer and long-term maintainer** of the tool.

1. **Origins — the internal "ICE" procedure at Egis.** The project originates from internal R&D work carried out within Egis (including its subsidiary Elioth) to quantify urban heat islands and guide urban design projects. the initial team has establish the physical and methodological foundation.
2. **The open-source pivot (ICEtool v1).** To make this work accessible to all local authorities and urban planners, Arthur Evrard developed the QGIS plugin **on a volunteer, individual basis**: the code was completely rewritten, the algorithms corrected, redesigned and drastically optimized, and a user-friendly graphical interface was created.
3. **Today — a mixed, partnership-based ecosystem.** Egis and Elioth keep supporting the tool and feeding back field experience; INSA Toulouse (with the LMDC laboratory) acts as official academic sponsor, with student research supervised by Arthur Evrard directly contributing to updates; ADEME recognizes and scientifically validates the tool through national methodological guides on urban thermal resilience; Banque des Territoires and Région Nouvelle-Aquitaine co-fund ongoing R&D.

ICEtool is therefore an applied-research project supported by Arthur, his employer Egis, and released as open source with the academic backing of INSA Toulouse and sponsors.

**To install ICEtool: simply use the plugin manager directly into QGIS** (there is nothing to download, QGIS will take care of everything)

This plugin is based on the preliminary work made with [ICE procedure](https://gitlab.com/elioth/ice) (from Egis: [Elioth](https://elioth.com/) and [VRM](https://www.egis.fr/activites/villes-0)). In addition to being more user-friendly and fully integrated into a plugin, code has been completely rewritten, algorithms have been optimized and new features have been added. </br>
ICEtool includes the shadow generator of [UMEP QGIS plugin](https://github.com/UMEP-dev/UMEP), thanks to UMEP team for all their work ! Check UMEP [here](https://umep-docs.readthedocs.io/en/latest/index.html).

ICEtool sources (for example for material database) are stored just [here](https://github.com/Art-Ev/ICEtool_sources) <br>
To get started with ICEtool, ensure that QGIS Processing Toolbox is displayed (CTRL+ALT+T) and read the user manual in the Help menu of ICEtool.

<p align="center">
<img src="https://github.com/Art-Ev/ICEtool_sources/blob/main/Main_repo_resources/INSA_Example_arrows.png" title="example" />
</p>

ICEtool now with dynamic indicators!
<p align="center">
<img src="https://github.com/Art-Ev/ICEtool_sources/blob/main/Main_repo_resources/Indicators.PNG" height="85" title="indicators" />
</p>

## How to use ICEtool ?
To learn how to use ICEtool :arrow_right: [User manual](https://github.com/Art-Ev/ICEtool/blob/main/Scripts/Docs/HOW_TO_english.pdf)<br>
Pour apprendre à utiliser ICEtool :arrow_right: [Manuel utilisateur](https://github.com/Art-Ev/ICEtool/blob/main/Scripts/Docs/HOW_TO_french.pdf)<br>
(ICEtool as been tested and validated on QGIS 3.10, 3.14, 3.16, 3.18, 3.20, 3.22, 3.24 & 3.26)

## What does ICEtool take into account ?
Ground temperature is an estimation based on :
<p align="center">
<img src="https://latex.codecogs.com/svg.latex?\Large&space;\pagecolor{white}Q_R=Q_H+Q_L+Q_C+{\delta}Q_S" title="ICEtool_computed" />
</p>

with:
- $Q_R$ : Heat flux related to radiation (from the sun, infrared radiation and the atmosphere)
- $Q_H$ : Heat flux related to convection (considered as very low and homogeneous)
- $Q_L$ : Sensitive and latent heat flux of water
- $Q_C$ : Heat flow related to conduction
- ${\delta}Q_S$ : Heat flow related to thermal storage (thermal capacity of materials)

Want to see how ICEtool estimates temperatures inside the soil ? (and understand why Canadian wells are so awesome)
</a>
<p align="center">
<a href="https://www.cableizer.com/blog/post/soil-temperature-calculator/">
<img src="https://github.com/Art-Ev/ICEtool_sources/blob/main/Main_repo_resources/annual_soil_temp.gif" width="250" title="diagram" />
</a>
</p>

## What is not included in the calculation ?
- $Q_R$ : does not include the radiation from the reflection on building facades
- $Q_H$ : The anthropogenic heat flux is not calculated, so neither the heat release from cars nor from air conditioners is evaluated.

## And so, what are the consequences for ICEtool ?
As a consequence of these shortcomings, ICEtool cannot substitute itself to a real thermal simulation like the one that could be realized with envi-met for example. However, ICEtool is a good solution to easily obtain a good approximation based on a calculation performed on solid scientific basis.


## You want to help us with ICEtool but don't know where to start ?
There is some enhancement ideas posted in issues and maybe you will also find some bug to correct...
You have absolutely no idea how ICEtool works but you would like to know so you can help? Take a look at our beautiful diagram! (clic on it to discover the interactive version)
<p align="center">
<a href="https://refined-github-html-preview.kidonng.workers.dev/Art-Ev/ICEtool_sources/raw/main/Main_repo_resources/ICEtool_diagram.html">
<img src="https://github.com/Art-Ev/ICEtool_sources/blob/main/Main_repo_resources/ICEtool_diagram.png" width="800" title="diagram" />
</a>
</p>

---

## Sponsors
<p align="center">
<a href="https://www.egis-group.com/sectors/cities"><img style="float: right;" src="https://upload.wikimedia.org/wikipedia/fr/5/5b/Logo-egis.gif" width="200" title="Egis" /></a>
<a href="https://www.insa-toulouse.fr/fr/index.html"><img style="float: right;" src="https://www.insa-toulouse.fr/wp-content/uploads/2022/10/Logo_INSAvilletoulouse-RVB-HD.png" width="140" title="INSA_T" /></a>
<a href="https://www.lab-lmdc.fr/"><img style="float: right;" src="https://www.lab-lmdc.fr/wp-content/uploads/2021/06/logo-lmdc-2021-1024x469.png" width="180" title="LMDC" /></a>
<a href="https://wiki.resilience-territoire.ademe.fr/wiki/ICEtool"><img style="float: right;" src="https://www.ademe.fr/wp-content/uploads/2022/06/logoademe2020_rvb.jpg" width="120" title="ADEME" /></a>
<a href="https://www.nouvelle-aquitaine.fr/"><img style="float: right;" src="https://www.nouvelle-aquitaine.fr/themes/dsnaq/logo.svg" width="120" title="R_NA" /></a>
</p>

---

## Main contributors:
- [Arthur Evrard](https://www.linkedin.com/in/artev/)
- [Marion Bonhomme](https://www.linkedin.com/in/marion-bonhomme-32418586/)
- [Marie Toubin](https://www.linkedin.com/in/marie-toubin-5259b188/)
- [Antoine Derveaux](https://www.linkedin.com/in/antoine-derveaux-512174151/)
- [Lisa-Marie Coelho](https://www.linkedin.com/in/lisa-marie-coelho-a0701124b/)
- [Stéphanie Maalouf](https://www.linkedin.com/in/stephanie-maalouf/)
- [Marceau Leymarie](https://www.linkedin.com/in/marceau-leymarie-666b671b5/)
- [Florian Guelfi](https://www.linkedin.com/in/florian-guelfi-865404bb/)
- [Guillaume Meunier](https://www.linkedin.com/in/meunierguillaume/)
- [Olivier Ledru](https://www.linkedin.com/in/olivierledru/)

