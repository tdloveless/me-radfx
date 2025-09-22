# me-radfx
IUB ENGR-E-399/599 ME Radiation Effects and Reliability
##  HW 2: Modeling the Natural Space Radiation Environment - SOLUTIONS
### This assignment uses [SPENVIS](https://www.spenvis.oma.be)
1. Using SPENVIS, model the following two orbits

||Polar LEO (POES, IRIDIUM)|HEO (Van Allen Probes, MMS)|
|--|--|--|
|Mission Duration|7 Years|2 years|
|Apogee|825 km|70000 km|
|Perigee|825 km|2500 km|
|Inclination|98.8 deg|28 deg|
|RAAN<sup>1</sup>|0 deg|0 deg|
|Argument of Perigee|0 deg|0 deg|
|True Anomaly|0 degs|0 deg|

<sup>1</sup>Right Ascension of the Ascending Node


* Assume a mission start date of Jan 1, 2026
* Use the following models:
	- Trapped Protons and Electronics: Standard AE-8 (solar max., 50% confidence level), AP-8 (solar min.)
	- CRÉME-96 solar particle model (Worst Day)
	- ESP-PHYCHIC solar particle model for total fluence (95% confidence level)
	- CRÉME-96 galactic cosmic ray model (solar min.)

<!--- ## Polar LEO orbit (30 days): [polar leo orbit parameters](./HW_02_Solutions/P1A-orbit.html) -->

### 1. Orbit Models:
||Polar LEO|HEO|
|--|--|--|
|3D View|![polar leo orbit](./HW_02_Solutions/P1A-orbit.png)||
|World Map View)|![polar leo orbit world map](./HW_02_Solutions/P1A-orbit-worldmap.png)||

### 2A. Trapped Radiation Environment:
||Polar LEO|HEO|
|--|--|--|
|World map of the trapped proton flux (for >10 MeV)|![polar leo orbit world map](./HW_02_Solutions/P1A-orbit-worldmap.png)|![heo orbit](./HW_02_Solutions/P1B-orbit.png)|
|World map of the trapped proton flux (for >200 MeV)|![World map of the trapped proton flux (for >200 MeV)](./HW_02_Solutions/P2A-proton200MeV-worldmap.png)||
* Trapped proton integral flux spectrum (solar min): ![Trapped proton integral flux spectrum](./trapped_proton_integral_flux_loglog.png)

<!--- COMMENTED OUT ORIGINAL, RAW SPENVIS CHARTS
* Trapped proton spectra (solar min): [trapped particle fluxes](./trapped_proton_integral_flux_loglog.png)
	 * World map of the trapped proton flux (for >10 MeV): ![World map of the trapped proton flux (for >10 MeV)](./HW_02_Solutions/P2A-proton10MeV-worldmap.png)

	 * World map of the trapped proton flux (for >200 MeV): ![World map of the trapped proton flux (for >200 MeV)](./HW_02_Solutions/P2A-proton200MeV-worldmap.png)

	 * Trapped proton flux spectrum: ![Trapped proton flux spectrum (solar min)](./HW_02_Solutions/P2A-protonfluxp_spec.png)  -->

### 2B. Solar Radiation Environment:
||Polar LEO|HEO|
|--|--|--|
|World map of the 200 MeV solar proton attenuation factor|![World map of the 200 MeV solar proton attenuation factor](./HW_02_Solutions/P3A-proton_sepflare_map-200MeV.png)||

* Solar proton integral flux spectrum (worst day): ![Solar proton flux spectrum (worst day)](./solar_proton_integral_flux_loglog.png)
* Solar heavy-ion integral flux spectrum (worst day): ![Solar HI flux spectrum (worst day)](./solar_hi_integral_flux_loglog.png)
* Mission average solar proton fluence spectrum: ![Solar proton fluence spectrum](./solar_proton_integral_fluence_loglog.png)
* Mission average solar heavy-ion fluence spectrum: ![Solar HI fluence spectrum](./solar_hi_integral_fluence_loglog.png)


<!--- COMMENTED OUT ORIGINAL, RAW SPENVIS CHARTS
* Solar particle spectra (worst day): [solar particle fluxes](./HW_02_Solutions/P3A-Solar-particle-fluxes.html), [solar particle fluence (95% confidence level)](./HW_02_Solutions/P3A-Solar-particle-fluences.html)
	
	* World map of the 200 MeV solar proton attenuation factor: ![World map of the 200 MeV solar proton attenuation factor](./HW_02_Solutions/P3A-proton_sepflare_map-200MeV.png)
	
	* Solar proton flux spectrum: ![Solar proton flux spectrum (worst day)](./HW_02_Solutions/P3A-Solar-particle-flux-spectra.png) 

	* Mission average solar proton fluence spectrum: ![Solar proton fluence spectrum](./HW_02_Solutions/P3A-proton-fluences.png)

	* Solar heavy ion flux spectrum for He: ![Solar heavy ion flux spectra for He](./HW_02_Solutions/P3A-flarei_specHe.png)

	* Mission average solar He fluence spectrum: ![Mission average solar He fluence spectrum](./HW_02_Solutions/P3A-SolarHe-fluences.png)

	* Solar heavy ion flux spectrum for Fe: ![Solar heavy ion flux spectra for Fe](./HW_02_Solutions/P3A-flarei_specFe.png)

	* Mission average solar Fe fluence spectrum: ![Mission average solar Fe fluence spectrum](./HW_02_Solutions/P3A-SolarFe-fluences.png) -->

