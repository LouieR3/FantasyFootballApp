import asyncio
import aiohttp
import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import re
import time
from aiohttp import ClientSession, ClientTimeout

start_time = time.time()
count = 0
async def get_data(session, row, csv_columns, max_retries=3):
    global count
    count += 1

    url = row['CLICKTHROUGH']
    print(url)
    retries = 0

    while retries < max_retries:
        try:
            async with session.get(url, timeout=10) as response:
                # if count % 100 == 0:
                #     print(f"{count} records processed")
                if response.status == 200:
                    html_content = await response.text()
                    # Parse the HTML content of the response
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Find the HTML table on the page (you may need to customize this based on the specific structure of the page)
                    parcel_table = soup.find('table', {'id': 'Parcel'})
                    owner_table = soup.find('table', {'id': 'Owner'})
                    if parcel_table is not None and owner_table is not None:
                        # Initialize a dictionary to store the data
                        data_dict = {}
                        
                        # Iterate through the <tr> elements within the "Parcel" table
                        for tr in parcel_table.find_all('tr'):
                            # Find the <td> elements in each <tr>
                            td_elements = tr.find_all('td')
                            if len(td_elements) == 2:
                                # Extract the header (first <td>) and value (second <td>)
                                header = td_elements[0].get_text()
                                header = str(header).replace(":", "")
                                value = td_elements[1].get_text()
                                if value == "-":
                                    value = ""
                                # Store the data in the dictionary
                                # Check if it's the "Legal Description" section
                                if " " == header:
                                    # Combine both values separated by a space
                                    if "Parcel_Legal_Description" in data_dict:
                                        data_dict["Parcel_Legal_Description"] += ", " + value
                                    else:
                                        data_dict["Parcel_Legal_Description"] = value
                                else:
                                    full_header = "Parcel_"+header.replace(" ","_")
                                    data_dict[full_header] = str(value).replace(" ", "")
                        data_dict["Parcel_Legal_Description"] = data_dict["Parcel_Legal_Description"].replace(" , ", "")
                        data_dict["Parcel_Legal_Description"] = data_dict["Parcel_Legal_Description"].lstrip(", ")

                        # Ensure only one space between words in the "Parcel_Site_Location" column
                        if "Parcel_Site_Location" in data_dict:
                            data_dict["Parcel_Site_Location"] = re.sub(' +', ' ', data_dict["Parcel_Site_Location"])
                        if "Parcel_Municipality" in data_dict:
                            data_dict["Parcel_Municipality"] = re.sub(' +', ' ', data_dict["Parcel_Municipality"])

                        # Iterate through the <tr> elements within the "Owner" table
                        for tr in owner_table.find_all('tr'):
                            td_elements = tr.find_all('td')
                            if len(td_elements) == 2:
                                header = td_elements[0].get_text()
                                header = str(header).replace(":", "")
                                value = td_elements[1].get_text()
                                if value == "-":
                                    value = ""
                                # Check if it's the "Name(s)" header
                                if "Name(s)" in header:
                                    # Combine both values separated by a space
                                    if "Owner_Name(s)" in data_dict:
                                        data_dict["Owner_Name(s)"] += " " + value
                                    else:
                                        data_dict["Owner_Name(s)"] = value
                                elif "Mailing Address" in header:
                                    # Combine both values separated by a space
                                    if "Mailing_Address" in data_dict:
                                        data_dict["Owner_Mailing_Address"] += ", " + value
                                    else:
                                        data_dict["Owner_Mailing_Address"] = value
                                else:
                                    full_header = "Owner_"+header.replace(" ","_")
                                    data_dict[full_header] = str(value).replace(" ", "")
                        data_dict["Owner_Mailing_Address"] = data_dict["Owner_Mailing_Address"].replace(",  , ", ", ")
                        
                        if data_dict["Parcel_Property_Type"] == "01 - Taxable Residential":
                            # Get Data from Mortgage Company table
                            mortgage_table = soup.find('table', {'id': 'Mortgage Company'})
                            if mortgage_table is not None:
                                mortgage_df = pd.read_html(StringIO(str(mortgage_table)))[0].dropna()
                                mortgage_df.columns = mortgage_df.iloc[0]
                                mortgage_df = mortgage_df[1:]
                                data_dict["Mortgage_Company"] = mortgage_df["Mortgage Company"].iloc[0]
                                data_dict["Mortgage_Service_Co_Name"] = mortgage_df["Mortgage.Service Co Name"].iloc[0]
                            
                            # Get Data from Original Current Year Assessment table
                            estimate_table = soup.find('table', {'id': 'Original Current Year Assessment'})
                            if estimate_table is not None:
                                estimate_df = pd.read_html(StringIO(str(estimate_table)))[0].dropna(axis=1, how='all')
                                estimate_df.columns = estimate_df.iloc[0]
                                estimate_df.reset_index(drop=True)
                                estimate_df = estimate_df[1:]
                                data_dict["Assessment_Value"] = estimate_df["Assessment Value"].iloc[1]
                                data_dict["Assessment_Date"] = estimate_df["Assessment Date"].iloc[1]
                                data_dict["Assessment_Reason_for_Change"] = estimate_df["Reason for Change"].iloc[1]
                                data_dict["Assessment_Comment"] = estimate_df["Comment"].iloc[1]

                            # ---------------------------------------------------
                            # Get Data from Residential Page
                            # ---------------------------------------------------
                            new_url = url.replace("mode=", "mode=residential")
                            response = requests.get(new_url)
                            if response.status_code == 200:
                                res_soup = BeautifulSoup(response.text, 'html.parser')
                                residential_table = res_soup.find('table', {'id': 'Residential'})
                                yard_table = res_soup.find('table', {'id': 'Outbuildings and Yard Items'})
                                if residential_table is not None:
                                    for tr in residential_table.find_all('tr'):
                                        td_elements = tr.find_all('td')
                                        if len(td_elements) == 2:
                                            header = td_elements[0].get_text()
                                            header = str(header).replace(":", "")
                                            value = td_elements[1].get_text()
                                            if value == "-":
                                                value = ""
                                            if header != "Card" and header != " ":
                                                full_header = "Residential_"+header.replace(" ","_")
                                                data_dict[full_header] = str(value).replace(" ", "")
                                else:
                                    if yard_table is not None:
                                        yard_df = pd.read_html(StringIO(str(yard_table)))[0].dropna(axis=1, how='all')
                                        yard_df.columns = yard_df.iloc[0]
                                        yard_df = yard_df[1:]
                                        data_dict["Yard_Code"] = yard_df["Code"].iloc[0]
                                        data_dict["Yard_Year_Built"] = yard_df["Year Built"].iloc[0]
                                        data_dict["Yard_Effective_Year"] = yard_df["Effective Year"].iloc[0]
                                        data_dict["Yard_Grade"] = yard_df["Grade"].iloc[0]
                                        data_dict["Yard_Units"] = yard_df["Units"].iloc[0]
                                        data_dict["Yard_Area"] = yard_df["Area"].iloc[0]
                                        data_dict["Yard_Value"] = yard_df["Value"].iloc[0]
                                        data_dict["Yard_Homestead_%"] = yard_df["Homestead %"].iloc[0]

                                        # ---------------------------------------------------
                                        # Get Data from Commercial Page
                                        # ---------------------------------------------------
                                        new_url = url.replace("mode=", "mode=comsummary")
                                        response = requests.get(new_url)
                                        if response.status_code == 200:
                                            comm_soup = BeautifulSoup(response.text, 'html.parser')
                                            # Get Data from Commercial table
                                            commercial_table = comm_soup.find('table', {'id': 'Commercial'})
                                            for tr in commercial_table.find_all('tr'):
                                                td_elements = tr.find_all('td')
                                                if len(td_elements) == 2:
                                                    header = td_elements[0].get_text()
                                                    header = str(header).replace(":", "")
                                                    value = td_elements[1].get_text()
                                                    if value == "-":
                                                        value = ""
                                                    if header != "Card" and header != " ":
                                                        full_header = "Commercial_"+header.replace(" ","_")
                                                        data_dict[full_header] = str(value).replace(" ", "")

                                            # Get Data from Summary of Interior/Exterior Data table
                                            summary_table = comm_soup.find('table', {'id': 'Summary of Interior/Exterior Data'})

                                            # Get Data from Interior/Exterior Details table
                                            int_ext_table = comm_soup.find('table', {'id': 'Interior/Exterior Details'})
                                            for tr in int_ext_table.find_all('tr'):
                                                td_elements = tr.find_all('td')
                                                if len(td_elements) == 2:
                                                    header = td_elements[0].get_text()
                                                    header = str(header).replace(":", "")
                                                    value = td_elements[1].get_text()
                                                    if value == "-":
                                                        value = ""
                                                    if header != "Card" and header != " ":
                                                        full_header = "Details_"+header.replace(" ","_")
                                                        data_dict[full_header] = str(value).replace(" ", "")

                                            # Get Data from Other Feature Details table
                                            other_table = comm_soup.find('table', {'id': 'Other Feature Details'})
                                            if other_table is not None:
                                                other_df = pd.read_html(StringIO(str(other_table)))[0].dropna(axis=1, how='all')
                                                other_df.columns = other_df.iloc[0]
                                                other_df = other_df[1:]
                                                data_dict["Other_Code/Description"] = other_df["Code/Description"].iloc[1]
                                                data_dict["Other_Measurement_1"] = other_df["Measurement 1"].iloc[1]
                                                data_dict["Other_Measurement_2"] = other_df["Measurement 2"].iloc[1]
                                                data_dict["Other_Identical_Units"] = other_df["Identical Units"].iloc[1]
                                        # ---------------------------------------------------
                                # ---------------------------------------------------
                        elif data_dict["Parcel_Property_Type"] == "02 - Taxable Commercial":
                            # Get Data from Original Current Year Assessment table
                            estimate_table = soup.find('table', {'id': 'Original Current Year Assessment'})
                            if estimate_table is not None:
                                estimate_df = pd.read_html(StringIO(str(estimate_table)))[0].dropna(axis=1, how='all')
                                estimate_df.columns = estimate_df.iloc[0]
                                estimate_df.reset_index(drop=True)
                                estimate_df = estimate_df[1:]
                                data_dict["Assessment_Value"] = estimate_df["Assessment Value"].iloc[1]
                                data_dict["Assessment_Date"] = estimate_df["Assessment Date"].iloc[1]
                                data_dict["Assessment_Reason_for_Change"] = estimate_df["Reason for Change"].iloc[1]
                                data_dict["Assessment_Comment"] = estimate_df["Comment"].iloc[1]

                            # ---------------------------------------------------
                            # Get Data from Commercial Page
                            # ---------------------------------------------------
                            new_url = url.replace("mode=", "mode=comsummary")
                            response = requests.get(new_url)
                            if response.status_code == 200:
                                comm_soup = BeautifulSoup(response.text, 'html.parser')
                                # Get Data from Commercial table
                                commercial_table = comm_soup.find('table', {'id': 'Commercial'})
                                if commercial_table is not None:
                                    for tr in commercial_table.find_all('tr'):
                                        td_elements = tr.find_all('td')
                                        if len(td_elements) == 2:
                                            header = td_elements[0].get_text()
                                            header = str(header).replace(":", "")
                                            value = td_elements[1].get_text()
                                            if value == "-":
                                                value = ""
                                            if header != "Card" and header != " ":
                                                full_header = "Commercial_"+header.replace(" ","_")
                                                data_dict[full_header] = str(value).replace(" ", "")

                                    # Get Data from Summary of Interior/Exterior Data table
                                    summary_table = comm_soup.find('table', {'id': 'Summary of Interior/Exterior Data'})

                                    # Get Data from Interior/Exterior Details table
                                    int_ext_table = comm_soup.find('table', {'id': 'Interior/Exterior Details'})
                                    for tr in int_ext_table.find_all('tr'):
                                        td_elements = tr.find_all('td')
                                        if len(td_elements) == 2:
                                            header = td_elements[0].get_text()
                                            header = str(header).replace(":", "")
                                            value = td_elements[1].get_text()
                                            if value == "-":
                                                value = ""
                                            if header != "Card" and header != " ":
                                                full_header = "Details_"+header.replace(" ","_")
                                                data_dict[full_header] = str(value).replace(" ", "")

                                    # Get Data from Other Feature Details table
                                    other_table = comm_soup.find('table', {'id': 'Other Feature Details'})
                                    if other_table is not None:
                                        other_df = pd.read_html(StringIO(str(other_table)))[0].dropna(axis=1, how='all')
                                        other_df.columns = other_df.iloc[0]
                                        other_df = other_df[1:]
                                        data_dict["Other_Code/Description"] = other_df["Code/Description"].iloc[1]
                                        data_dict["Other_Measurement_1"] = other_df["Measurement 1"].iloc[1]
                                        data_dict["Other_Measurement_2"] = other_df["Measurement 2"].iloc[1]
                                        data_dict["Other_Identical_Units"] = other_df["Identical Units"].iloc[1]
                            # ---------------------------------------------------

                        data_dict["Parcel_ID"] = str(int(row["PARID"]))
                        data_dict["URL"] = row["CLICKTHROUGH"]
                        data_dict["geometry"] = row["rings"]
                        # extract data into data_dict
                        data_df = pd.DataFrame([data_dict], columns=csv_columns)
                        # print(data_df)
                        data_df.to_csv("parcel_data.csv", mode="a", header=False, index=False)
                    break
        except asyncio.TimeoutError:
            retries += 1
            print(f"Timeout occurred for {url}. Retrying... ({retries}/{max_retries})")
            await asyncio.sleep(2)  # Wait for a bit before retrying

    if retries == max_retries:
        print(f"Failed to fetch data for {url} after {max_retries} retries.")
        print()
        # You might want to handle this case, e.g., logging the failure or raising an exception  

