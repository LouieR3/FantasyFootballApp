import pdfplumber

# Path to your PDF file
pdf_path = "35910389_FL_DW.pdf"

def extract_lead_data(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                # Extract tables from the page
                tables = page.extract_tables()
                
                if not tables:
                    continue  # Skip if no tables on this page
                
                for table in tables:
                    # Process each row in the table
                    for row in table:
                        if len(row) > 1 and "Lead" in row:  # Adjust the condition based on table structure
                            print(f"Page {page_number}: {row}")
                            return row  # Return the row containing 'Lead'
        
        print("Lead data not found in the document.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Run the function
lead_data = extract_lead_data(pdf_path)

if lead_data:
    print("\nExtracted Lead Data:")
    print(lead_data)