### 2C. GCR Radiation Environment:
* GCR spectra: ![GCR proton, He, and Fe flux spectrum](./gcr_hi_integral_flux_loglog.png)


<!--- COMMENTED OUT ORIGINAL, RAW SPENVIS CHARTS
* GCR spectra: [GCR H Spectrum](./HW_02_Solutions/P4A-GCR.htm)
	* H flux spectrum: ![GCR heavy ion flux spectra for H](./HW_02_Solutions/P4A-GCR_H.png)
	* He flux spectrum: ![GCR heavy ion flux spectra for He](./HW_02_Solutions/P4A-GCR_He.png)
	* Fe flux spectrum: ![GCR heavy ion flux spectra for Fe](./HW_02_Solutions/P4A-GCR_Fe.png)
-->

<!--- COMMENTED OUT ORIGINAL, RAW SPENVIS CHARTS
## HEO orbit (30 days): [polar leo orbit parameters](./HW_02_Solutions/P1B-orbit.html)
### 1. Orbit Model:


### 2A. Trapped Radiation Environment:
* Trapped proton spectra (solar min): [trapped particle fluxes](./HW_02_Solutions/P2B-Trapped-particle-fluxes.html)
	* World map of the trapped proton flux (for >10 MeV): ![World map of the trapped proton flux (for >10 MeV)](./HW_02_Solutions/P2B-proton10MeV-worldmap.png)

	* World map of the trapped proton flux (for >200 MeV): ![World map of the trapped proton flux (for >200 MeV)](./HW_02_Solutions/P2B-proton200MeV-worldmap.png)

	* Trapped proton flux spectrum: ![Trapped proton flux spectrum (solar min)](./HW_02_Solutions/P2B-protonfluxp_spec.png) 

### 2B. Solar Radiation Environment:
* Solar particle spectra (worst day): [solar particle fluxes](./HW_02_Solutions/P3B-Solar-particle-fluxes.html), [solar particle fluence (95% confidence level)](./HW_02_Solutions/P3B-Solar-particle-fluences.html)
	
	* World map of the 200 MeV solar proton attenuation factor: ![World map of the 200 MeV solar proton attenuation factor](./HW_02_Solutions/P3B-proton_sepflare_map-200MeV.png)
	
	* Solar proton flux spectrum: ![Solar proton flux spectrum (worst day)](./HW_02_Solutions/P3B-Solar-particle-flux-spectra.png) 

	* Mission average solar proton fluence spectrum: ![Solar proton fluence spectrum](./HW_02_Solutions/P3B-proton-fluences.png)

	* Solar heavy ion flux spectrum for He: ![Solar heavy ion flux spectra for He](./HW_02_Solutions/P3B-flarei_specHe.png)

	* Mission average solar He fluence spectrum: ![Mission average solar He fluence spectrum](./HW_02_Solutions/P3B-SolarHe-fluences.png)

	* Solar heavy ion flux spectrum for Fe: ![Solar heavy ion flux spectra for Fe](./HW_02_Solutions/P3B-flarei_specFe.png)

	* Mission average solar Fe fluence spectrum: ![Mission average solar Fe fluence spectrum](./HW_02_Solutions/P3B-SolarFe-fluences.png)

### 2C. GCR Radiation Environment:

* GCR spectra: [GCR H Spectrum](./HW_02_Solutions/P4A-GCR.htm)
	* H flux spectrum: ![GCR heavy ion flux spectra for H](./HW_02_Solutions/P4B-GCR_H.png)
	* He flux spectrum: ![GCR heavy ion flux spectra for He](./HW_02_Solutions/P4B-GCR_He.png)
	* Fe flux spectrum: ![GCR heavy ion flux spectra for Fe](./HW_02_Solutions/P4B-GCR_Fe.png)
-->

## Analysis
### 3. Name three differences in each of these orbits, as compared to the in-class example of a notional Starlink LEO orbit
* LEO (Polar):
	- Similar,  circular LEO orbit; however, the altitude is > 200km higher
	- As the inclination is greater, the orbit reaches ~30deg higher latitudes compared to the Starlink LEO orbit.
	- Larger concentration of protons at all energies due to the higher altitude
* HEO:
	- Highly elliptical orbit with varying altitudes that travels through the Van Allen Belts
	- Larger concentration of GCRs


### 4. What is the integral flux of trapped protons of energy 1 MeV or greater?  What about for 200 MeV or greater?  
### 5. For the life of each of these missions, how does the total fluence of solar protons of 200 MeV or greater to compare to the Starlink LEO mission?  _Provide the expected ratio (fluence of desired mission)/fluence of Starlink LEO._
### 6. Which mission sees the highest flux of GCR of Z=2 and higher?  How about Z=26 and higher? Why?