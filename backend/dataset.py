# This is the file to work with the datasets

import pandas as pd
import app
import requests
from tqdm import tqdm  # Import tqdm for the progress bar
import os
import shutil
import csv

# Set the filename
filename = "emails.csv"

# Importing the file
data = "csv/" + filename

# Importing the name of the email column
col_name = "Email"

# Reading the imported file
df = pd.read_csv(data)

# Save the names of the original columns in the original_columns variable
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
        df[key] = json_response[key]

    # Print the column names of the updated DataFrame
    print(df.columns)
else:
    print(f"API request failed with status code {response.status_code}")
    
# Create a dictionary to store the key-value pairs from API responses
data_dict = {}

# Define the output directory and filename
output_directory = os.path.join(os.getcwd(), "csv")
output_filename = os.path.splitext(filename)[0] + "_in_progress.csv"
output_file_path = os.path.join(output_directory, output_filename)

# Initialize tqdm with the total number of rows and specify the mininterval
progress_bar = tqdm(total=len(df), unit="row")

# Create the "csv" directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Check if the file already exists to determine if we need headers
file_exists = os.path.exists(output_file_path)

# Open the file once in append mode
with open(output_file_path, 'a', newline='') as f:
    writer = csv.writer(f)
    
    # If file does not exist, write the headers
    if not file_exists:
        writer.writerow(df.columns)
    
    # Iterate through the values in the specified column
    for index, row in df.iterrows():
        value = row[col_name]

        # Build the API endpoint for the current value
        api_endpoint_full = app.backend_address + f"/single-email/{value}"

        # Send a GET request to the API
        response = requests.get(api_endpoint_full)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            json_response = response.json()

            # Update the row with the data from the API response
            for key, val in json_response.items():
                row[key] = val
                
                # Update the data dictionary with key-value pairs from the JSON response
                data_dict[key] = data_dict.get(key, []) + [val]

            # Save the updated row to the in-progress file
            writer.writerow(row)

            # Update the progress bar by 1 row
            progress_bar.update(1)
            
# Close the progress bar
progress_bar.close()

# Update the DataFrame with the data from the API responses
for key, values in data_dict.items():
    df[key] = values

# Define a function to delete rows based on a condition in a column
def delete_rows(condition_column, condition_value):
    return df[df[condition_column] != condition_value]

# DEBUG

print(df.head())
print(df["is_microsoft_email"].unique())
print(df["is_microsoft_email"].value_counts())

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