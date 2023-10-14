# This is the file to work with the datasets

import pandas as pd
import app
import requests
from tqdm import tqdm
import os
import time
import csv

# Set the filename
filename = "emails.csv"

# Importing the file
data = "csv/" + filename

# Importing the name of the email column
col_name = "Email"

# Defining the output directory and filename
output_directory = os.path.join(os.getcwd(), "csv")
output_filename = os.path.splitext(filename)[0] + "_in_progress.csv"
output_file_path = os.path.join(output_directory, output_filename)

df = pd.read_csv(data)

# Save the names of the columns in the original_columns variable
original_columns = df.columns.tolist()

# Trim leading and trailing spaces from the values in the col_name
df[col_name] = df[col_name].str.strip()

# Get the first value in the specified column
first_value = df.loc[0, col_name]

# Define the API endpoint URL
api_endpoint = app.backend_address + f"/single-email/{first_value}"

# Send a GET request to the API
response = requests.get(api_endpoint)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    json_response = response.json()

    # Extract all keys from the JSON response except "email"
    dynamic_keys = [key for key in json_response.keys() if key != "email"]

    # Create new columns in the DataFrame for the dynamic keys and populate them with values
    for key in dynamic_keys:
        if key not in df.columns:  # Check if the column doesn't exist already
            df[key] = json_response[key]
else:
    print(f"API request failed with status code {response.status_code}")
    
# Create a dictionary to store the key-value pairs from API responses
data_dict = {}

# Determine the last processed email from the output file
last_processed_email = None

# Determine the last processed index from the "_in_progress.csv" file
if os.path.exists(output_file_path):
    df_existing = pd.read_csv(output_file_path)
    
    # Check if the output file contains any rows
    if not df_existing.empty:
        last_processed_index = df_existing.index[-1] + 1  # Get the index of the last row + 1
    else:
        last_processed_index = 0
else:
    last_processed_index = 0
    
print(last_processed_index)

progress_bar = tqdm(total=len(df), unit="row", initial=last_processed_index)

# Open the file once in append mode
with open(output_file_path, 'a', newline='') as f:
    writer = csv.writer(f)
    
    # Check if this is the first row (header row)
    if last_processed_index == 0:
        # Write the header row
        header_row = df.columns.tolist()
        writer.writerow(header_row)
    
    # Iterate through the values in the specified column starting from the last processed row
    for index, row in df.iloc[last_processed_index:].iterrows():
        value = row[col_name]

        # Build the API endpoint for the current value
        api_endpoint_full = app.backend_address + f"/single-email/{value}"

        attempts = 0
        success = False
        
        # Try to make the request up to 3 times
        while attempts < 3 and not success:
            # Send a GET request to the API
            response = requests.get(api_endpoint_full)

            # Check if the request was successful
            if response.status_code == 200:
                success = True
                # Parse the JSON response
                json_response = response.json()

                # Update the row with the data from the API response
                for key, val in json_response.items():
                    if key == "email":
                        continue
                    row[key] = val
                    
                    # Update the data dictionary with key-value pairs from the JSON response
                    data_dict[key] = data_dict.get(key, []) + [val]
                    
                # Save the updated row to the in-progress file
                writer.writerow(row)

                # Update the progress bar by 1 row
                progress_bar.update(1)
            
            else:
                attempts += 1
                if attempts < 3:  # Only sleep if we're going to make another attempt
                    time.sleep(3)  # Sleep for 3 seconds before retrying (optional)
        
# Close the progress bar
progress_bar.close()

# Delete the old DataFrame since we need to clear everything
del df

# Load the "_in_progress.csv" file with all of the updated information into a new DataFrame
df = pd.read_csv(output_file_path)

# Define a function to delete rows based on a condition in a column
def delete_rows(condition_column, condition_value):
    return df[df[condition_column] != condition_value]

while True:
    # Prompt the user for input

    # Count the number of "false" values in the "domain_exists" column
    domain_doesnt_exist_count = (df["domain_exists"] == False).sum()
    # Count the number of "false" values in the "has_mx_records" column
    no_mx_record_count = (df["has_mx_records"] == False).sum()
    # Count the number of "false" values in the "is_valid_syntax" column
    invalid_syntax_count = (df["is_valid_syntax"] == False).sum()
    # Count the number of "true" values in the "is_disposable_email" column
    disposable_email_count = (df["is_disposable_email"] == True).sum()
    # Count the number of "true" values in the "is_microsoft_email" column
    microsoft_email_count = (df["is_microsoft_email"] == True).sum()
    # Count the number of "true" values in the "is_role_based_email" column
    rolebased_email_count = (df["is_role_based_email"] == True).sum()

    # Print the count
    print(f"1. Non-existent domains: {domain_doesnt_exist_count}")
    print(f"2. Non-existent MX ecords: {no_mx_record_count}")
    print(f"3. Emails with invalid syntax: {invalid_syntax_count}")
    print(f"4. Number of disposable emails: {disposable_email_count}")
    print(f"5. Number of Microsoft emails: {microsoft_email_count}")
    print(f"6. Number of role-based emails: {rolebased_email_count}")
    user_input = input(f"TYPE THE NUMBER OF WHAT YOU'D LIKE TO DELETE. TYPE 0 TO EXPORT: ")
    
    # Check if the user wants to exit
    if user_input == "0":
        break

    # Check if the input is valid (1 through 6)
    if user_input not in ["1", "2", "3", "4", "5", "6"]:
        print("Invalid input. Please enter a valid number.")
        continue

    # Convert the user input to an integer
    user_choice = int(user_input)

    # Define the column and condition based on the user's choice
    condition_column = ""
    condition_value = ""

    if user_choice == 1:
        condition_column = "domain_exists"
        condition_value = False
    elif user_choice == 2:
        condition_column = "has_mx_records"
        condition_value = False
    elif user_choice == 3:
        condition_column = "is_valid_syntax"
        condition_value = False
    elif user_choice == 4:
        condition_column = "is_disposable_email"
        condition_value = True
    elif user_choice == 5:
        condition_column = "is_microsoft_email"
        condition_value = True
    elif user_choice == 6:
        condition_column = "is_role_based_email"
        condition_value = True

    # Delete rows based on the selected condition
    df = delete_rows(condition_column, condition_value)

# Select only the original columns in the DataFrame
df = df[original_columns]

# Construct the full output file path within the "csv" directory
output_file_path = os.path.join(os.getcwd(), "csv", output_filename)  # Save in "csv" directory in the current directory

# Create the "csv" directory if it doesn't exist
os.makedirs(os.path.join(os.getcwd(), "csv"), exist_ok=True)

# After all processing is complete, rename the in-progress file to the final output file
output_file_path_temp = os.path.join(os.getcwd(), "csv", output_filename.replace("_in_progress.csv", "_filtered.csv"))

# Export the final DataFrame with the modified filename
df.to_csv(output_file_path_temp, index=False)

# Remove the in-progress file
os.remove(output_file_path)

print(f"Filtered data exported to '{output_file_path_temp}'")