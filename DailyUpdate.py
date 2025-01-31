from arcgis.gis import GIS
from arcgis import GeoAccessor
from arcgis.features import Feature
import requests
import json
from arcgis import features
from arcgis.geocoding import get_geocoders, batch_geocode
from arcgis.features.managers import FeatureLayerCollectionManager
import pandas as pd
from datetime import date
from datetime import timedelta
import calendar
import os
import csv
import asyncio
from aiohttp import ClientSession
import time
from urllib.error import HTTPError
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from arcgis.geometry import SpatialReference

# Get time the script started so you know how long it ran
start_time = time.time()

# Deltek specific url to organization
DeltekUrl = "https://pennoni.deltekfirst.com/Pennoni/"

# Deltek API url to gain authentication token
url = DeltekUrl + "api/token"

# Deltek account and API information
DeltekUser = "PENNONIINTEGRATION"
DeltekPassword = "h5TZjKmrMxsuZmhD6T5a!"
DeltekDatabase = "C0000040060P_1_PENNONI0000"
DeltekClientID = "1zlHl4b2SAHyZkicCSFNH2Wu7%2Be8h5X77ILbY5d72o8%3D"
DeltekClientSecret = "fbdce358398a43c78587ddd39fd7104b"

# Cookie information
AWSELB = "7FBF1F35024EFFB27249CF87B253C76DB70CC6F8712C2AD28EB4045E67244EFB221025F93F26A3F3EC5BB64AC0A89D15B6F753594A5FC4B145F47C3322BBAAB040FE08A0A1"
AWSELBCORS = "7FBF1F35024EFFB27249CF87B253C76DB70CC6F8712C2AD28EB4045E67244EFB221025F93F26A3F3EC5BB64AC0A89D15B6F753594A5FC4B145F47C3322BBAAB040FE08A0A1"

# API credentials to gain authentication token with specified credentials
payload = (
    "Username="
    + DeltekUser
    + "&Password="
    + DeltekPassword
    + "&grant_type=password&Integrated=N&database="
    + DeltekDatabase
    + "&Client_Id="
    + DeltekClientID
    + "&client_secret="
    + DeltekClientSecret
)
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "AWSELB=" + AWSELB + "; AWSELBCORS=" + AWSELBCORS,
}

response = requests.request("POST", url, headers=headers, data=payload)
authRes = response.json()
# the authentication token that allows acces to GETs and POSTs to Deltek
authToken = authRes["access_token"]

# --------------------------------------------------------------------------------------------
# Deltek API call to grab all projects with at least a City entered for addfinalJSONResult and WBS1 only
# --------------------------------------------------------------------------------------------

# below variables are used to acquire the YYYY-MM-DD of yesterday and the time of midnight to use when pulling projects modified
today = date.today()
yesterday = today - timedelta(days=1)
utcMidnight = "T04:00:00.000"
estDate = str(yesterday) + utcMidnight

# The columns you want to select for the projects
columnFilter = "name,wbs1,CustClientAlpha,CustProjectFolderPath,ProjMgrEmail,ProjMgrName,desc_CustCorpCommAssistanceRequired,CustCorpCommAssistanceRequestedDate,CustMarketSector,CreateDate,CloseDate,CustBillingClientAlpha,Level1Name,Status,BillingClientContact,Address1,City,State,Zip,Country,StageDescription,CustLatitude,CustLongitude,ProjectType,PlanStartDate,PlanEndDate,desc_CustPrimaryServiceLine,desc_CustBusinessUnit,OrgName,ClientName,BillingClientName,PrincipalName,SupervisorName,desc_CustRegionalVicePresident,desc_CustAssociatePM,BillerName,desc_CustBusinessUnitDirector,desc_CustPrimaryClientAccountManager,desc_CustPrimaryBillingClientAccountManager,ProposalManagerName,MarketingCoordinatorName,BusinessDeveloperLeadName,desc_CustAltBusinessDeveloperLead,Revenue,CustRevenue"

# Check that City column is filled out and that you are just pulling the WBS1 project and not WBS2 or WBS3
url = (
    DeltekUrl
    + "api/project/?fieldFilter="
    + columnFilter
    + "&filterHash[0][name]=City&filterHash[0][value]=&filterHash[0][opp]=!=&filterHash[1][name]=wbs2&filterHash[1][value]&filterHash[1][opp]=="
    + "&filterHash[2][name]=ModDate&filterHash[2][value]="
    + estDate
    + "&filterHash[2][opp]=>=&filterHash[3][name]=ChargeType&filterHash[3][value]=R&filterHash[3][opp]==&filterHash[4][name]=State&filterHash[4][value]=&filterHash[4][opp]=!="
)

payload = ""
headers = {
    "Authorization": "Bearer " + authToken,
    "Cookie": "AWSELB=" + AWSELB + "; AWSELBCORS=" + AWSELBCORS,
}
# --------------------------------------------------------------------------------------------

response = requests.request("GET", url, headers=headers, data=payload)
# take the group of all Deltek projects and turn data into JSON format
jsonObj = response.json()
# list to hold addresses to be geocoded
addrList = []

