<p align="center">
<img src="https://github.com/Art-Ev/ICEtool_sources/blob/main/Main_repo_resources/ICEtool_GardenCity.png" width="650" height="170" title="example" />
</p>

<p align="center">
<a href=""><img src="https://img.shields.io/badge/version-1.4.1-blue" /></a>
<a href=""><img src="https://img.shields.io/badge/project-experimental-yellow" /></a>
<a href="https://github.com/Art-Ev/ICEtool/blob/main/LICENSE"> <img src="https://img.shields.io/badge/licence-GPL 3.0-green" /></a>
</p>

# Presentation

ICEtool is an all in one QGIS plugin to easily compute ground temperatures in an urban environment. <br>
This allows you to make and highlight the urban design choices (e.g. vegetation, materials) that reduce urban heat island phenomena.

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

## they support ICEtool (in many ways) and thanks for that!
<p align="center">
<a href="https://www.egis-group.com/sectors/cities"><img style="float: right;" src="https://upload.wikimedia.org/wikipedia/fr/5/5b/Logo-egis.gif" width="200" title="Egis" /></a>
<a href="https://www.insa-toulouse.fr/fr/index.html"><img style="float: right;" src="https://www.insa-toulouse.fr/wp-content/uploads/2022/10/Logo_INSAvilletoulouse-RVB-HD.png" width="180" title="INSA_T" /></a>
<a href="https://wiki.resilience-territoire.ademe.fr/wiki/ICEtool"><img style="float: right;" src="https://www.ademe.fr/wp-content/uploads/2022/06/logoademe2020_rvb.jpg" width="120" title="ADEME" /></a>
</p>

## And finally, main contributors:
- [Arthur Evrard](https://www.linkedin.com/in/artev/)
- [Stéphanie Maalouf](https://www.linkedin.com/in/stephanie-maalouf/)
- [Marceau Leymarie](https://www.linkedin.com/in/marceau-leymarie-666b671b5/)
- [Florian Guelfi](https://www.linkedin.com/in/florian-guelfi-865404bb/)
- [Guillaume Meunier](https://www.linkedin.com/in/meunierguillaume/)
- [Olivier Ledru](https://www.linkedin.com/in/olivierledru/)
