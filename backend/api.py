# This file has functions for API endpoints

from flask import Flask, jsonify, request
import func
import pandas as pd
import csv
import mysql.connector
import random
import string


# Database configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "database": "imadebouncechecker",
    "auth_plugin": "mysql_native_password"
}

# Loading a list of disposable domains

def load_disposable_domains(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return set(line.strip() for line in file)
    except Exception as e:
        print(f"Error loading file: {e}")
        return set()

disposable_domains = load_disposable_domains('./disposable_email_blocklist.txt')

# Loading a list of role-based usernames

def load_role_based_usernames(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return set(line.strip() for line in file)
    except Exception as e:
        print(f"Error loading file: {e}")
        return set()

role_based_usernames = load_role_based_usernames('./role_based_usernames.txt')

# Basic Endpoint
def basic():
    return jsonify(message="This API works just fine!")

def sender_status(email):
    is_domain_ip_blacklisted = func.is_domain_ip_blacklisted(email)
    sender_score = func.get_sender_score(email)
    check_spf_record = func.check_spf_record(email)
    check_dmarc_record = func.check_dmarc_record(email)
    get_ssl_certificate_info = func.get_ssl_certificate_info(email)
    verification_result = {
        'email': email,
        'is_domain_ip_blacklisted': is_domain_ip_blacklisted,
        'sender_score': sender_score,
        'spf_record': check_spf_record,
        'dmarc_record': check_dmarc_record,
        'ssl_info': get_ssl_certificate_info,
    }
    return jsonify(verification_result)

def single_email(email):
    is_valid_syntax = func.is_valid_syntax(email)
    domain_exists = func.domain_exists(email)
    has_mx_records = func.has_mx_records(email)
    is_disposable_email = func.is_disposable_email(email, disposable_domains)
    role_based = func.is_role_based_email(email, role_based_usernames)
    is_domain_ip_blacklisted = func.is_domain_ip_blacklisted(email)
    # is_greylisting_enabled = func.is_greylisting_enabled(email)
    is_microsoft_email = func.is_microsoft_email(email)
    # Prepare verification result
    verification_result = {
        'email': email,
        'is_valid_syntax': is_valid_syntax,
        'domain_exists': domain_exists,
        'has_mx_records': has_mx_records,
        'is_disposable_email': is_disposable_email,
        'is_role_based_email': role_based,
        'is_domain_ip_blacklisted': is_domain_ip_blacklisted,
        'is_microsoft_email': is_microsoft_email,
    }
    return jsonify(verification_result)

file_path = 'emails.csv'

# def load_csv_file(file_path):
#     try:
#         with open(file_path, 'r', newline='') as csvfile:
#             csv_reader = csv.DictReader(csvfile)
#             data = [row for row in csv_reader]
#         return data
#     except Exception as e:
#         print(f"Error loading CSV file: {e}")
#         return None

# Creating a temp table

def create_temporary_table(file_path):
    # Create a random temporary table name
    characters = string.ascii_lowercase + string.digits
    table_name = ''.join(random.choice(characters) for _ in range(32))

    try:
        # Read headers from the CSV file
        with open(file_path, 'r', newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            headers = next(csv_reader)

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Create temporary table with ID column and other columns from headers
        create_table_query = f"""
        CREATE TEMPORARY TABLE {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            {', '.join(f'`{header}` VARCHAR(255)' for header in headers)}
        );
        """
        cursor.execute(create_table_query)

        # Import CSV data into the temporary table using LOAD DATA INFILE
        load_data_query = f"""
        LOAD DATA INFILE '{file_path}'
        INTO TABLE {table_name}
        FIELDS TERMINATED BY ',' 
        IGNORE 1 LINES;
        """
        cursor.execute(load_data_query)

        connection.commit()
        return table_name
    except Exception as e:
        print(f"Error creating temporary table: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def bulk_emails(email_col):
    table_name = create_temporary_table(file_path)
    try:

        # Implement further logic to process data in the temporary table
        # Run queries, perform computations, etc.

        # Example: Fetch data from the temporary table
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Extract the appropriate column name for email_col from the headers
        # Assuming email_col is the name of the column you want to use
        # You can modify this logic based on your specific requirements
        email_col_sql = f'`{email_col}`'

        query = f"SELECT * FROM {table_name} WHERE {email_col_sql} IS NOT NULL;"
        cursor.execute(query)
        results = cursor.fetchall()

        # Process the results and prepare the response
        response_data = []
        for row in results:
            response_data.append({
                "id": row["id"],
                "email": row[email_col]
                # Add more fields as needed
            })

        return jsonify({"data": response_data})
    except Exception as e:
        print(f"Error processing bulk emails: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if table_name:
            # Drop the temporary table after processing
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
                connection.commit()
            except Exception as e:
                print(f"Error dropping temporary table: {e}")
            finally:
                cursor.close()
                connection.close()