# assign path variables for your data path, json file, main csv of data, and backup csv which will hold the information of the main csv from the last time a script was run
data_path = "C:\\Users\\gisadmin\\Documents\\Deltek"
csv_file = "DeltekMapLayer.csv"
json_file = "deltekProjects.json"
backupCSV = "Backup.csv"
fullJSON = os.path.join(data_path, json_file)
fullCSV = os.path.join(data_path, csv_file)

# ConvertProjType is a csv file with the data from the ProjectTypeCode database which holds the conversion of Project Type Code to Project Type Name
conv = "ConvertProjType.csv"
convertCSV = os.path.join(data_path, conv)

# keyOfIndices holds all WBS1's correlated to addresses to be geocoded, along with the index within the geocoded list it will be found
keyOfIndices = []
# keyOfLatLong holds the index of the project in the list of projects pulled and the latitude, longitude, and score that correlates to the exact address, city, and state found in the csv
# in short: this is a list of projects with latitude and longitude already found in the csv based on the full address
keyOfLatLong = []

i = 0
# for each project pulled, add together the address elements for the geocoder
while i < len(jsonObj):
    various = "VARIOUS"
    na = "N/A"
    statewide = "Statewide"
    a = ""
    # keep address blank (as to not add a needless comma) unless the address is not null and not populated with the term "various"
    if (
        len(jsonObj[i]["Address1"]) > 0
        and jsonObj[i]["Address1"].upper() != various
        and jsonObj[i]["Address1"].upper() != na
        and jsonObj[i]["Address1"].upper() != statewide
    ):
        a = jsonObj[i]["Address1"] + ", "

    # keep city blank as well if the city is equal to "various"
    b = ""
    if jsonObj[i]["City"].upper() != various and jsonObj[i]["City"].upper() != na:
        b = jsonObj[i]["City"] + ", "

    c = jsonObj[i]["State"] + ", "

    # keep zip code blank without a comma unless the value is not null
    d = ""
    zipCode = str(jsonObj[i]["Zip"])
    if len(zipCode) > 0 and jsonObj[i]["Zip"].upper() != na:
        d = zipCode + ", "

    e = jsonObj[i]["Country"]

    # String of the address as full as it is filled out in Deltek
    addrString = "%s%s%s%s%s" % (a, b, c, d, e)
    # this is boolean to be triggered if the full address string is already in the list to be geocoded
    chk = False
    # tempIndex represents the index in the list to be geocoded for the project to be added to keyOfIndices
    tempIndex = 0

    # Go through the list to be geocoded to this point and check for the full address string
    for addr in addrList:
        # If the address is in the list to be geocoded, add the index of the addrList as a pointer for the address and its unique WBS1, set chk to True, and stop the loop
        if addrString == addr:
            keyOfIndices.append([tempIndex, jsonObj[i]["WBS1"]])
            chk = True
            break
        tempIndex += 1
    # If the address string was not in the list to be geocoded, check the csv for that address next, if still not, add to the list to be geocoded
    if chk == False:
        # this is a second boolean that is triggered if the address is in the csv already, meaning the latitude and longitude can be pulled from there
        nextChk = False
        # Open the main CSV and check if the address has been geocoded before
        with open(fullCSV, "rt", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f, delimiter=",")
            # Skip the header
            next(reader)
            # Go through each row
            for row in reader:
                # If the current address, city, and state are already in the csv at this current row set the Latitude, Longitude, and score to the values the row holds and stop looking through the csv
                if (
                    (
                        jsonObj[i]["Address1"] == row[5]
                        or jsonObj[i]["Address1"].upper() == "N/A"
                        or jsonObj[i]["Address1"].upper() == "VARIOUS"
                        or jsonObj[i]["Address1"].upper() == "STATEWIDE"
                    )
                    and jsonObj[i]["City"] == row[6]
                    and jsonObj[i]["State"] == row[7]
                    and str(row[9]) != "0"
                    and str(row[9]) != "0.0"
                ):
                    lat = row[9]
                    lon = row[10]
                    scre = row[11]
                    # add the index in the list of projects pulled, latitude, longitude, and score to keyOfLatLong to be pulled before adding to the csv
                    keyOfLatLong.append([i, lat, lon, scre])
                    nextChk = True
                    break
        # If you went through the whole CSV and didn't find the address, then add it to the geocoding list and key of indices
        if nextChk == False:
            keyOfIndices.append([tempIndex, jsonObj[i]["WBS1"]])
            addrList.append(addrString)
    i += 1

overlapList = []
overlapIndex = 0
# Go through the csv to get the values held for the OVERLAP and IsNoti columns for each row in the csv which holds a value
with open(fullCSV, "rt", encoding="utf-8", errors="ignore") as f:
    reader = csv.reader(f, delimiter=",")
    # Skip the header
    next(reader)
    # Go through each row
    for row in reader:
        overlap = row[44]
        isnoti = row[45]
        if len(overlap) > 0:
            overlapList.append([overlapIndex, overlap, isnoti])
        overlapIndex += 1

