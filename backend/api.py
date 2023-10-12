# This file has functions for API endpoints

from flask import Flask, jsonify, request
import func
import fetch
import pandas as pd
import csv
import mysql.connector
import random
import string


# Loading a list of disposable domains

def load_disposable_domains(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return set(line.strip() for line in file)
    except Exception as e:
        print(f"Error loading file: {e}")
        return set()

disposable_domains = load_disposable_domains('./lists/disposable_email_blocklist.txt')

# Loading a list of role-based usernames

def load_role_based_usernames(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return set(line.strip() for line in file)
    except Exception as e:
        print(f"Error loading file: {e}")
        return set()

role_based_usernames = load_role_based_usernames('./lists/role_based_usernames.txt')

# Basic Endpoint
def basic():
    return jsonify(message="This API works just fine!")

def sender_status(email):
    records = fetch.fetch_records(email)
    is_domain_ip_blacklisted = func.is_domain_ip_blacklisted(records)
    domain_name = func.domain_name(email)
    sender_score = func.get_sender_score(records)
    check_spf_record = func.check_spf_record(records)
    check_dmarc_record = func.check_dmarc_record(records)
    get_ssl_certificate_info = func.get_ssl_certificate_info(email)
    verification_result = {
        'email': email,
        'domain': domain_name,
        'is_domain_ip_blacklisted': is_domain_ip_blacklisted,
        'sender_score': sender_score,
        'spf_record': check_spf_record,
        'dmarc_record': check_dmarc_record,
        'ssl_info': get_ssl_certificate_info,
    }
    return jsonify(verification_result)

def single_email(email):
    records = fetch.fetch_records(email)
    is_valid_syntax = func.is_valid_syntax(email)
    domain_exists = func.domain_exists(records)
    domain_name = func.domain_name(email)
    has_mx_records = func.has_mx_records(email, records)
    mx_records = func.mx_records(records)
    is_disposable_email = func.is_disposable_email(email, disposable_domains)
    role_based = func.is_role_based_email(email, role_based_usernames)
    is_domain_ip_blacklisted = func.is_domain_ip_blacklisted(records)
    is_microsoft_email = func.is_microsoft_email(records)
    # Prepare verification result
    verification_result = {
        'email': email,
        'domain': domain_name,
        'is_valid_syntax': is_valid_syntax,
        'domain_exists': domain_exists,
        'has_mx_records': has_mx_records,
        'mx_records': mx_records,
        'is_disposable_email': is_disposable_email,
        'is_role_based_email': role_based,
        'is_domain_ip_blacklisted': is_domain_ip_blacklisted,
        'is_microsoft_email': is_microsoft_email,
    }
    return jsonify(verification_result)

def fetch_records(email):
    records = fetch.fetch_records(email)
    verification_result = {
        'email': email,
        'records': records,
    }
    return jsonify(verification_result)