async def main():
    url = "https://dcgis.co.delaware.pa.us/arcgis/rest/services/Delaware_County_Public_Parcels/FeatureServer/0/query"

    # Specify the parameters for the query
    params = {
        "where": "MUNICIPALI = 16",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "json",
        "resultOffset": 0,  # Start with the first record
        "resultRecordCount": 2000,  # Number of records to retrieve per request
    }

    dfs_to_query = []
    query_df = pd.DataFrame()

    while True:
        # Send the GET request to the ArcGIS Feature Service
        response = requests.get(url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            # Extract the features from the response
            features = data.get("features", [])
            # Break the loop if there are no more records
            if not features:
                break
            # Create a DataFrame from the features
            df = pd.json_normalize(features)
            # Create a mapping of new column names
            current_columns = df.columns
            new_columns = {col: col.split('.')[-1] for col in current_columns}
            # Rename the columns in the DataFrame
            df.rename(columns=new_columns, inplace=True)
            # Append the DataFrame to the list
            dfs_to_query.append(df)
            # Increment the result offset for the next iteration
            params["resultOffset"] += params["resultRecordCount"]
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            break
    csv_df = pd.read_csv("parcel_data.csv")
    # Concatenate all DataFrames in the list into the combined DataFrame
    query_df = pd.concat(dfs_to_query, ignore_index=True)
    query_df = query_df[~query_df['PARID'].isin(csv_df['Parcel_ID'])]
    query_df = query_df.head(1000)
    csv_columns = csv_df.columns

    print(len(query_df))
    query_df = query_df[query_df['CLICKTHROUGH'].notnull()]
    print(len(query_df))

    dfs_to_concat = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        count = 0
        for index, row in query_df.iterrows():
            task = asyncio.ensure_future(get_data(session, row, csv_df.columns))
            tasks.append(task)

        try:
            datas = await asyncio.gather(*tasks)
        except asyncio.TimeoutError:
            print("Timeout occurred. Retrying tasks...")
            # Retry the failed tasks
            retry_tasks = []
            for task in tasks:
                if not task.done():
                    retry_task = asyncio.ensure_future(task)
                    retry_tasks.append(retry_task)
            
            datas = await asyncio.gather(*retry_tasks)
    print("DONE")



# Run the event loop
count = 0
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
print(f"Total processed: {count}")
print("Program finished --- %s seconds ---" % (time.time() - start_time))
