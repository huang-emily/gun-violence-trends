# MASS SHOOTINGS
setwd("G:\\My Drive\\NCCU\\GRANTS\\01-NSF-HBCU-UP-BPRP-554402-EES1912408\\DSSJ-Projects\\DATA CLEANING")

library(tidyverse)
library(lubridate) # separate the date field into year, month and day

# This dataset was sent to us through email by the Data Manager (Sharon Williams)
# at the Gun Violence Archive (GVA) on Feb 19, 2024 following a request since
# their system was blocking our IP address after a couple of downloads.
# The mass shooting data on their system is available by year.
# The file they sent is in the DOWNLOADED DATASETS folder under the
# name: Save-Sent-By-GVA-Data-Manager-Sharon-Williams-mass-shootings-2014-2023.xlsx

# PRE-CLEANING: The top few rows had the note to cite GVA as the source of the data.
# Those lines were removed manually and the file was saved as .csv
df = read.csv(".\\PRE-CLEANED DATASETS\\pre-semi-cleaned-mass-shootings-2014-2023.csv")

# For information of how this data is collected, 
# go to: https://www.gunviolencearchive.org/explainer
# Definition for mass shooting and mass murder from the above website:
# Mass Shooting Methodology and Reasoning

# Mass Shootings are, for the most part an American phenomenon. While they are 
# generally grouped together as one type of incident they are several different 
# types including public shootings, bar/club incidents, family annihilations, 
# drive-by, workplace and those which defy description but with the established 
# foundation definition being that they have a minimum of four victims shot, 
# either injured or killed, not including any shooter who may also have been 
# killed or injured in the incident. GVA also presents the count of Mass Murder 
# which, like the FBI's definition is four or more victims, killed, not including 
# the shooter. Mass Murder by gun is a subset of the Mass Shooting count.


colnames(df)

df$Date = dmy(df$Date)
df$Year = as.factor(year(df$Date))
df$Month = as.factor(month(df$Date))
df$Day = day(df$Date) #keeping it a numerical variable

names(df) <- c("Incident_ID", "Incident_Date", "Incident_Time", "State_Name", 
                  "City_or_County", "Business_or_Location_Name",
                  "Address", "Latitude", "Longitude", "Victims_Killed", 
                  "Victims_Injured", "Suspects_Killed", "Suspects_Injured", 
                  "Suspects_Arrested", "Incident_Characteristics", "Year", "Month", "Day")
############################
# The US Cities lat-long data was downloaded from 
# https://simplemaps.com/data/us-cities
# on July 21, 2023
# uslatlong = read.csv(".\\DOWNLOADED DATASETS\\uscities.csv")
# colnames(uslatlong)
# uslatlong <- uslatlong[,-c(1)] # keep ascii format (col 2) and remove city name column with spanish accents etc
# colnames(uslatlong)
# names(uslatlong) <- c("City","State_ID", "State_Name", "County_FIPS", 
#                       "County_Name", "Latitude", "Longitude", "Population", "Density",     
#                       "Source", "Military", "Incorporated", "Timezone", "Ranking",     
#                       "ZIPs", "Id")
# colnames(uslatlong)
#############################
# Tried to fuzzy join on lat/long. But too many missing values and some rows on the gun violence data got duplicated in the join
# So abandoning this

#library(fuzzyjoin)
#dfNew <- geo_left_join(df, uslatlong, by = c('Latitude'='Latitude', 'Longitude'='Longitude'), method = "haversine", max_dist = 1,distance_col = NULL)
#############################

dfNew <- df
df2014 <- filter(dfNew, Year == '2014')
df2015 <- filter(dfNew, Year == '2015')
df2016 <- filter(dfNew, Year == '2016')
df2017 <- filter(dfNew, Year == '2017')
df2018 <- filter(dfNew, Year == '2018')
df2019 <- filter(dfNew, Year == '2019')
df2020 <- filter(dfNew, Year == '2020')
df2021 <- filter(dfNew, Year == '2021')
df2022 <- filter(dfNew, Year == '2022')
df2023 <- filter(dfNew, Year == '2023')


write.csv(dfNew,file="cleaned-mass-shootings-2014-2023.csv", row.names = FALSE)

write.csv(df2014,file="cleaned-mass-shootings-2014.csv", row.names = FALSE)
write.csv(df2015,file="cleaned-mass-shootings-2015.csv", row.names = FALSE)
write.csv(df2016,file="cleaned-mass-shootings-2016.csv", row.names = FALSE)
write.csv(df2017,file="cleaned-mass-shootings-2017.csv", row.names = FALSE)
write.csv(df2018,file="cleaned-mass-shootings-2018.csv", row.names = FALSE)
write.csv(df2019,file="cleaned-mass-shootings-2019.csv", row.names = FALSE)
write.csv(df2020,file="cleaned-mass-shootings-2020.csv", row.names = FALSE)
write.csv(df2021,file="cleaned-mass-shootings-2021.csv", row.names = FALSE)
write.csv(df2022,file="cleaned-mass-shootings-2022.csv", row.names = FALSE)
write.csv(df2023,file="cleaned-mass-shootings-2023.csv", row.names = FALSE)

# # For Shantel Reddick - for GURS 2024
# dfSR <- rbind(df2014,df2015,df2016,df2017)
# View(dfSR)
# write.csv(dfSR,file="gurs-mass-shootings-2014-2017.csv", row.names = FALSE)
