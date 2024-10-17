######################################################################################################
# This script is used to validate the format of FASTA files.
# It is designed to be used in NGS genotyping pipelines.
# The script utilizes Streamlit to provide a web interface for the end-user.
# To run the script, use the command: #"python -m streamlit run fasta_checker.py"
# This script was developed and tested by Eslam Ibrahim (Eslam.ibrahim@anu.edu.au) on OCT. 10, 2024.
######################################################################################################

import streamlit as st
import pandas as pd
import chardet  # For automatic encoding detection
from Bio import SeqIO

issue_num = 0
#=====================================
# A function to check for non-ASCII characters in sequence headers
def check_non_ascii(file_content):
    issues = []
    lines = file_content.splitlines()
    line_num = 1  # Start with the first line


    for line in lines:
        if line.startswith(">"):
            for idx, char in enumerate(line):
                if ord(char) > 127:  # ASCII characters have values from 0 to 127
                    global issue_num
                    issue_num += 1
                    issues.append({
                        'Issue Number': issue_num,
                        'Line Number': line_num,
                        'Issue': f"Invalid character in sequence header: '{char}' at position {idx + 1}"
                    })
        line_num += 1  # Move to the next line number
    return issues  
#=====================================
# Function to check that sequences contain only A, T, C, G, N
# Spaces and tabs will not be reported here, only checked in check_gaps
def check_valid_sequence(file_content):
    issues = []
    lines = file_content.splitlines()
    line_num = 1  # Start with the first line

    for line in lines:
        if line.startswith(">") or not line.strip():  # Ignore headers and blank lines
            line_num += 1
            continue
        
        sequence = line.strip().replace(" ", "").replace("\t", "")  # Clean the sequence

        for idx, char in enumerate(sequence):
            if char not in "AaTtCcGgNn":  # Check for valid characters
                global issue_num
                issue_num += 1
                issues.append({
                    'Issue Number': issue_num,
                    'Line Number': line_num,
                    'Issue': f"Invalid character in sequence: '{char}' at position {idx + 1}"
                })
        
        line_num += 1  # Move to the next line number

    return issues
#=====================================
# Function to check for gaps (spaces or tabs) within sequences
def check_gaps(file_content):
    issues = []
    lines = file_content.splitlines()
    line_num = 1  # Start with the first line

    for line in lines:
        if line.startswith(">") or not line.strip():  # Ignore headers and blank lines
            line_num += 1
            continue

        if " " in line or "\t" in line:
            global issue_num
            issue_num += 1
            issues.append({
                'Issue Number': issue_num,
                'Line Number': line_num,
                'Issue': "Gap (space or tab) in sequence"
            })
        
        line_num += 1  # Move to the next line number

    return issues
#=====================================
# Function to check for blank lines
def check_blank_lines(file_content):
    issues = []
    lines = file_content.splitlines()
    line_num = 1  # Start with the first line

    for line in lines:
        if not line.strip():  # Blank line
            global issue_num
            issue_num += 1
            issues.append({
                'Issue Number': issue_num,
                'Line Number': line_num,
                'Issue': "Blank line found"
            })
        line_num += 1  # Move to the next line number
    return issues
#=====================================
# Main function to check all issues in the file
def check_file(file_content):
    issues = []
    issues.extend(check_non_ascii(file_content))
    issues.extend(check_valid_sequence(file_content))
    issues.extend(check_gaps(file_content))
    issues.extend(check_blank_lines(file_content))
    return issues   
#=====================================
# Streamlit UI
st.title("FASTA/Text File Quality Checker")
st.write("Upload a file to check for issues such as non-ASCII characters, sequence validity, gaps, and blank lines.")

uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
    # Read the raw file
    rawfile = uploaded_file.read()
    
    # Detect encoding and Decode the file content
    result = chardet.detect(rawfile)
    charenc = result['encoding']
    file_content = rawfile.decode(charenc)
    
    # Check for issues in the file content
    issues = check_file(file_content)
    
    if issues:
        # Create DataFrame and sort by Line Number if necessary
        df = pd.DataFrame(issues)
        # df = df.sort_values(by="Line Number")  # Uncomment if you want to sort by line number
        
        # Count the number of issues found
        issue_num = len(issues)
        
        # Display the number of issues found and the table with custom size
        st.write(f"There are {issue_num} issues found in the file:")
        st.dataframe(df, height=600, width=1000)  # Increase table size
    else:
        st.write("No issues found. The file is valid.")

