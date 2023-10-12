# This file is designed to fetch various records

import dns.resolver
import requests
import time
import logging

# Read the proxy list from the file
with open('lists/proxy_list.txt', 'r') as file:
    proxy_list = [line.strip() for line in file.readlines()]
    
# Create a session with a proxy
session = requests.Session()

# Define a function to set the proxy for the session
def set_proxy(session, proxy):
    session.proxies = {
        "http": proxy,
        "https": proxy
    }

# Function to fetch MX, A, SPF, and DMARC records for a domain
def fetch_records(email, max_retries=3, retry_interval=1):
    domain = email.split('@')[1] 
    records = {
        "mx_record": None,
        "a_record": None,
        "spf_record": None,
        "dmarc_record": None
    }

    attempts = 0
    while attempts < max_retries:
        try:
            proxy = proxy_list[attempts % len(proxy_list)]
            # Set the proxy for the session
            set_proxy(session, proxy)

            # Print the proxy address being used
            print(f"Using proxy: {proxy}")

            # Fetch MX records
            mx_records = dns.resolver.query(domain, 'MX')
            if mx_records:
                records["mx_record"] = str(mx_records[0].exchange)

            # Fetch A records
            a_records = dns.resolver.query(domain, 'A')
            if a_records:
                records["a_record"] = [str(record) for record in a_records]

            # Fetch SPF record
            spf_records = dns.resolver.query(domain, 'TXT')
            for spf_record in spf_records:
                if "v=spf1" in spf_record.to_text():
                    records["spf_record"] = spf_record.to_text().strip('"')

            # Fetch DMARC record
            dmarc_records = dns.resolver.query(f"_dmarc.{domain}", 'TXT')
            for dmarc_record in dmarc_records:
                if "v=DMARC" in dmarc_record.to_text():
                    records["dmarc_record"] = dmarc_record.to_text().strip('"')

            return records

        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            logging.warning(f"No records found for domain: {domain}")
            return records  # If no records are found
        except dns.exception.Timeout:
            attempts += 1
            if attempts < max_retries:
                print(f"Retrying record lookup for {domain} in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                logging.error(f"Maximum retries reached for record lookup for {domain}. Query timed out.")
                return records
        except Exception as e:
            logging.error(f"Error during record lookup for {domain}: {str(e)}")
            return records