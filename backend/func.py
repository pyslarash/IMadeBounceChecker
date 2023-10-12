# This is the file with checks

import re
import dns.resolver
import smtplib
from senderscore import senderscore
import ssl
import socket
import requests

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

# 100 Common domain names
common_domain_names = [
        "gmail.com", "yahoo.com", "hotmail.com", "aol.com", "hotmail.co.uk", "hotmail.fr", "msn.com", "yahoo.fr",
        "wanadoo.fr", "orange.fr", "comcast.net", "yahoo.co.uk", "yahoo.com.br", "yahoo.co.in", "live.com",
        "rediffmail.com", "free.fr", "gmx.de", "web.de", "yandex.ru", "ymail.com", "libero.it", "outlook.com",
        "uol.com.br", "bol.com.br", "mail.ru", "cox.net", "hotmail.it", "sbcglobal.net", "sfr.fr", "live.fr",
        "verizon.net", "live.co.uk", "googlemail.com", "yahoo.es", "ig.com.br", "live.nl", "bigpond.com",
        "terra.com.br", "yahoo.it", "neuf.fr", "yahoo.de", "alice.it", "rocketmail.com", "att.net", "laposte.net",
        "facebook.com", "bellsouth.net", "yahoo.in", "hotmail.es", "charter.net", "yahoo.ca", "yahoo.com.au",
        "rambler.ru", "hotmail.de", "tiscali.it", "shaw.ca", "yahoo.co.jp", "sky.com", "earthlink.net",
        "optonline.net", "freenet.de", "t-online.de", "aliceadsl.fr", "virgilio.it", "home.nl", "qq.com",
        "telenet.be", "me.com", "yahoo.com.ar", "tiscali.co.uk", "yahoo.com.mx", "voila.fr", "gmx.net", "mail.com",
        "planet.nl", "tin.it", "live.it", "ntlworld.com", "arcor.de", "yahoo.co.id", "frontiernet.net", "hetnet.nl",
        "live.com.au", "yahoo.com.sg", "zonnet.nl", "club-internet.fr", "juno.com", "optusnet.com.au",
        "blueyonder.co.uk", "bluewin.ch", "skynet.be", "sympatico.ca", "windstream.net", "mac.com", "centurytel.net",
        "chello.nl", "live.ca", "aim.com", "bigpond.net.au"
    ]

# Checking email syntax
def is_valid_syntax(email):
    # Regular expression for validating an Email
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    
    # Check if the email matches the regular expression
    if re.match(regex, email):
        return True
    else:
        return False

# Check if domain exists
def domain_exists(records):
    # Check if an MX record is present and if there are A records
    return bool(records["mx_record"]) and bool(records["a_record"])

# Check MX record
def has_mx_records(email, records):
    # Extract domain from the email address
    domain = email.split('@')[1]

    # Check if the domain is in the list of excluded domains
    if domain in common_domain_names:
        return True

    # Check if mx_record list in records is not empty
    return bool(records["mx_record"])

# Gets MX record
def mx_records(records):
    # Get the list of MX records
    return records["mx_record"]

# Checking against the list of disposable domains
def is_disposable_email(email, disposable_domains):
    # Extract the domain part of the email
    domain = email.split('@')[-1]
    
    # Check if the domain is in the set of disposable domains
    if domain in disposable_domains:
        return True
    else:
        return False
    
# Checking against the list of role-based usernames
def is_role_based_email(email, role_based_usernames):
    # Extract the username part of the email (before '@')
    username = email.split('@')[0]
    
    # Check if the extracted username is in the set of role-based usernames
    if username in role_based_usernames:
        return True
    else:
        return False
    