# ESRI's geocoder has a limit of 1000 unique geocodes at one time, if the list to be geocoded is 1000 or more, stop the code
if len(addrList) < 1000:
    # Sign in to ArcGIS with the credentials given and the pennoni arcgis url
    gisUser, gisPass = "GIS_Pennoni", "P3NNON!G!S"
    gis = GIS("https://pennoni.maps.arcgis.com/", gisUser, gisPass)

    # Collection of geocoded project information
    geocodeList = batch_geocode(addrList)

    createdCount = 0

    # Create JSON file with newly geocoded addresses in case it needs to be looked at seperately
    f = open("geocode.txt", "w", encoding="utf8")
    f.write(str(geocodeList))
    f.close()

    # These lines print certain aspects of how many projects have been pulled compared to how many were geocoded for debugging purposes
    print("keyOfLatLong LIST")
    print(len(keyOfLatLong))
    print(keyOfLatLong)
    print()
    print("ADDR LIST")
    print(len(addrList))
    print(addrList)
    print()
    print("keyOfIndices LIST")
    print(len(keyOfIndices))
    print(keyOfIndices)
    print()
    print("==================================================================")
    geocoder = get_geocoders(gis)[0]
    print("MaxBatchSize : " + str(geocoder.properties.locatorProperties.MaxBatchSize))
    print(
        "SuggestedBatchSize : "
        + str(geocoder.properties.locatorProperties.SuggestedBatchSize)
    )
    print(len(jsonObj))
    print(len(geocodeList))
    notGeo = len(jsonObj) - len(geocodeList)
    print("Projects not geocoded: " + str(notGeo))
    print("==================================================================")

    # list to become json object of the projects pulled with the latitude, longitude, and score data added, as well as the U Drive and Deltek links
    finalJSON = []
    # list of projects that need their latitude and longitude updated in Deltek
    deltekUpdateList = []
    # list of WBS1's pulled from Deltek to add to dailyAdded.txt, file to show what WBS1's were modified/added from the script
    updateList = []

    g = 0
    # Go through JSON of all Deltek Projects pulled and create a new JSON which will include geocoded information, as well as U Drive and Deltek links
    while g < len(jsonObj):
        # Create U Drive path for each project systematically
        last = " - "
        uDrivePath = jsonObj[g]["CustProjectFolderPath"]
        uDrivePath = uDrivePath.replace("\n\\", "\\")
        # Data elements needed to construct U Drive Path
        WBS1 = jsonObj[g]["WBS1"]
        Name1 = jsonObj[g]["Level1Name"]
        fullName = "%s%s%s" % (WBS1, last, Name1)
        # Take just the year, month, and day of the start and end date
        PlanStartDate = jsonObj[g]["PlanStartDate"][0:10]
        PlanEndDate = jsonObj[g]["PlanEndDate"][0:10]

        zipCode = str(jsonObj[g]["Zip"])

        # instantiate the variables for latitude, longitude, and score which will be set later depending on where those values are found
        latit, longit, score = 0, 0, 0
        overlap, isnoti = "", ""

        # go through overlapList and set overlap and isnoti to the value it should hold for this index
        for ov in range(len(overlapList)):
            if overlapList[ov][0] == g:
                overlap = overlapList[ov][1]
                isnoti = overlapList[ov][2]
                break
        # boolean which will be triggered the current project from the json is in keyOfIndices
        checker = False
        # go through keyOfIndices and set checker to true if the current project in json was geocoded
        for wb in range(len(keyOfIndices)):
            if WBS1 == keyOfIndices[wb][1]:
                checker = True
                break

        # if the Latitude is in Deltek and the project wasn't geocoded, then set latitude and longitude to the values to those in Deltek
        if (
            len(jsonObj[g]["CustLatitude"]) > 0
            and str(jsonObj[g]["CustLatitude"]) != "0"
            and checker == False
        ):
            latit = jsonObj[g]["CustLatitude"]
            longit = jsonObj[g]["CustLongitude"]
            score = 100
        else:
            # Go through the list of projects that have an identical address to one in the CSV already
            for key in range(len(keyOfLatLong)):
                # If the the index of the JSON is the same as the index of the project which had the same Lat and Long as one in the CSV, set the values and stop the loop
                if keyOfLatLong[key][0] == g:
                    latit = keyOfLatLong[key][1]
                    longit = keyOfLatLong[key][2]
                    score = keyOfLatLong[key][3]
                    break

            # keyIndex is the index for the current project in the list of geocoded address, found by looking at the keyOfIndices
            keyIndex = 0
            # Go through list of geocoded project info and get index to set latitude and longitude
            for wbs in range(len(keyOfIndices)):
                # If the WBS1 from keyOfIndices is the same as the current WBS1 being looked at in the JSON set the index and then Latitude and Longitude
                if keyOfIndices[wbs][1] == WBS1:
                    # set keyIndex to the index where this projects geocode information will be found
                    keyIndex = keyOfIndices[wbs][0]
                    z = 0
                    for gc in range(len(geocodeList)):
                        resID = geocodeList[gc]["attributes"]["ResultID"]
                        if keyIndex == resID:
                            # make sure the geocoder brought back a mostly confident score from the address that is at least in the same state as the one given in the full address string, if not keep at 0,0
                            if (
                                geocodeList[z]["score"] > 70
                                and jsonObj[g]["State"]
                                == geocodeList[z]["attributes"]["RegionAbbr"]
                            ):
                                latit = geocodeList[z]["location"]["y"]
                                longit = geocodeList[z]["location"]["x"]
                                score = geocodeList[z]["score"]
                            break
                        z += 1
            # List which will be used to asynchronously update all Deltek projects in list with the Latitude and Longitude as long as they are not 0,0
            if str(latit) != "0" or str(latit) != "0.0" or latit != 0 or latit != 0.0:
                deltekUpdateList.append([WBS1, latit, longit])

        print(" FINAL RESULT ")
        print(WBS1)
        print(latit)
        print(longit)
        print(score)
        print("=================")

        # go through the ConvertProjType csv to match the Project Type code provided from Deltek with the actual name of the Project Type
        with open(convertCSV, "rt", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f, delimiter=",")
            # Skip the header
            next(reader)
            # Go through each row
            for row in reader:
                # If the current address, city, and state are already in the csv at this current row set the Lat and Long to the values it holds
                if jsonObj[g]["ProjectType"] == row[0]:
                    projectType = row[1]
                    break

        cd = jsonObj[g]["CreateDate"]
        split_string = cd.split("T", 1)
        CreateDate = split_string[0]
        if CreateDate == str(yesterday):
            createdCount += 1
        wd = jsonObj[g]["CloseDate"]
        split_string2 = wd.split("T", 1)
        WLDate = split_string2[0]

        updateList.append(WBS1)
        # JSON object which will reflect the CSV that will be uploaded to ArcGIS
        iterObj = {
            "Name": jsonObj[g]["Name"].replace(",", ""),
            "WBS1": WBS1,
            "FullProjectName": fullName,
            "StageDescription": jsonObj[g]["StageDescription"],
            "Status": jsonObj[g]["Status"],
            "Address": jsonObj[g]["Address1"],
            "City": jsonObj[g]["City"],
            "State": jsonObj[g]["State"],
            "Zip": zipCode,
            "Latitude": latit,
            "Longitude": longit,
            "Score": score,
            "PrimaryServiceLine": jsonObj[g]["desc_CustPrimaryServiceLine"],
            "BusinessUnit": jsonObj[g]["desc_CustBusinessUnit"],
            "ProjectType": projectType,
            "MarketSector": jsonObj[g]["CustMarketSector"],
            "CreateDate": CreateDate,
            "WinLossDate": WLDate,
            "Organization": jsonObj[g]["OrgName"],
            "ClientAlpha": jsonObj[g]["CustClientAlpha"],
            "BillingClientAlpha": jsonObj[g]["CustBillingClientAlpha"],
            "BillingClientContact": jsonObj[g]["BillingClientContact"].replace(",", ""),
            "PlanStartDate": PlanStartDate,
            "PlanEndDate": PlanEndDate,
            "PrincipalinCharge": jsonObj[g]["PrincipalName"],
            "ProjectManager": jsonObj[g]["ProjMgrName"],
            "ProjectManagerEmail": jsonObj[g]["ProjMgrEmail"],
            "ProjectCoordinator": jsonObj[g]["SupervisorName"],
            "RegionalVicePresident": jsonObj[g]["desc_CustRegionalVicePresident"],
            "AssociatePM": jsonObj[g]["desc_CustAssociatePM"],
            "Biller": jsonObj[g]["BillerName"],
            "BusinessUnitDirector": jsonObj[g]["desc_CustBusinessUnitDirector"],
            "AccountManagerforPrimaryClient": jsonObj[g][
                "desc_CustPrimaryClientAccountManager"
            ],
            "AccountManagerforBillingClient": jsonObj[g][
                "desc_CustPrimaryBillingClientAccountManager"
            ],
            "TechnicalLeader": jsonObj[g]["ProposalManagerName"],
            "ProposalSpecialist": jsonObj[g]["MarketingCoordinatorName"],
            "BusinessDevelopmentLead": jsonObj[g]["BusinessDeveloperLeadName"],
            "AltBusinessDevelopmentLead": jsonObj[g][
                "desc_CustAltBusinessDeveloperLead"
            ],
            "EstimatedFee": jsonObj[g]["Revenue"],
            "Revenue": jsonObj[g]["CustRevenue"],
            "CorpCommAssistanceRequired": jsonObj[g][
                "desc_CustCorpCommAssistanceRequired"
            ],
            "CorpCommAsstRequestDate": jsonObj[g][
                "CustCorpCommAssistanceRequestedDate"
            ][0:10],
            # Link to specific project on Deltek
            "URL": "https://pennoni.deltekfirst.com/Pennoni/app/#!Projects/view/project/overview/"
            + WBS1
            + "/presentation",
            "UDrive": uDrivePath,
            "OVERLAP": overlap,
            "IsNotified": isnoti,
        }
        finalJSON.append(iterObj)
        g += 1

    lenAll = len(jsonObj)
    lenGeocode = len(geocodeList)
    notGeo = lenAll - lenGeocode
    finString = str(createdCount)
    pct = (lenGeocode / lenAll) * 100
    percent = "Percentage geocoded: " + str(pct) + "%"

    f = open("dailyAdded.txt", "w", encoding="utf8")
    f.write(str(today))
    f.write("\n")
    f.write(str(updateList))
    f.write("\n")
    f.write("\n")
    f.write(str(lenAll))
    f.write("\n")
    f.write(str(lenGeocode))
    f.write("\n")
    f.write(str(notGeo))
    f.write("\n")
    f.write("Projects created that day: ")
    f.write(finString)
    f.close()

    f = open("geocodeTrack.txt", "a", encoding="utf8")
    f.write("\n")
    f.write("\n")
    f.write(str(today))
    f.write(" ")
    f.write(calendar.day_name[today.weekday()])
    f.write("\n")
    f.write(str(lenAll))
    f.write("\n")
    f.write(str(lenGeocode))
    f.write("\n")
    f.write(str(notGeo))
    f.write("\n")
    f.write("Projects created that day: ")
    f.write(finString)
    f.write("\n")
    f.write(percent)
    f.close()

    username = "PotentialConflicts@pennoni.com"
    password = os.environ.get("MAIL_PASS")
    mail_from = "PotentialConflicts@pennoni.com"

    dayOfWeek = calendar.day_name[today.weekday()]
    today = str(today)
    lenAll = str(lenAll)
    lenGeocode = str(lenGeocode)
    notGeo = str(notGeo)
    SUBJECT = "Daily Deltek Report"
    TEXT = "Date: {0} {1}\nTotal modified projects: {2}\nAmount of geocoded projects: {3}\nProjects not geocoded: {4}\nProjects created that day: {5}\n{6}\n{7}\n\n{8}\n{9}\n".format(
        today,
        dayOfWeek,
        lenAll,
        lenGeocode,
        notGeo,
        finString,
        percent,
        addrList,
        keyOfIndices,
        deltekUpdateList,
    )

    to = "lrodriguez@pennoni.com"
    cc = "ERPRequests@pennoni.com"

    mimemsg = MIMEMultipart()
    mimemsg["From"] = mail_from
    mimemsg["To"] = to
    mimemsg['Cc'] = cc
    mimemsg["Subject"] = SUBJECT
    mimemsg.attach(MIMEText(TEXT, "plain"))
    connection = smtplib.SMTP(host="smtp.office365.com", port=587)
    connection.starttls()
    connection.login(username, password)
    connection.send_message(mimemsg)
    connection.quit()

    # Full JSON object of Deltek Project information ready to be translated to CSV
    finalJSONResult = json.dumps(finalJSON)

    # Create JSON file with final JSON object information
    f = open(json_file, "w", encoding="utf8")
    f.write(finalJSONResult)
    f.close()

    # Create CSV as backup to main CSV of all projects
    def copy_csv(filename):
        df = pd.read_csv(
            filename,
            dtype={
                "Name": "object",
                "WBS1": "object",
                "FullProjectName": "object",
                "StageDescription": "object",
                "Status": "object",
                "Address": "object",
                "City": "object",
                "State": "object",
                "Zip": "object",
                "Latitude": float,
                "Longitude": float,
                "Score": float,
                "PrimaryServiceLine": "object",
                "BusinessUnit": "object",
                "ProjectType": "object",
                "MarketSector": "object",
                "CreateDate": "object",
                "WinLossDate": "object",
                "Organization": "object",
                "ClientAlpha": "object",
                "BillingClientAlpha": "object",
                "BillingClientContact": "object",
                "PlanStartDate": "object",
                "PlanEndDate": "object",
                "PrincipalinCharge": "object",
                "ProjectManager": "object",
                "ProjectManagerEmail": "object",
                "ProjectCoordinator": "object",
                "RegionalVicePresident": "object",
                "AssociatePM": "object",
                "Biller": "object",
                "BusinessUnitDirector": "object",
                "AccountManagerforPrimaryClient": "object",
                "AccountManagerforBillingClient": "object",
                "TechnicalLeader": "object",
                "ProposalSpecialist": "object",
                "BusinessDevelopmentLead": "object",
                "AltBusinessDevelopmentLead": "object",
                "EstimatedFee": float,
                "Revenue": float,
                "CorpCommAssistanceRequired": "object",
                "CorpCommAsstRequestDate": "object",
                "URL": "object",
                "UDrive": "object",
                "OVERLAP": "object",
                "IsNotified": "object",
            },
        )
        df.to_csv(backupCSV, index=False)

    copy_csv(fullCSV)

    # Read through JSON file at specified path and convert to CSV
    df = pd.read_json(fullJSON)
    # Our current dataframe has both the data from our points feature layer and municipality feature layer, so we tell the csv what columns to keep
    column_order = [
        "Name",
        "WBS1",
        "FullProjectName",
        "StageDescription",
        "Status",
        "Address",
        "City",
        "State",
        "Zip",
        "Latitude",
        "Longitude",
        "Score",
        "PrimaryServiceLine",
        "BusinessUnit",
        "ProjectType",
        "MarketSector",
        "CreateDate",
        "WinLossDate",
        "Organization",
        "ClientAlpha",
        "BillingClientAlpha",
        "BillingClientContact",
        "PlanStartDate",
        "PlanEndDate",
        "PrincipalinCharge",
        "ProjectManager",
        "ProjectManagerEmail",
        "ProjectCoordinator",
        "RegionalVicePresident",
        "AssociatePM",
        "Biller",
        "BusinessUnitDirector",
        "AccountManagerforPrimaryClient",
        "AccountManagerforBillingClient",
        "TechnicalLeader",
        "ProposalSpecialist",
        "BusinessDevelopmentLead",
        "AltBusinessDevelopmentLead",
        "EstimatedFee",
        "Revenue",
        "CorpCommAssistanceRequired",
        "CorpCommAsstRequestDate",
        "URL",
        "UDrive",
        "OVERLAP",
        "IsNotified",
    ]
    # add on the json object we just created of the projects pulled with the latitude and longitude data to the main csv
    export_csv = df[column_order].to_csv(
        fullCSV, mode="a", index=False, header=False)

    # making data frame from csv file
    data = pd.read_csv(
        fullCSV,
        dtype={
            "Name": "object",
            "WBS1": "object",
            "FullProjectName": "object",
            "StageDescription": "object",
            "Status": "object",
            "Address": "object",
            "City": "object",
            "State": "object",
            "Zip": "object",
            "Latitude": float,
            "Longitude": float,
            "Score": float,
            "PrimaryServiceLine": "object",
            "BusinessUnit": "object",
            "ProjectType": "object",
            "MarketSector": "object",
            "CreateDate": "object",
            "WinLossDate": "object",
            "Organization": "object",
            "ClientAlpha": "object",
            "BillingClientAlpha": "object",
            "BillingClientContact": "object",
            "PlanStartDate": "object",
            "PlanEndDate": "object",
            "PrincipalinCharge": "object",
            "ProjectManager": "object",
            "ProjectManagerEmail": "object",
            "ProjectCoordinator": "object",
            "RegionalVicePresident": "object",
            "AssociatePM": "object",
            "Biller": "object",
            "BusinessUnitDirector": "object",
            "AccountManagerforPrimaryClient": "object",
            "AccountManagerforBillingClient": "object",
            "TechnicalLeader": "object",
            "ProposalSpecialist": "object",
            "BusinessDevelopmentLead": "object",
            "AltBusinessDevelopmentLead": "object",
            "EstimatedFee": float,
            "Revenue": float,
            "CorpCommAssistanceRequired": "object",
            "CorpCommAsstRequestDate": "object",
            "URL": "object",
            "UDrive": "object",
            "OVERLAP": "object",
            "IsNotified": "object",
        },
    )
    # dropping ALL duplicte values
    data.drop_duplicates(subset="WBS1", keep="last", inplace=True)
    # remake the csv without duplicates
    data.to_csv(fullCSV, index=False)

    # -------------------------------------------------------------------------------------------------------------
    # This section of code deals with performing a spatial join on the layer of projects and layer of municaplity borders and changing the overlap values
    # -------------------------------------------------------------------------------------------------------------

    # connect to the gis.pennoni portal with the gis_integration credentials to grab the municipal county feature layer for the spatial join and then to overwrite the points feature layer
    target_portal = "gis.pennoni.com/portal/"
    target_admin = "gis_integration"
    target_admin_password = "P3NNON!G!S"
    target = GIS(
        "https://" + target_portal,
        target_admin,
        target_admin_password,
        verify_cert=False,
    )

    # Grab the data from the layer of current Pennoni Municipalities
    polys = target.content.get("f315a0eb768845a5928db3a6e2cad115").layers[0]

    # Create spatially enabled dataframe from the polygon feature layer and turn the spatial reference from State Plane to that matching the csv
    poly_df = GeoAccessor.from_layer(polys)
    # Change the spatial reference of the Municipalities layer to match the CSV of data
    poly_df.spatial.project(4326)
    # Create spatially enabled dataframe from the csv of projects
    point_df = GeoAccessor.from_xy(data, "Longitude", "Latitude")

    # Grab the up-to-date CSV data
    data = pd.read_csv(
        fullCSV,
        dtype={
            "Name": "object",
            "WBS1": "object",
            "FullProjectName": "object",
            "StageDescription": "object",
            "Status": "object",
            "Address": "object",
            "City": "object",
            "State": "object",
            "Zip": "object",
            "Latitude": float,
            "Longitude": float,
            "Score": float,
            "PrimaryServiceLine": "object",
            "BusinessUnit": "object",
            "ProjectType": "object",
            "MarketSector": "object",
            "CreateDate": "object",
            "WinLossDate": "object",
            "Organization": "object",
            "ClientAlpha": "object",
            "BillingClientAlpha": "object",
            "BillingClientContact": "object",
            "PlanStartDate": "object",
            "PlanEndDate": "object",
            "PrincipalinCharge": "object",
            "ProjectManager": "object",
            "ProjectManagerEmail": "object",
            "ProjectCoordinator": "object",
            "RegionalVicePresident": "object",
            "AssociatePM": "object",
            "Biller": "object",
            "BusinessUnitDirector": "object",
            "AccountManagerforPrimaryClient": "object",
            "AccountManagerforBillingClient": "object",
            "TechnicalLeader": "object",
            "ProposalSpecialist": "object",
            "BusinessDevelopmentLead": "object",
            "AltBusinessDevelopmentLead": "object",
            "EstimatedFee": float,
            "Revenue": float,
            "CorpCommAssistanceRequired": "object",
            "CorpCommAsstRequestDate": "object",
            "URL": "object",
            "UDrive": "object",
            "OVERLAP": "object",
            "IsNotified": "object",
        },
    )

    # Perform a spatial join on the two GeoDataframes
    xs_df = point_df.spatial.join(poly_df, how="left")

    xs_df["OVERLAP"] = ""

    # Update OVERLAP based on intersection to set any overlapping project to True
    xs_df["OVERLAP"].mask(
        (xs_df["index_right"].notna()), "True", inplace=True,
    )

    # If the project Alpha matches the Alpha of the Municipality company record, don't mark as an Overlap
    for x in range(len(xs_df)):
        alpha = str(xs_df["alpha"][x])
        alpha2 = str(xs_df["alpha2"][x])
        ClientAlpha = str(xs_df["ClientAlpha"][x])
        if (alpha == ClientAlpha) | (alpha2 == ClientAlpha):
            xs_df.at[x, "OVERLAP"] = ""
            xs_df.at[x, "IsNotified"] = ""

    # Update IsNotified based on what fields are marked as an OVERLAP but have not been notified yet
    xs_df["IsNotified"].mask(
        ((xs_df["OVERLAP"] == "True") & (xs_df["IsNotified"].isna())),
        "False",
        inplace=True,
    )
    # Any project that isn't overlapping should have no value in IsNotified
    xs_df["IsNotified"].mask(
        xs_df["OVERLAP"] == "", "", inplace=True,
    )

    column_order = [
        "Name",
        "WBS1",
        "FullProjectName",
        "StageDescription",
        "Status",
        "Address",
        "City",
        "State",
        "Zip",
        "Latitude",
        "Longitude",
        "Score",
        "PrimaryServiceLine",
        "BusinessUnit",
        "ProjectType",
        "MarketSecor",
        "CreatedDate",
        "WinLossDate",
        "Organization",
        "ClientAlpha",
        "BillingClientAlpha",
        "BillingClientContact",
        "PlanStartDate",
        "PlanEndDate",
        "PrincipalinCharge",
        "ProjectManager",
        "ProjectManagerEmail",
        "ProjectCoordinator",
        "RegionalVicePresident",
        "AssociatePM",
        "Biller",
        "BusinessUnitDirector",
        "AccountManagerforPrimaryClient",
        "AccountManagerforBillingClient",
        "TechnicalLeader",
        "ProposalSpecialist",
        "BusinessDevelopmentLead",
        "AltBusinessDevelopmentLead",
        "EstimatedFee",
        "Revenue",
        "CorpCommAssistanceRequired",
        "CorpCommAsstRequestDate",
        "URL",
        "UDrive",
        "OVERLAP",
        "IsNotified",
    ]

    # Export this OVERLAP and IsNotified data to the csv with this column order and without creating an index field
    xs_df[column_order].to_csv(fullCSV, index=False)

    # -------------------------------------------------------------------------------------------------------------
    # Asynchronous functions to update each Deltek project with WBS1 with the Latitude and Longitude in the list
    # -------------------------------------------------------------------------------------------------------------
    # Function to send each PUT request and print response
    async def update_projects_async(wbs1, latit, longit, session):
        url = DeltekUrl + "api/project/" + wbs1
        headers = {
            "Authorization": "Bearer " + authToken,
            "Content-Type": "application/json",
            "Cookie": "AWSELB=" + AWSELB + "; AWSELBCORS=" + AWSELBCORS,
        }
        payload = json.dumps({"CustLatitude": latit, "CustLongitude": longit})
        try:
            response = await session.request(
                method="PUT", url=url, headers=headers, data=payload
            )
            response.raise_for_status()
            # print(f"Response status ({url}): {response.status}")
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error ocurred: {err}")
        response_json = await response.json()
        return response_json

    # Function to run updates on projects for each project in list
    async def run_program(wbs1, latit, longit, session):
        try:
            response = await update_projects_async(wbs1, latit, longit, session)
        except Exception as err:
            print(f"Exception occured: {err}")
            pass

    # Main function to create session and run program for list
    async def main():
        async with ClientSession() as session:
            await asyncio.gather(
                *[
                    run_program(wbs1, latit, longit, session)
                    for wbs1, latit, longit in deltekUpdateList
                ]
            )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    # -------------------------------------------------------------------------------------------------------------

    # given the service ItemID from the ArcGIS rest directory for the feature layer, fetch a feature layer to be edited
    # item = gis.content.get("fce2f1b1e6744e80adfffcb146515122")
    # # FeatureLayerCollectionManager allows you to manipulate a given feature item
    # the_flc = FeatureLayerCollectionManager.fromitem(item)
    # # Overwrite this file with the updated CSV
    # print(the_flc.overwrite(fullCSV))
    # print(item.share(org=True))

    # # This is the hot fix for Project Phoenix
    # searchItem = target.content.search(
    #     query="title:DeltekMapLayer, owner:" + target.users.me.username,
    # )
    # searchItem[0].delete()
    # searchItem[1].delete()

    # # add the csv as an item
    # item_prop = {
    #     "title": "DeltekMapLayer",
    #     "snippet": "This is a dataset of all Pennoni projects found in Deltek",
    #     "tags": "deltek",
    # }
    # csv_item = target.content.add(item_properties=item_prop, data=fullCSV)

    # # publish the csv item into a feature layer
    # projectItems = csv_item.publish()
    # print(projectItems.share(org=True))
    # print(projectItems.shared_with)

    # making data frame from csv file
    data = pd.read_csv(
        fullCSV,
        dtype={
            "Name": "object",
            "WBS1": "object",
            "FullProjectName": "object",
            "StageDescription": "object",
            "Status": "object",
            "Address": "object",
            "City": "object",
            "State": "object",
            "Zip": "object",
            "Latitude": float,
            "Longitude": float,
            "Score": float,
            "PrimaryServiceLine": "object",
            "BusinessUnit": "object",
            "ProjectType": "object",
            "MarketSector": "object",
            "CreateDate": "object",
            "WinLossDate": "object",
            "Organization": "object",
            "ClientAlpha": "object",
            "BillingClientAlpha": "object",
            "BillingClientContact": "object",
            "PlanStartDate": "object",
            "PlanEndDate": "object",
            "PrincipalinCharge": "object",
            "ProjectManager": "object",
            "ProjectManagerEmail": "object",
            "ProjectCoordinator": "object",
            "RegionalVicePresident": "object",
            "AssociatePM": "object",
            "Biller": "object",
            "BusinessUnitDirector": "object",
            "AccountManagerforPrimaryClient": "object",
            "AccountManagerforBillingClient": "object",
            "TechnicalLeader": "object",
            "ProposalSpecialist": "object",
            "BusinessDevelopmentLead": "object",
            "AltBusinessDevelopmentLead": "object",
            "EstimatedFee": float,
            "Revenue": float,
            "CorpCommAssistanceRequired": "object",
            "CorpCommAsstRequestDate": "object",
            "URL": "object",
            "UDrive": "object",
            "OVERLAP": "object",
            "IsNotified": "object",
        },
    )
    # given the service ItemID from the ArcGIS rest directory for the feature layer, fetch the feature layer to be edited
    # change the date columns in the DataFrame which are currently in String format to datetime64
    data["CreatedDate"] = pd.to_datetime(data["CreatedDate"])
    data["WinLossDate"] = pd.to_datetime(data["WinLossDate"])
    data["PlanStartDate"] = pd.to_datetime(data["PlanStartDate"])
    data["PlanEndDate"] = pd.to_datetime(data["PlanEndDate"])
    data["CorpCommAsstRequestDate"] = pd.to_datetime(
        data["CorpCommAsstRequestDate"])
    # pull the feature layer to append to
    lyr = target.content.get("9ff5f3653e29456aa3f56e018dbd0962").layers[0]
    # GeoAccessor class adds a spatial namespace that performs spatial operations on the given Pandas DataFrame
    sdf = GeoAccessor.from_xy(data, "Longitude", "Latitude")

    # convert column names from csv to match lower case format on the ESRI portal
    cols = {
        "Name": "name",
        "WBS1": "wbs1",
        "FullProjectName": "fullprojectname",
        "StageDescription": "stagedescription",
        "Status": "status",
        "Address": "address",
        "City": "city",
        "State": "state",
        "Zip": "zip",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "Score": "score",
        "PrimaryServiceLine": "primaryserviceline",
        "BusinessUnit": "businessunit",
        "ProjectType": "projecttype",
        "MarketSecor": "marketsecor",
        "CreatedDate": "createddate",
        "WinLossDate": "winlossdate",
        "Organization": "organization",
        "ClientAlpha": "clientalpha",
        "BillingClientAlpha": "billingclientalpha",
        "BillingClientContact": "billingclientcontact",
        "PlanStartDate": "planstartdate",
        "PlanEndDate": "planenddate",
        "PrincipalinCharge": "principalincharge",
        "ProjectManager": "projectmanager",
        "ProjectManagerEmail": "projectmanageremail",
        "ProjectCoordinator": "projectcoordinator",
        "RegionalVicePresident": "regionalvicepresident",
        "AssociatePM": "associatepm",
        "Biller": "biller",
        "BusinessUnitDirector": "businessunitdirector",
        "AccountManagerforPrimaryClient": "accountmanagerforprimaryclient",
        "AccountManagerforBillingClient": "accountmanagerforbillingclient",
        "TechnicalLeader": "technicalleader",
        "ProposalSpecialist": "proposalspecialist",
        "BusinessDevelopmentLead": "businessdevelopmentlead",
        "AltBusinessDevelopmentLead": "altbusinessdevelopmentlead",
        "EstimatedFee": "estimatedfee",
        "Revenue": "revenue",
        "CorpCommAssistanceRequired": "corpcommassistancerequired",
        "CorpCommAsstRequestDate": "corpcommasstrequestdate",
        "URL": "url",
        "UDrive": "udrive",
        "OVERLAP": "overlap",
        "IsNotified": "isnotified",
    }
    # rename the column in the DataFrame, this will not change the base csv
    sdf.rename(columns=cols, inplace=True)
    sdf.columns.to_list()
    # truncate all records from the feature layer
    lyr.manager.truncate()

    # apply new records to layer in 200-feature chunks
    i = 0
    while i < len(sdf):
        fs = sdf.loc[i: i + 199].spatial.to_featureset()
        updt = lyr.edit_features(adds=fs)
        msg = updt["addResults"][0]
        # print(f"Rows {i:4} - {i+199:4} : {msg['success']}")
        if "error" in msg:
            print(f"Rows {i:4} - {i+199:4} : {msg['success']}")
            try:
                print(msg["error"]["description"])
            except:
                print(msg["error"])
        i += 200

    # printing length of the list of projects updated in Deltek for debugging purposes
    print(len(deltekUpdateList))
    print(
        "============================================================================"
    )

    # Print the length of time it took the code to run
    print("Feature Layer has been overwritten")
    print("Program finished --- %s seconds ---" % (time.time() - start_time))
else:
    print("BATCH SIZE TOO BIG")
    stri = str(len(addrList))
    print(stri)
