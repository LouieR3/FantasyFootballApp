
import pandas as pd
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re

# Read the Excel file and get the DataFrame
def load_excel_file(file_path):
    df = pd.read_excel(file_path)
    return df

# Function to extract year from a date like 15-APR-59 or similar
def extract_year_from_date(sales_date):
    if isinstance(sales_date, str):
        # Regex to find the year in a date like 15-APR-59 or similar
        match = re.search(r'\d{2}-[A-Z]{3}-(\d{2})', sales_date)
        if match:
            year_suffix = match.group(1)
            # Assume dates before 50 are 20xx, after 50 are 19xx
            year = int(year_suffix)
            if year <= 20:
                return 2000 + year
            else:
                return 1900 + year
    return None

# Asynchronously fetch the page and extract the last sales date
async def fetch_property_data(session, parcel_num):
    # Define the URLs for residential, commercial, and owner history pages
    residential_url = f'https://www.buckscountyboa.org/datalets/datalet.aspx?mode=residential&UseSearch=no&pin={parcel_num}&jur=009&taxyr=2024&LMparent=20'
    commercial_url = f'https://www.buckscountyboa.org/datalets/datalet.aspx?mode=commercial&UseSearch=no&pin={parcel_num}&jur=009&taxyr=2024&LMparent=20'
    owner_history_url = f'https://www.buckscountyboa.org/datalets/datalet.aspx?mode=own_history&UseSearch=no&pin={parcel_num}&jur=009&taxyr=2024&LMparent=20'
    
    print(parcel_num)

    # Step 1: Try the residential page to get 'Year Built'
    async with session.get(residential_url) as response:
        if response.status == 200:
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the 'Year Built' field in the residential table
            residential_table = soup.find('table', {'id': 'Residential'})
            if residential_table:
                rows = residential_table.find_all('tr')
                
                for row in rows:
                    columns = row.find_all('td')
                    if len(columns) > 1 and 'Year Built' in columns[0].text:
                        year_built = columns[1].text.strip()
                        if year_built:
                            print(f"Year Built: {year_built}")
                            return year_built  # Return the 'Year Built' value

    # Step 2: If no data from residential, try the commercial page
    print(f'Trying commercial page for parcel number: {parcel_num}')
    async with session.get(commercial_url) as response:
        if response.status == 200:
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the 'Year Built' field in the commercial table
            commercial_table = soup.find('table', {'id': 'Commercial'})  # Adjust the id based on actual page structure
            if commercial_table:
                rows = commercial_table.find_all('tr')
                
                for row in rows:
                    columns = row.find_all('td')
                    if len(columns) > 1 and 'Year Built' in columns[0].text:
                        year_built = columns[1].text.strip()
                        if year_built:
                            print(f"Year Built (Commercial): {year_built}")
                            return year_built  # Return the 'Year Built' value from commercial

    # Step 3: If no data from residential or commercial, try the owner history page
    print(f'Trying owner history page for parcel number: {parcel_num}')
    async with session.get(owner_history_url) as response:
        if response.status == 200:
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the Owner History table and extract sale date
            owner_history_table = soup.find('table', {'id': 'Owner History'})
            if owner_history_table:
                rows = owner_history_table.find_all('tr')
                
                for row in reversed(rows):
                    columns = row.find_all('td')
                    if len(columns) > 5:  # Ensure it has enough columns
                        sale_date = columns[5].text.strip()  # Extract the "Sale Date"
                        if sale_date:
                            return extract_year_from_date(sale_date)  # Process and return the year from sale date

    # Log the URL to a text file if all attempts fail
    with open('failed_urls.txt', 'a') as file:
        file.write(residential_url + '\n')
        file.write(commercial_url + '\n')
        file.write(owner_history_url + '\n')
    
    print(f'Failed to retrieve data for parcel number: {parcel_num}')
    return None

# Main function
async def main():
    # Load the Excel file
    df = load_excel_file('arcgis_with_service_lines.xlsx')

    # Create an aiohttp session for async requests
    async with aiohttp.ClientSession() as session:
        tasks = []
        # Iterate over rows in the dataframe
        for index, row in df.iterrows():
            parcel_num = row['PARCEL_NUM']
            task = asyncio.ensure_future(fetch_property_data(session, parcel_num))
            tasks.append(task)
        
        # Gather all tasks and get the results
        results = await asyncio.gather(*tasks)
        
        # Add the results as a new column in the DataFrame
        df['Property Date'] = results

        # Handle special cases where year ends in '00'
        df['Property Date'] = df['Property Date'].apply(lambda x: None if x == 2000 else x)

        # Save the updated DataFrame to a new Excel file
        df.to_excel('updated_arcgis_with_service_lines.xlsx', index=False)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