# Checking if the IP is blacklisted
def is_domain_ip_blacklisted(records, max_retries=3):
    # Get the list of A records from the records dictionary
    a_records = records.get("a_record", [])

    # Define the DNSBL domain to check against (e.g., zen.spamhaus.org)
    dnsbl_domain = 'zen.spamhaus.org'

    # Iterate through the A records
    for a_record in a_records:
        ip_address = a_record

        attempts = 0
        while attempts < max_retries:
            try:
                proxy = proxy_list[attempts % len(proxy_list)]
                # Set the proxy for the session
                set_proxy(session, proxy)

                # Print the proxy address being used
                print(f"Using proxy: {proxy}")
                
                # Perform a DNS query to check if the IP address is in the blacklist
                query_result = dns.resolver.query(f'{ip_address}.{dnsbl_domain}', 'A')
                
                # If the query succeeds, the IP address is blacklisted
                return True
                
            except dns.resolver.NXDOMAIN:
                return False  # IP address is not blacklisted
            except dns.resolver.Timeout:
                print("DNS query timed out. Retrying...")
            except Exception as e:
                print(f"Error occurred: {e}")
            
            attempts += 1

    print("Maximum retries reached. Unable to determine blacklist status.")
    return False  # Unable to determine blacklist status after max_retries attempts

# Check for greylisting
def is_greylisting_enabled(email):
    domain = email.split('@')[1]
    try:
        # Attempt to connect to the recipient's mail server
        server = smtplib.SMTP(domain)
        server.quit()  # Close the connection if successful
        
        return False  # No greylisting (server accepted the connection)
    except smtplib.SMTPConnectError as e:
        # Check the error code to determine if it's a temporary error (greylisting)
        error_code = e.smtp_code
        if error_code and error_code[0] == '4':
            return True  # Greylisting might be in effect
        else:
            return False  # Other connection errors (not greylisting)
    except Exception as e:
        print(f"Error occurred: {e}")
        return False  # Other errors during the connection attempt
    
# Checking if email uses Microsoft servers    
def is_microsoft_email(records):
    try:
        # Get the list of MX records from the records dictionary
        mx_records = records.get("mx_record")
        mx_without_dot = mx_records.rstrip('.')  # Remove trailing dot, if present
        print(mx_without_dot)
        # Check if any MX record points to Microsoft's servers
        microsoft_domains = ['outlook.com', 'office365.com', 'live.com', 'hotmail.com']
        for microsoft_domain in microsoft_domains:
            if microsoft_domain in mx_without_dot:
                return True  # Email is hosted on Microsoft servers
        return False  # Email is not hosted on Microsoft servers
    except Exception as e:
        print(f"Error occurred: {e}")
        return False  # Error occurred during the check
    
# Getting the sender score
def get_sender_score(records):
    try:
        # Get the list of A records from the records dictionary
        a_records = records.get("a_record", [])

        if not a_records:
            return None  # No A records found

        # Take the first IP address from the A records
        ip_address = a_records[0]

        # Get the Sender Score using the senderscore module
        score = senderscore.get_score(ip_address)
        return score
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

# SPF Record Check
def check_spf_record(records):
    try:
        # Get the SPF record from the records dictionary
        spf_record = records.get("spf_record", None)

        # Check if the SPF record exists
        if spf_record and spf_record.startswith("v=spf1"):
            return True
        
        return False  # No SPF record found or it doesn't start with 'v=spf1'
    except Exception as e:
        print(f"Error occurred: {e}")
        return False
        
# Checking DMARC Record:
def check_dmarc_record(records):
    try:
        # Get the DMARC record from the records dictionary
        dmarc_record = records.get("dmarc_record", None)

        # Check if the DMARC record exists
        if dmarc_record:
            return True
        
        return False  # No DMARC record found
    except Exception as e:
        print(f"Error occurred: {e}")
        return False
        
# Getting SSL Information
def get_ssl_certificate_info(email, port=443):
    # Extract the domain part of the email address
    domain = email.split('@')[1] 
    try:
        # Establish a connection to the domain and port
        context = ssl.create_default_context()
        with context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=domain) as sock:
            sock.connect((domain, port))
            # Get the SSL certificate
            cert = sock.getpeercert()
            return {
                "subject": dict(x[0] for x in cert["subject"]),
                "issuer": dict(x[0] for x in cert["issuer"]),
                "version": cert["version"],
                "serialNumber": cert["serialNumber"],
                "notBefore": cert["notBefore"],
                "notAfter": cert["notAfter"],
                "subjectAltName": cert.get("subjectAltName", []),
            }
    except ssl.SSLError as e:
        return f"SSL Error: {e}"
    except Exception as e:
        return f"Error occurred: {e}"
    
# Domain name

def domain_name(email):
    domain = email.split('@')[1] 
    
    return domain