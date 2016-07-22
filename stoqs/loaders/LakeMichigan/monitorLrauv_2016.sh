#!/bin/bash
cd /opt/stoqsgit_dj1.8/venv-stoqs/bin
source activate
cd /opt/stoqsgit_dj1.8/stoqs/loaders/LakeMichigan
post=''#'--post'
debug=''
start_datetime='20160724T000000'
end_datetime='20160824T000000'
export SLACKTOKEN=${SLACKTOCKEN}
database='stoqs_michigan2016'
urlbase='http://elvis.shore.mbari.org/thredds/catalog/LRAUV'
declare -a searchstr=("/realtime/sbdlogs/2016/.*shore.nc4$" "/realtime/cell-logs/.*Priority.nc4$" "/realtime/cell-logs/.*Normal.nc4$")
declare -a platforms=("tethys")

pos=$(( ${#searchstr[*]} - 1 ))
last=${searchstr[$pos]}

for platform in "${platforms[@]}"
do
    for search in "${searchstr[@]}"
    do
        # get everything before the last /  - this is used as the directory base for saving the interpolated .nc files
        directory=`echo ${search} | sed 's:/[^/]*$::'`
        python monitorLrauv.py --start '${start_datetime}' --end '${end_datetime}' -d  'Lake Michigan LRAUV Experiment 2016' --productDir '/mbari/ODSS/data/canon/2016_OffSeason/Products/LRAUV' \
 	--contourDir '/tmp/LRAUV/stoqs' --contourUrl 'http://dods.mbari.org/opendap/data/lrauv/stoqs/' -o /tmp/LRAUV/${platform}/${directory}/ \
        -u ${urlbase}/${platform}/${search} -b ${database} -c 'Lake Michigan LRAUV Experiment 2016'  --append --autoscale \
        --iparm bin_mean_mass_concentration_of_chlorophyll_in_sea_water \
	--booleanPlotGroup front \
 	--plotDotParmName vertical_temperature_homogeneity_index \
        --parms bin_median_mass_concentration_of_chlorophyll_in_sea_water \
	front \
	vertical_temperature_homogeneity_index \
        bin_mean_mass_concentration_of_chlorophyll_in_sea_water \
        bin_median_mass_concentration_of_chlorophyll_in_sea_water \
        bin_mean_sea_water_temperature \
        bin_median_sea_water_temperature \
        bin_mean_sea_water_temperature  \
        bin_median_sea_water_temperature  \
        bin_mean_sea_water_salinity \
        bin_median_sea_water_salinity \
        sea_water_salinity \
        sea_water_temperature  \
        mass_concentration_of_oxygen_in_sea_water  \
        downwelling_photosynthetic_photon_flux_in_sea_water \
        --plotgroup \
	front \
	vertical_temperature_homogeneity_index \
        bin_mean_mass_concentration_of_chlorophyll_in_sea_water \
        bin_mean_sea_water_temperature \
        bin_mean_sea_water_salinity \
        --latest24hr $post $debug > /tmp/monitorLrauv${platform}.out 2>&1
    done
done

