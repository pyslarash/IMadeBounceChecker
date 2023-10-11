# This is the file with checks

import re
import dns.resolver
import time
import smtplib
from senderscore import senderscore
import ssl
import socket

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

# Checking if fomain exists
def domain_exists(email, max_retries=3, retry_interval=1):
    attempts = 0
    while attempts < max_retries:
        try:
            # Extract domain from the email address
            domain = email.split('@')[1]

            # Perform a DNS query to check if MX records exist for the domain
            dns.resolver.query(domain, 'MX')
            return True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return False
        except dns.exception.Timeout:
            attempts += 1
            if attempts < max_retries:
                print(f"Retrying query for {domain} in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                print(f"Maximum retries reached for {domain}. Query timed out.")
                return False

# Check MX record

def has_mx_records(email, max_retries=3, retry_interval=1):
    domain = email.split('@')[1]
    excluded_domains = common_domain_names

    if domain in excluded_domains:
        return True

    attempts = 0
    while attempts < max_retries:
        try:
            answers = dns.resolver.query(domain, 'MX')
            return len(answers) > 0
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return False
        except dns.exception.Timeout:
            attempts += 1
            if attempts < max_retries:
                print(f"Retrying query for {domain} in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                print(f"Maximum retries reached for {domain}. Query timed out.")
                return False

# Gets MX record

def get_mx_record(email):
    try:
        # Extract the domain from the email address
        domain = email.split('@')[1]

        # Perform an MX record lookup
        mx_records = dns.resolver.query(domain, 'MX')
        
        # Return the first MX record found
        if mx_records:
            return str(mx_records[0].exchange)
        
        return "null"  # If no MX record is found

    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
        return "null"  # If an error occurs during the lookup

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

def is_domain_ip_blacklisted(email, max_retries=3):
    domain = email.split('@')[1]
    try:
        # Perform a DNS query to get the IP address of the domain
        ip_address = dns.resolver.query(domain, 'A')[0].address
        
        def is_ip_blacklisted(ip_address, dnsbl_domain='zen.spamhaus.org'):
            try:
                # Perform a DNS query to check if the IP address is in the blacklist
                query_result = dns.resolver.query(f'{ip_address}.{dnsbl_domain}', 'A')
                return True  # IP address is blacklisted
            except dns.resolver.NXDOMAIN:
                return False  # IP address is not blacklisted
            except dns.resolver.Timeout:
                print("DNS query timed out. Unable to check IP blacklist status.")
                return False  # Unable to determine blacklist status due to timeout
            except Exception as e:
                print(f"Error occurred: {e}")
                return False  # Error occurred during DNS query

        # Retry the check in case of a timeout
        attempts = 0
        while attempts < max_retries:
            if is_ip_blacklisted(ip_address):
                return True
            attempts += 1
        
        return False  # IP address is not blacklisted after max_retries attempts
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        print(f"No IP address found for domain: {domain}")
        return False  # Domain does not resolve to an IP address
    except dns.resolver.Timeout:
        print("DNS query timed out. Unable to check IP blacklist status.")
        return False  # Unable to determine blacklist status due to timeout
    except Exception as e:
        print(f"Error occurred: {e}")
        return False  # Error occurred during DNS query

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
    
def is_microsoft_email(email):
    try:
        # Extract domain from the email address
        domain = email.split('@')[1]
        
        # Perform a DNS query to get MX records for the domain
        mx_records = dns.resolver.query(domain, 'MX')
        
        # Check if any MX record points to Microsoft's servers
        microsoft_domains = ['outlook.com', 'office365.com', 'live.com', 'hotmail.com']
        for mx in mx_records:
            for microsoft_domain in microsoft_domains:
                if microsoft_domain in str(mx.exchange):
                    return True  # Email is hosted on Microsoft servers
        return False  # Email is not hosted on Microsoft servers
    except dns.resolver.NXDOMAIN:
        print(f"No MX records found for domain: {domain}")
        return False  # Domain does not have MX records
    except Exception as e:
        print(f"Error occurred: {e}")
        return False  # Error occurred during the check
    
# Getting the sender score

def get_sender_score(email):
    try:
        # Extract the domain part of the email address
        domain = email.split('@')[1]
        
        # Perform a DNS query to get the IP address of the domain
        answers = dns.resolver.query(domain, 'A')
        ip_address = answers[0].address
        print(ip_address)

        # Get the Sender Score using the senderscore module
        score = senderscore.get_score(ip_address)
        return score
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

# SPF Record Check
    
def check_spf_record(email, max_retries=3):
    retries = 0
    # Extract the domain part of the email address
    domain = email.split('@')[1]    
    while retries < max_retries:
        try:
            # Perform a DNS query to retrieve the SPF record of the domain
            spf_records = dns.resolver.query(domain, 'TXT')
            
            # Check if any TXT record starts with 'v=spf1', indicating an SPF record
            for spf_record in spf_records:
                if spf_record.strings[0].decode().startswith('v=spf1'):
                    return True
            
            # If no SPF record found, return False
            return False
        
        except dns.resolver.NXDOMAIN:
            return False
        except dns.resolver.Timeout:
            retries += 1
            if retries < max_retries:
                print(f"DNS query timed out. Retrying... (Attempt {retries + 1}/{max_retries})")
            else:
                print("Max retries reached. Unable to check SPF record.")
                return False
        except Exception as e:
            print(f"Error occurred: {e}")
            return False
        
# Checking DMARC Record:

def check_dmarc_record(email, max_retries=3):
    retries = 0
    # Extract the domain part of the email address
    domain = email.split('@')[1] 
    while retries < max_retries:
        try:
            # Perform a DNS query to retrieve the DMARC record of the domain
            dmarc_records = dns.resolver.query(f'_dmarc.{domain}', 'TXT')
            
            # If any DMARC record found, return True
            for dmarc_record in dmarc_records:
                return True
            
            # If no DMARC record found, return False
            return False
        
        except dns.resolver.NXDOMAIN:
            return False
        except dns.resolver.Timeout:
            retries += 1
            if retries < max_retries:
                print(f"DNS query timed out. Retrying... (Attempt {retries + 1}/{max_retries})")
            else:
                print("Max retries reached. Unable to check DMARC record.")
                return False
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