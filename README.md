# ICEtool
ICEtool is a QGIS plugin to easily compute ground temperatures in an urban environment. <br>
This allows you to make and highlight the urban design choices (e.g. vegetation, materials) that reduce urban heat island phenomena.

This plugin is based on the preliminary work made with [ICE procedure](https://gitlab.com/elioth/ice) (from [Elioth](https://elioth.com/) and [Egis VRM](https://www.egis.fr/activites/villes-0)). In addition to being more user-friendly and fully integrated into a plugin, code has been completely rewritten, algorithms have been optimized and new features have been added. </br>

ICEtool sources (for example for material database) are stored just [here](https://github.com/Art-Ev/ICEtool_sources) <br>
To work with ICEtool, you will also need UMEP plugin. <br>
To get started with ICEtool, ensure that QGIS Processing Toolbox is displayed (CTRL+ALT+T) and read the user manual in the Help menu of ICEtool.

<p align="center">
<img src="https://github.com/Art-Ev/ICEtool_sources/blob/main/INSA_Example_arrows.png" title="example" />
</p>

## How to use ICEtool ?
To learn how to use ICEtool --> [User manual](https://github.com/Art-Ev/ICEtool/blob/main/Scripts/Docs/HOW_TO_english.pdf)<br>
Pour apprendre à utiliser ICEasy --> [Manuel utilisateur](https://github.com/Art-Ev/ICEtool/blob/main/Scripts/Docs/HOW_TO_french.pdf)<br>
(ICEasy as been tested on QGIS 3.16, 3.18, 3.20 and 3.22, to date it's not compatible with versions <3.16)

## What does ICEtool take into account ?
Ground temperature is an estimation based on :
<p align="center">
<img src="https://latex.codecogs.com/svg.latex?\Large&space;\pagecolor{white}Q_R=Q_H+Q_L+Q_C+{\delta}Q_S" title="ICEtool_computed" />
</p>

with:
- <img src="https://latex.codecogs.com/svg.latex?\Large&space;\pagecolor{white}Q_R" title="QR" /> : Heat flux related to radiation (from the sun, infrared radiation and the atmosphere)
- <img src="https://latex.codecogs.com/svg.latex?\Large&space;\pagecolor{white}Q_H" title="QH" /> : Heat flux related to convection (considered as very low and homogeneous)
- <img src="https://latex.codecogs.com/svg.latex?\Large&space;\pagecolor{white}Q_L" title="QL" /> : Sensitive and latent heat flux of water
- <img src="https://latex.codecogs.com/svg.latex?\Large&space;\pagecolor{white}Q_C" title="QC" /> : Heat flow related to conduction
- <img src="https://latex.codecogs.com/svg.latex?\Large&space;\pagecolor{white}{\delta}Q_S" title="QS" /> : Heat flow related to thermal storage (thermal capacity of materials)

## What is not included in the calculation ?
- <img src="https://latex.codecogs.com/svg.latex?\Large&space;\pagecolor{white}Q_R" title="QR" /> : does not include the radiation from the reflection on building facades
- <img src="https://latex.codecogs.com/svg.latex?\Large&space;\pagecolor{white}Q_H" title="QH" /> : The anthropogenic heat flux is not calculated, so neither the heat release from cars nor from air conditioners is evaluated.

## And so, what are the consequences for ICEtool ?
As a consequence of these shortcomings, ICEtool cannot substitute itself to a real thermal simulation like the one that could be realized with envi-met for example. However, ICEtool is a good solution to easily obtain a good approximation based on a calculation performed on solid scientific basis.
