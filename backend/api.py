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
    is_domain_ip_blacklisted = func.is_domain_ip_blacklisted(email)
    domain_name = func.domain_name(email)
    sender_score = func.get_sender_score(email)
    check_spf_record = func.check_spf_record(email)
    check_dmarc_record = func.check_dmarc_record(email)
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
    is_valid_syntax = func.is_valid_syntax(email)
    domain_exists = func.domain_exists(email)
    domain_name = func.domain_name(email)
    has_mx_records = func.has_mx_records(email)
    get_mx_record = func.get_mx_record(email)
    is_disposable_email = func.is_disposable_email(email, disposable_domains)
    role_based = func.is_role_based_email(email, role_based_usernames)
    is_domain_ip_blacklisted = func.is_domain_ip_blacklisted(email)
    # is_greylisting_enabled = func.is_greylisting_enabled(email)
    is_microsoft_email = func.is_microsoft_email(email)
    # Prepare verification result
    verification_result = {
        'email': email,
        'domain': domain_name,
        'is_valid_syntax': is_valid_syntax,
        'domain_exists': domain_exists,
        'has_mx_records': has_mx_records,
        'mx_record': get_mx_record,
        'is_disposable_email': is_disposable_email,
        'is_role_based_email': role_based,
        'is_domain_ip_blacklisted': is_domain_ip_blacklisted,
        'is_microsoft_email': is_microsoft_email,
    }
    return jsonify(verification_result)