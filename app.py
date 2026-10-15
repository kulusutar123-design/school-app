import os
import base64
import json
import uuid
import hashlib
import smtplib
from email.mime.text import MIMEText
from typing import Optional

from fastapi import FastAPI, Form, File, UploadFile, Request
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# ----------------- PAYU HASH GENERATOR -----------------
def get_payu_hash(key, salt, txnid, amount, productinfo, firstname, email):
    hash_string = f"{key}|{txnid}|{amount}|{productinfo}|{firstname}|{email}|||||||||||{salt}"
    return hashlib.sha512(hash_string.encode('utf-8')).hexdigest()

# ----------------- REAL EMAIL OTP SENDER -----------------
def send_real_otp_email(to_email, otp, admin_email="admin@school.com"):
    try:
        sender_email = "admin_mail@gmail.com" 
        app_password = "nlsedpbxnvoayspt" 
        msg = MIMEText(f"Namaskar,\n\nYour OTP for School Portal Registration is: {otp}\n\nPlease enter this to verify your email.\n\nThank you.")
        msg['Subject'] = 'School Portal Verification OTP'
        msg['From'] = "School Admin"
        msg['To'] = to_email
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(sender_email, app_password)
        s.sendmail(sender_email, [to_email], msg.as_string())
        s.quit()
    except Exception as e:
        print("Email sending failed:", str(e))

# ----------------- BOARD AUTO-FETCH DATABASE (All 42 Students Safe) -----------------
BOARD_DB = {
    "175CB0077": {"st_name": "ADYASHA SAHOO", "gender": "Female", "mother_name": "MAMATARANI SAHU", "father_name": "UTTAM KUMAR SAHOO", "dob": "2011-03-20", "pen_no": "21333578409", "apar_id": "340630618949", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "87"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "81"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "92"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "69"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "73"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "66"}}},
    "175CB0078": {"st_name": "ALOKTIKA MISHRA", "gender": "Female", "mother_name": "SAROJINI MISHRA", "father_name": "DEBASIS MISHRA", "dob": "2011-02-14", "pen_no": "21182142821", "apar_id": "704082184322", "category": "GENERAL", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "90"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "67"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "86"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "66"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "70"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "67"}}},
    "175CB0079": {"st_name": "ABHILIPSHA DAS", "gender": "Female", "mother_name": "JALPANA DAS", "father_name": "HIMANSHU BHUSHAN DAS", "dob": "2010-02-11", "pen_no": "21349438955", "apar_id": "NA", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "46"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "34"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "38"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "30"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "39"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "43"}}},
    "175CB0080": {"st_name": "BAISAKHI SAMAL", "gender": "Female", "mother_name": "CHANCHALA SAMAL", "father_name": "SUDHAKAR SAMAL", "dob": "2010-12-26", "pen_no": "21041084790", "apar_id": "789783065343", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "87"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "72"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "81"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "57"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "61"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "62"}}},
    "175CB0081": {"st_name": "BARSHA PRIYADARSHANI MOHANTY", "gender": "Female", "mother_name": "SUBHADRA MOHANTY", "father_name": "PURNA CHANDRA MOHANTY", "dob": "2010-10-01", "pen_no": "21498662821", "apar_id": "913475687849", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "60"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "45"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "58"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "30"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "34"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "41"}}},
    "175CB0082": {"st_name": "BARSHARANI KHILAR", "gender": "Female", "mother_name": "SANDHYARANI KHILAR", "father_name": "SANTOSH KHILAR", "dob": "2011-03-12", "pen_no": "21050451252", "apar_id": "252741731402", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "30"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "33"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "39"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "38"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "30"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "34"}}},
    "175CB0083": {"st_name": "BHAGYASHREE MOHANTY", "gender": "Female", "mother_name": "RASHMITA MOHANTY", "father_name": "ARUN KUMAR MOHANTY", "dob": "2009-10-11", "pen_no": "21082361081", "apar_id": "642970156338", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "41"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "38"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "32"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "38"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "36"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "37"}}},
    "175CB0084": {"st_name": "DIPTI MAYEE SETHY", "gender": "Female", "mother_name": "BUNI SETHY", "father_name": "SANJAY SETHY", "dob": "2011-01-11", "pen_no": "21025149546", "apar_id": "503511373905", "category": "SC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "45"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "32"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "38"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "30"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "30"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "38"}}},
    "175CB0085": {"st_name": "HARAPRIYA LENKA", "gender": "Female", "mother_name": "SARASWATI LENKA", "father_name": "NILAMANI LENKA", "dob": "2010-11-27", "pen_no": "21264457196", "apar_id": "922843423885", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "64"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "51"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "76"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "34"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "50"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "53"}}},
    "175CB0086": {"st_name": "JOSODA PARIDA", "gender": "Female", "mother_name": "GAURIBALA PARIDA", "father_name": "SURENDRA PARIDA", "dob": "2011-04-01", "pen_no": "21697711277", "apar_id": "618622215960", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "73"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "40"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "60"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "31"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "39"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "57"}}},
    "175CB0087": {"st_name": "JYOTI SWORUPA PADHI", "gender": "Female", "mother_name": "PURNIMA PADHI", "father_name": "SUDHANSHU SEKHAR PADHI", "dob": "2010-09-19", "pen_no": "NA", "apar_id": "135620099184", "category": "GENERAL", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "62"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "43"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "59"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "39"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "39"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "46"}}},
    "175CB0088": {"st_name": "JYOTSHNA RANI BISWAL", "gender": "Female", "mother_name": "PRATIMA BISWAL", "father_name": "SRABAN KUMAR BISWAL", "dob": "2010-10-13", "pen_no": "21067317375", "apar_id": "904172854667", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "74"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "62"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "77"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "41"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "48"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "64"}}},
    "175CB0089": {"st_name": "LIPA JENA", "gender": "Female", "mother_name": "MAMATA JENA", "father_name": "MANMATH JENA", "dob": "2010-05-14", "pen_no": "21109012923", "apar_id": "593617329877", "category": "SC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "86"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "72"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "82"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "58"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "64"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "67"}}},
    "175CB0090": {"st_name": "LIJA JENA", "gender": "Female", "mother_name": "MILI JENA", "father_name": "BASANTA JENA", "dob": "2011-09-29", "pen_no": "23364745896", "apar_id": "184265815264", "category": "SC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "28"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "29"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "31"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "31"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "29"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "38"}}},
    "175CB0091": {"st_name": "LIZA PADHI", "gender": "Female", "mother_name": "RANJITA PADHI", "father_name": "RATNAKAR PADHI", "dob": "2010-09-18", "pen_no": "21064948534", "apar_id": "777043813613", "category": "GENERAL", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "70"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "53"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "62"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "42"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "52"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "52"}}},
    "175CB0092": {"st_name": "LOVELY PALAI", "gender": "Female", "mother_name": "JHUNARANI PALAI", "father_name": "PRATAP PALAI", "dob": "2010-05-25", "pen_no": "21311696258", "apar_id": "671413877266", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "48"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "38"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "50"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "32"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "32"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "42"}}},
    "175CB0093": {"st_name": "MANISHA SETHY", "gender": "Female", "mother_name": "PURNIMA SETHY", "father_name": "SUSANTA SETHY", "dob": "2010-09-12", "pen_no": "21106762170", "apar_id": "611657596631", "category": "SC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "37"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "32"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "38"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "34"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "30"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "38"}}},
    "175CB0094": {"st_name": "MANISHA JENA", "gender": "Female", "mother_name": "SUBHASMITA JENA", "father_name": "DILLIP JENA", "dob": "2010-05-01", "pen_no": "21025888551", "apar_id": "270710056668", "category": "SC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "74"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "55"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "65"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "43"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "51"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "54"}}},
    "175CB0095": {"st_name": "MITASHREE JENA", "gender": "Female", "mother_name": "ANAPURNNA JENA", "father_name": "KHAGESWAR JENA", "dob": "2011-04-06", "pen_no": "21050476279", "apar_id": "790335617395", "category": "SC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "52"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "40"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "58"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "33"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "40"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "43"}}},
    "175CB0096": {"st_name": "PRIYANKA PRIYADARSHINI SAMAL", "gender": "Female", "mother_name": "SNEHANJALI SAMAL", "father_name": "MANGARAJ SAMAL", "dob": "2010-04-25", "pen_no": "21347860819", "apar_id": "284100557411", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "48"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "40"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "44"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "32"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "41"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "35"}}},
    "175CB0097": {"st_name": "PUJARANI MOHANTY", "gender": "Female", "mother_name": "DEBAKI MOHANTY", "father_name": "AMAR KUMAR MOHANTY", "dob": "2011-06-08", "pen_no": "21086864465", "apar_id": "408019175598", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "66"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "56"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "86"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "30"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "42"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "49"}}},
    "175CB0098": {"st_name": "PUJARANI PRUSTY", "gender": "Female", "mother_name": "SASMITA PRUSTY", "father_name": "RABINDRA PRUSTY", "dob": "2011-03-22", "pen_no": "21264956198", "apar_id": "360893477685", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "67"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "58"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "72"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "35"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "43"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "56"}}},
    "175CB0099": {"st_name": "PURBASHA PARIDA", "gender": "Female", "mother_name": "JHARANA PARIDA", "father_name": "HARINARAYAN PARIDA", "dob": "2010-02-11", "pen_no": "21229203899", "apar_id": "734196300420", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "70"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "41"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "59"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "38"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "38"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "54"}}},
    "175CB0100": {"st_name": "RANI JENA", "gender": "Female", "mother_name": "KUMUDINI JENA", "father_name": "RABINDRA JENA", "dob": "2010-11-18", "pen_no": "21421573731", "apar_id": "701239984481", "category": "SC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "48"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "46"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "48"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "33"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "33"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "37"}}},
    "175CB0101": {"st_name": "RADHA RANI BEHERA", "gender": "Female", "mother_name": "TAPASWINI BEHERA", "father_name": "DEBENDRA NATH BEHERA", "dob": "2011-03-08", "pen_no": "21402389757", "apar_id": "724381829344", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "75"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "68"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "77"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "40"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "43"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "57"}}},
    "175CB0102": {"st_name": "RASHMIREKHA DAS", "gender": "Female", "mother_name": "SASMITA DAS", "father_name": "NRUSINGHA DAS", "dob": "2010-12-05", "pen_no": "21050388749", "apar_id": "919157141678", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "76"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "62"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "80"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "37"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "50"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "62"}}},
    "175CB0103": {"st_name": "RINU MOHANTY", "gender": "Female", "mother_name": "MANORAMA MOHANTY", "father_name": "SIBA MOHANTY", "dob": "2010-08-15", "pen_no": "21558866778", "apar_id": "161232284559", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "70"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "55"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "74"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "38"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "43"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "53"}}},
    "175CB0104": {"st_name": "ROJALIN PANDA", "gender": "Female", "mother_name": "RANJITA PANDA", "father_name": "PRATAP KUMAR PANDA", "dob": "2010-07-17", "pen_no": "21197126707", "apar_id": "486947073442", "category": "GENERAL", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "84"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "69"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "82"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "48"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "63"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "57"}}},
    "175CB0105": {"st_name": "SAROJINI BEHERA", "gender": "Female", "mother_name": "MEERARANI BEHERA", "father_name": "MADAN BEHERA", "dob": "2010-12-25", "pen_no": "21024509156", "apar_id": "377751563500", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "51"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "35"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "48"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "38"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "34"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "34"}}},
    "175CB0106": {"st_name": "SHRABANI SAHOO", "gender": "Female", "mother_name": "DIPALI SAHOO", "father_name": "BIDYADHAR SAHOO", "dob": "2010-07-29", "pen_no": "21031034330", "apar_id": "536352323335", "category": "GENERAL", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "81"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "73"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "84"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "77"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "54"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "58"}}},
    "175CB0107": {"st_name": "SHRIYA PARIDA", "gender": "Female", "mother_name": "JYOTSNARANI PARIDA", "father_name": "ASHOK KUMAR PARIDA", "dob": "2010-06-04", "pen_no": "21704868439", "apar_id": "833200620741", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "64"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "38"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "62"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "31"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "31"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "46"}}},
    "175CB0108": {"st_name": "SMRUTIREKHA KHILLAR", "gender": "Female", "mother_name": "SABITA KHILLAR", "father_name": "CHHABINDRA KHILLAR", "dob": "2011-03-08", "pen_no": "21515201906", "apar_id": "856403020289", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "42"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "44"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "40"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "38"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "37"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "39"}}},
    "175CB0109": {"st_name": "SMRUTIREKHA SAHOO", "gender": "Female", "mother_name": "PRAMILA SAHOO", "father_name": "BIJAY KUMAR SAHOO", "dob": "2009-11-09", "pen_no": "21158801854", "apar_id": "845483054020", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "82"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "69"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "75"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "54"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "56"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "62"}}},
    "175CB0110": {"st_name": "SRUTINGYA KHILAR", "gender": "Female", "mother_name": "SABITRI KHILAR", "father_name": "BISWANATH KHILAR", "dob": "2010-12-09", "pen_no": "21013751501", "apar_id": "240564234821", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "82"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "71"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "94"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "66"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "65"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "80"}}},
    "175CB0111": {"st_name": "SUBHADRA BEHERA", "gender": "Female", "mother_name": "REENARANI BEHERA", "father_name": "AJAYA BEHERA", "dob": "2011-03-13", "pen_no": "21697498328", "apar_id": "346161684808", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "67"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "66"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "74"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "44"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "52"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "65"}}},
    "175CB0112": {"st_name": "SUBHASMITA PANDA", "gender": "Female", "mother_name": "HEMALATA PANDA", "father_name": "NARAYAN PANDA", "dob": "2010-09-07", "pen_no": "21013361804", "apar_id": "549518813294", "category": "GENERAL", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "66"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "52"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "56"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "31"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "44"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "51"}}},
    "175CB0113": {"st_name": "SHUBHASMITA SAMANTA", "gender": "Female", "mother_name": "SASMITA SAMANTA", "father_name": "BHASKAR CHANDRA SAMANTA", "dob": "2010-02-26", "pen_no": "21077897450", "apar_id": "939307473716", "category": "GENERAL", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "57"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "42"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "56"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "31"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "38"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "50"}}},
    "175CB0114": {"st_name": "SWAPNARANI PARIDA", "gender": "Female", "mother_name": "RADHARANI PARIDA", "father_name": "HAREKRUSHNA PARIDA", "dob": "2010-12-21", "pen_no": "21060625257", "apar_id": "807530411559", "category": "GENERAL", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "61"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "50"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "69"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "34"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "46"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "62"}}},
    "175CB0115": {"st_name": "SWOPNA JENA", "gender": "Female", "mother_name": "BASANTI JENA", "father_name": "MUKTIKANTA JENA", "dob": "2010-08-09", "pen_no": "21073087895", "apar_id": "795235253070", "category": "SC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "35"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "32"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "31"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "32"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "34"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "34"}}},
    "175CB0116": {"st_name": "TRUPTI REKHA BARIK", "gender": "Female", "mother_name": "RANJULATA BARIK", "father_name": "RABINDRA BARIK", "dob": "2010-02-01", "pen_no": "21358384708", "apar_id": "393771061550", "category": "SEBC", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "62"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "45"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "57"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "38"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "40"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "42"}}},
    "175CB0117": {"st_name": "UME SALMA", "gender": "Female", "mother_name": "FAIJUN NESHA", "father_name": "SHAH MD QUAMRUDDIN", "dob": "2010-04-19", "pen_no": "21354154825", "apar_id": "156117659572", "category": "GENERAL", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLU": {"name": "FIRST LANGUAGE URDU", "full": "100", "sec": "60"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "55"}, "TLH": {"name": "THIRD LANGUAGE HINDI", "full": "100", "sec": "48"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "33"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "42"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "48"}}},
    "175CB0118": {"st_name": "YANJYASENI DAS", "gender": "Female", "mother_name": "KABITA BEHURIA", "father_name": "SUSANTA DAS", "dob": "2010-11-01", "pen_no": "21072379693", "apar_id": "147250355555", "category": "GENERAL", "aadhaar": "[Aadhaar Redacted]", "subjects": {"FLO": {"name": "FIRST LANGUAGE ODIA", "full": "100", "sec": "38"}, "SLE": {"name": "SECOND LANGUAGE ENGLISH", "full": "100", "sec": "30"}, "TLS": {"name": "THIRD LANGUAGE SANSKRIT", "full": "100", "sec": "38"}, "MTH": {"name": "MATHEMATICS", "full": "100", "sec": "32"}, "GSC": {"name": "GENERAL SCIENCE", "full": "100", "sec": "35"}, "SSC": {"name": "SOCIAL SCIENCE", "full": "100", "sec": "34"}}}
}

# ----------------- DATABASE SETUP -----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE_1 = os.path.join(BASE_DIR, "school_db.json")
DB_FILE_2 = "/home/school_db.json"  

def load_db():
    data = None
    if os.path.exists(DB_FILE_1):
        try:
            with open(DB_FILE_1, "r") as f: data = json.load(f)
        except: pass
    if not data and os.path.exists(DB_FILE_2):
        try:
            with open(DB_FILE_2, "r") as f: data = json.load(f)
        except: pass
    if not data:
        data = {"admin_data": {}, "home_settings": {}, "schools": [], "students": [], "temp_regs": {}, "cert_requests": []}
    
    ad = data["admin_data"]
    for k in ["username", "password", "email", "mobile", "upi_id", "payu_merchant_id", "payu_salt", "paytm_mid", "paytm_key", "instamojo_api_key", "instamojo_auth_token", "reg_fee"]:
        if k not in ad: ad[k] = ""
    if not ad["username"]: ad["username"] = "admin"
    if not ad["password"]: ad["password"] = "123"
    
    hs = data["home_settings"]
    if "notice" not in hs: hs["notice"] = "Welcome! New Registration is Open for 2026."
    if "notice_link_text" not in hs: hs["notice_link_text"] = "Click here for latest updates"
    if "notice_link_url" not in hs: hs["notice_link_url"] = "https://www.kulusutar.in"
    if "bg_image" not in hs: hs["bg_image"] = "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?q=80&w=1920&auto=format&fit=crop"

    if "students" not in data: data["students"] = []
    if "temp_regs" not in data: data["temp_regs"] = {}
    if "schools" not in data: data["schools"] = []
    if "cert_requests" not in data: data["cert_requests"] = []
    return data

db = load_db()
admin_data = db["admin_data"]
home_settings = db["home_settings"]
schools = db["schools"]
students = db["students"]
temp_regs = db["temp_regs"]
cert_requests = db.get("cert_requests", [])

def save_db():
    try:
        with open(DB_FILE_1, "w") as f: json.dump(db, f)
    except: pass
    try:
        with open(DB_FILE_2, "w") as f: json.dump(db, f)
    except: pass

states_list = ["Andaman and Nicobar Islands", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chandigarh", "Chhattisgarh", "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Jharkhand", "Karnataka", "Kerala", "Ladakh", "Lakshadweep", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Puducherry", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"]
blood_groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
categories = ["General", "OBC", "SEBC", "SC", "ST"]
classes_list = ["Class I", "Class II", "Class III", "Class IV", "Class V", "Class VI", "Class VII", "Class VIII", "Class IX", "Class X", "X Pass Out"]
languages_list = ["Odia", "Hindi", "English", "Telugu", "Bengali", "Marathi", "Gujarati", "Tamil", "Urdu", "Kannada", "Malayalam", "Punjabi", "Sanskrit"]

# ----------------- HTML STRINGS -----------------
H_BODY = "margin:0; font-family:sans-serif; display:flex; flex-direction:column; color:#fff;"
H_BOX = "background:white; padding:30px; border-radius:10px; box-shadow:0 4px 10px rgba(0,0,0,0.1); width:400px; text-align:center;"
H_INP = "width:100%; padding:10px; margin-bottom:15px; border:1px solid #ccc; border-radius:5px;"
H_BTN = "width:100%; padding:12px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;"

def get_header(title, bg_image=None):
    bg_style = f"background-image: url('{bg_image}'); background-size: cover; background-position: center; background-attachment: fixed;" if bg_image else "background:#f4f6f9;"
    return f"<html><head><title>{title}</title><style>body{{margin:0; font-family:Arial; {bg_style}}} .content{{margin-left:260px; padding:20px; min-height:100vh; background:rgba(255,255,255,0.85);}} .box{{background:white; padding:20px; border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,0.1);}} input, select{{padding:8px; margin-bottom:10px; border:1px solid #ccc; border-radius:4px; width:100%; box-sizing:border-box;}} .btn{{padding:8px 12px; border:none; border-radius:5px; color:white; font-weight:bold; cursor:pointer; text-decoration:none; display:inline-block; font-size:13px;}} .grid-2{{display:grid; grid-template-columns:1fr 1fr; gap:15px;}} table{{width:100%; border-collapse:collapse;}} th, td{{padding:10px; border-bottom:1px solid #ddd; text-align:left;}} th{{background:#0d47a1; color:white;}}</style></head><body>"

def render_admin_sidebar(active):
    p_schools = sum(1 for s in schools if s.get("status") == "Inactive")
    not_s = f" <span style='background:red; color:white; border-radius:50%; padding:2px 6px; font-size:10px;'>{p_schools}</span>" if p_schools>0 else ""
    return f"<div style='width:260px; background:#2c3e50; height:100vh; position:fixed; overflow-y:auto; border-right:1px solid #ccc; padding-top:20px; z-index:100;'><div style='text-align:center; margin-bottom:20px;'><h3 style='color:#f1c40f; margin:0;'>KULU SUTAR</h3><p style='color:white; font-size:12px; margin:5px 0;'>Admin Panel</p></div><a href='/dashboard' style='display:block; padding:12px 20px; text-decoration:none; color:white; background: {'#34495e' if active=='dash' else 'transparent'};'>📊 Dashboard</a><a href='/school-management' style='display:block; padding:12px 20px; text-decoration:none; color:white; background: {'#34495e' if active=='school' else 'transparent'};'>🏫 School Mgt {not_s}</a><a href='/admin-manage-students' style='display:block; padding:12px 20px; text-decoration:none; color:white; background: {'#34495e' if active=='students' else 'transparent'};'>🎓 Manage Students</a><a href='/home-ground-setup' style='display:block; padding:12px 20px; text-decoration:none; color:white; background: {'#34495e' if active=='home' else 'transparent'};'>🖼️ Home Ground Setup</a><a href='/payment' style='display:block; padding:12px 20px; text-decoration:none; color:white; background: {'#34495e' if active=='pay' else 'transparent'};'>💳 Payment Settings</a><a href='/profile' style='display:block; padding:12px 20px; text-decoration:none; color:white; background: {'#34495e' if active=='prof' else 'transparent'};'>👤 Manage Profile</a><a href='/' style='display:block; padding:10px; text-decoration:none; color:white; background:#e74c3c; text-align:center; margin:20px; border-radius:5px;'>🚪 Logout</a></div>"

def render_school_sidebar(active, school_code):
    sch = next((s for s in schools if s["code"] == school_code), None)
    name = sch['name'] if sch else "School"
    p_st = sum(1 for s in students if s.get("school_code") == school_code and s.get("status") == "Pending")
    not_st = f" <span style='background:red; color:white; border-radius:50%; padding:2px 6px; font-size:10px;'>{p_st}</span>" if p_st>0 else ""
    return f"<div style='width:260px; background:#11998e; height:100vh; position:fixed; overflow-y:auto; border-right:1px solid #ccc; padding-top:20px; z-index:100;'><div style='text-align:center; margin-bottom:20px;'><h3 style='color:white; margin:0;'>{name}</h3></div><a href='/school-dashboard/{school_code}' style='display:block; padding:12px 20px; text-decoration:none; color:white; background: {'#0d7a71' if active=='dash' else 'transparent'};'>📊 Dashboard</a><a href='/school-manage-students/{school_code}' style='display:block; padding:12px 20px; text-decoration:none; color:white; background: {'#0d7a71' if active=='manage' else 'transparent'};'>📝 Manage Student {not_st}</a><a href='/school-my-students/{school_code}' style='display:block; padding:12px 20px; text-decoration:none; color:white; background: {'#0d7a71' if active=='my' else 'transparent'};'>🎓 My Students</a><a href='/school-add-student/{school_code}' style='display:block; padding:12px 20px; text-decoration:none; color:white; background: {'#0d7a71' if active=='add' else 'transparent'};'>➕ Add Student</a><a href='/school-auto-import/{school_code}' style='display:block; padding:12px 20px; text-decoration:none; color:white; background: {'#0d7a71' if active=='import' else 'transparent'};'>📥 Auto Import</a><a href='/school-cert-manage/{school_code}' style='display:block; padding:12px 20px; text-decoration:none; color:white; background: {'#0d7a71' if active=='cert_manage' else 'transparent'};'>📑 Certificate Mngt</a><a href='/' style='display:block; padding:10px; text-decoration:none; color:white; background:#e74c3c; text-align:center; margin:20px; border-radius:5px;'>🚪 Logout</a></div>"

def render_school_reg_sidebar(active):
    return f"<div style='width:260px; background:#e67e22; height:100vh; position:fixed; overflow-y:auto; border-right:1px solid #ccc; padding-top:20px; z-index:100;'><div style='text-align:center; margin-bottom:20px;'><h3 style='color:white; margin:0;'>Registration</h3><p style='color:#fdf2e9; font-size:12px; margin:5px 0;'>School Portal</p></div><a href='/school-reg-apply' style='display:block; padding:12px 20px; text-decoration:none; color:white; background: {'#d35400' if active=='apply' else 'transparent'};'>📝 Apply Registration</a><a href='/school-reg-status-check' style='display:block; padding:12px 20px; text-decoration:none; color:white; background: {'#d35400' if active=='status' else 'transparent'};'>🔎 Check Status / View</a><a href='/' style='display:block; padding:10px; text-decoration:none; color:white; background:#c0392b; text-align:center; margin:20px; border-radius:5px;'>🏠 Return Home</a></div>"

def render_student_sidebar(active):
    return f"<div class='no-print' style='width:260px; background:#8e44ad; height:100vh; position:fixed; overflow-y:auto; border-right:1px solid #ccc; padding-top:20px; z-index:100;'><div style='text-align:center; margin-bottom:20px;'><h3 style='color:white; margin:0;'>Student Portal</h3></div><a href='/student-registration' style='display:block; padding:12px 20px; text-decoration:none; color:white; background: {'#732d91' if active=='apply' else 'transparent'};'>📝 New Application</a><a href='/student-status-check' style='display:block; padding:12px 20px; text-decoration:none; color:white; background: {'#732d91' if active=='status' else 'transparent'};'>🔎 Status / Print Form</a><a href='/student-cert-apply' style='display:block; padding:12px 20px; text-decoration:none; color:white; background: {'#732d91' if active=='cert' else 'transparent'};'>📜 Apply Certificate</a><a href='/' style='display:block; padding:10px; text-decoration:none; color:white; background:#c0392b; text-align:center; margin:20px; border-radius:5px;'>🏠 Return Home</a></div>"

# ----------------- HOME ROUTES -----------------
@app.get("/", response_class=HTMLResponse)
async def home():
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>School Portal</title>
    <style>
        body {{ margin:0; font-family:sans-serif; background:url('{home_settings["bg_image"]}') no-repeat center center fixed; background-size:cover; min-height:100vh; display:flex; flex-direction:column; color:#fff; }}
        .overlay {{ background:rgba(0,20,50,0.65); min-height:100vh; display:flex; flex-direction:column; justify-content:space-between; }}
        .marquee-box {{ background:rgba(0,0,0,0.4); color:white; padding:10px; font-weight:bold; font-size:16px; border-bottom:1px solid rgba(255,255,255,0.2); }}
        .navbar {{ padding:15px 40px; border-bottom:1px solid rgba(255,255,255,0.2); }}
        .grid-container {{ display:flex; flex-wrap:wrap; justify-content:center; gap:30px; margin:40px auto; max-width:1200px; }}
        .card-wrapper {{ display:flex; flex-direction:column; align-items:center; width:170px; text-decoration:none; }}
        .circle-btn {{ width:110px; height:110px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:2.5rem; box-shadow: 0 10px 15px rgba(0,0,0,0.5), inset 0 -5px 15px rgba(0,0,0,0.3); transition: transform 0.3s, box-shadow 0.3s; margin-bottom:12px; border:2px solid rgba(255,255,255,0.5); cursor:pointer; }}
        .circle-btn:hover {{ transform: translateY(-8px); box-shadow: 0 15px 25px rgba(0,0,0,0.6), inset 0 -5px 15px rgba(0,0,0,0.3); }}
        .card-label {{ background:white; color:#0d47a1; font-weight:bold; font-size:0.9rem; padding:8px 12px; border-radius:20px; text-align:center; width:100%; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
    </style></head><body>
    <div class="overlay">
        <div class="marquee-box"><marquee>{home_settings["notice"]}</marquee></div>
        <div style="background:rgba(255,255,255,0.1); padding:10px; border-bottom:1px solid rgba(255,255,255,0.2);">
            <marquee onmouseover="this.stop();" onmouseout="this.start();">
                <a href="{home_settings["notice_link_url"]}" target="_blank" style="color:#00e5ff; font-weight:bold; font-size:18px; text-decoration:none; text-shadow: 1px 1px 3px rgba(0,0,0,0.8);">🔗 {home_settings["notice_link_text"]}</a>
            </marquee>
        </div>
        <div class="navbar"><h2>🏫 School Portal</h2></div>
        <div style="text-align:center; margin:auto 0;">
            <div class="grid-container">
                <a href="/admin-login" class="card-wrapper"><div class="circle-btn" style="background:linear-gradient(135deg, #00c6ff, #0072ff);">⚙️</div><div class="card-label">ADMIN LOGIN</div></a>
                <a href="/school-login" class="card-wrapper"><div class="circle-btn" style="background:linear-gradient(135deg, #11998e, #38ef7d);">🏫</div><div class="card-label">SCHOOL LOGIN</div></a>
                <a href="/school-reg-portal" class="card-wrapper"><div class="circle-btn" style="background:linear-gradient(135deg, #f7971e, #ffd200);">📝</div><div class="card-label">SCHOOL REGISTRATION</div></a>
                <a href="/student-registration" class="card-wrapper"><div class="circle-btn" style="background:linear-gradient(135deg, #833ab4, #fd1d1d, #fcb045);">🎓</div><div class="card-label">STUDENT REGISTRATION</div></a>
                <a href="/results-portal" class="card-wrapper"><div class="circle-btn" style="background:linear-gradient(135deg, #ff416c, #ff4b2b);">📊</div><div class="card-label">RESULTS</div></a>
                <a href="#" class="card-wrapper"><div class="circle-btn" style="background:linear-gradient(135deg, #00b4db, #0083b0);">🏅</div><div class="card-label">SCHOLARSHIP</div></a>
            </div>
        </div>
    </div></body></html>"""

@app.get("/results-portal", response_class=HTMLResponse)
async def results_portal(error: str = None):
    err = f"<p style='color:red;'>{error}</p>" if error else ""
    return f"<html><body style='background:#f4f6f9; display:flex; justify-content:center; align-items:center; height:100vh; font-family:Arial;'><div style='{H_BOX}'><h2 style='color:#ff4b2b;'>🎓 Student Results Portal</h2><p style='color:gray; font-size:14px;'>Enter details to download Marksheet</p>{err}<form action='/search-results' method='post'><input type='text' name='roll_no' placeholder='Enter Roll Number' required style='{H_INP}'><input type='date' name='dob' required style='{H_INP}'><button type='submit' style='{H_BTN} background:#ff4b2b;'>View Result & Certificate</button></form><a href='/' style='display:block; margin-top:15px; text-decoration:none; color:green; font-weight:bold;'>🏠 Back to Home</a></div></body></html>"

@app.post("/search-results", response_class=HTMLResponse)
async def search_results(roll_no: str=Form(...), dob: str=Form(...)):
    st = next((x for x in students if x.get("roll_no") == roll_no and x.get("dob") == dob), None)
    if not st: return RedirectResponse(url="/results-portal?error=Invalid Roll No or Date of Birth!", status_code=303)
    if st.get("status") != "Approved": return RedirectResponse(url="/results-portal?error=Result is pending Admin/School Approval", status_code=303)
    return RedirectResponse(url=f"/public-certificate/{st['id']}", status_code=303)

# ----------------- ADMIN LOGIN ROUTES -----------------
@app.get("/admin-login", response_class=HTMLResponse)
async def admin_login_page(error: str=None):
    err = f"<p style='color:red; text-align:center;'>{error}</p>" if error else ""
    return f"<html><body style='font-family:Arial; background:#f0f2f5; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;'><div style='background:white; padding:30px; border-radius:10px; width:300px; box-shadow:0 4px 8px rgba(0,0,0,0.1);'><h2 style='text-align:center; color:#0d6efd;'>Admin Login</h2>{err}<form action='/login' method='post'><input type='text' name='username' placeholder='Username' style='{H_INP}' required><input type='password' name='password' placeholder='Password' style='{H_INP}' required><button type='submit' style='{H_BTN} background:#0d6efd;'>Login</button></form><div style='text-align:center; margin-top:15px;'><a href='/admin-forgot' style='color:#e74c3c; font-size:13px; text-decoration:none; font-weight:bold;'>Forgot Password?</a></div><a href='/' style='display:block; text-align:center; margin-top:15px; text-decoration:none; color: green; font-weight:bold;'>🏠 Home</a></div></body></html>"

@app.post("/login", response_class=HTMLResponse)
async def login(username: str=Form(...), password: str=Form(...)):
    if username == admin_data["username"] and password == admin_data["password"]: return RedirectResponse(url="/dashboard", status_code=303)
    return RedirectResponse(url="/admin-login?error=Invalid Login", status_code=303)

@app.get("/admin-forgot", response_class=HTMLResponse)
async def admin_forgot(error: str = None):
    err = f"<p style='color:red;'>{error}</p>" if error else ""
    return f"<html><body style='background:#f4f6f9; display:flex; justify-content:center; align-items:center; height:100vh; font-family:Arial;'><div style='{H_BOX}'><h2 style='color:#0d6efd;'>Admin Forgot Password</h2>{err}<form action='/admin-forgot-submit' method='post'><input type='email' name='email' placeholder='Enter Registered Email' required style='{H_INP}'><button type='submit' style='{H_BTN} background:#0d6efd;'>Get OTP</button></form><a href='/admin-login' style='display:block; margin-top:15px; text-decoration:none; color:gray; font-weight:bold;'>⬅️ Back to Login</a></div></body></html>"

@app.post("/admin-forgot-submit", response_class=HTMLResponse)
async def admin_forgot_submit(email: str=Form(...)):
    if email == admin_data.get("email"): return RedirectResponse(url=f"/admin-reset?email={email}", status_code=303)
    return RedirectResponse(url="/admin-forgot?error=Email not registered!", status_code=303)

@app.get("/admin-reset", response_class=HTMLResponse)
async def admin_reset(email: str, error: str = None):
    err = f"<p style='color:red;'>{error}</p>" if error else ""
    return f"<html><body style='background:#f4f6f9; display:flex; justify-content:center; align-items:center; height:100vh; font-family:Arial;'><div style='{H_BOX}'><h2 style='color:#0d6efd;'>Reset Admin Password</h2><p style='font-size:14px; color:gray;'>OTP sent to {email[:3]}***<br>(Demo OTP: <b>1234</b>)</p>{err}<form action='/admin-reset-submit' method='post'><input type='hidden' name='email' value='{email}'><input type='text' name='otp' placeholder='Enter 4-Digit OTP' required style='{H_INP}'><input type='password' name='new_pass' placeholder='New Password' required style='{H_INP}'><input type='password' name='conf_pass' placeholder='Confirm Password' required style='{H_INP}'><button type='submit' style='{H_BTN} background:#27ae60;'>Reset & Save</button></form></div></body></html>"

@app.post("/admin-reset-submit", response_class=HTMLResponse)
async def admin_reset_submit(email: str=Form(...), otp: str=Form(...), new_pass: str=Form(...), conf_pass: str=Form(...)):
    if otp != "1234": return RedirectResponse(url=f"/admin-reset?email={email}&error=Invalid OTP!", status_code=303)
    if new_pass != conf_pass: return RedirectResponse(url=f"/admin-reset?email={email}&error=Passwords do not match!", status_code=303)
    admin_data["password"] = new_pass
    save_db()
    return f"<html><body style='background:#f4f6f9; display:flex; justify-content:center; align-items:center; height:100vh; font-family:Arial;'><div style='{H_BOX}'><h2 style='color:green;'>✅ Password Changed Successfully!</h2><a href='/admin-login' style='display:inline-block; margin-top:15px; padding:10px 20px; background:#0d6efd; color:white; text-decoration:none; border-radius:5px; font-weight:bold;'>Go to Login</a></div></body></html>"

# ----------------- ADMIN DASHBOARD & SETUP -----------------
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    total_sch = len(schools)
    pend_sch = sum(1 for s in schools if s.get("status") != "Active")
    total_stu = len(students)
    pend_stu = sum(1 for st in students if st.get("status") == "Pending")
    stats_html = f"<div class='grid-2' style='margin-top:20px;'><div class='box' style='border-left:5px solid #3498db;'><h3 style='margin-top:0; color:#3498db;'>🏫 Total Schools</h3><h1 style='margin:0; font-size:36px;'>{total_sch}</h1></div><div class='box' style='border-left:5px solid #e74c3c;'><h3 style='margin-top:0; color:#e74c3c;'>⚠️ Pending Schools</h3><h1 style='margin:0; font-size:36px;'>{pend_sch}</h1></div><div class='box' style='border-left:5px solid #2ecc71;'><h3 style='margin-top:0; color:#2ecc71;'>🎓 Total Students</h3><h1 style='margin:0; font-size:36px;'>{total_stu}</h1></div><div class='box' style='border-left:5px solid #f39c12;'><h3 style='margin-top:0; color:#f39c12;'>⏳ Pending Students</h3><h1 style='margin:0; font-size:36px;'>{pend_stu}</h1></div></div>"
    return get_header("Admin Dashboard") + render_admin_sidebar('dash') + f"<div class='content'><h2>Admin Dashboard</h2><p>Welcome back! Here is the overall portal status:</p>{stats_html}</div></body></html>"

@app.get("/school-management", response_class=HTMLResponse)
async def school_management():
    rows = "".join([f"<tr style='background:white;'><td>{s['name']}</td><td>{s['code']}</td><td>{s.get('pay_status','')}</td><td style='color:{'green' if s.get('status','')=='Active' else 'red'}; font-weight:bold;'>{s.get('status','')}</td><td><a href='/view-school/{s['code']}' class='btn' style='background:#8e44ad;'>👁️ View / Edit</a></td></tr>" for s in schools])
    return get_header("School Management") + render_admin_sidebar('school') + f"<div class='content'><h2>School Management</h2><table><tr><th>School Name</th><th>User ID</th><th>Payment</th><th>Status</th><th>Action</th></tr>{rows}</table></div></body></html>"

@app.get("/view-school/{code}", response_class=HTMLResponse)
async def view_school(code: str, msg: str = None):
    s = next((x for x in schools if x["code"] == code), None)
    if not s: return "Not Found"
    logo_str = f"<img src='{s['school_logo']}' style='height:40px;'>" if s.get('school_logo') else "None"
    sign_str = f"<img src='{s['hm_sign']}' style='height:30px;'>" if s.get('hm_sign') else "None"
    cert_bg_str = f"<img src='{s['cert_bg']}' style='height:40px;'>" if s.get('cert_bg') else "None"
    alert = "<div style='background:#d4edda; color:#155724; padding:10px; border-radius:5px; margin-bottom:15px; font-weight:bold; border: 1px solid #c3e6cb;'>✅ Data & Photos Saved Successfully!</div>" if msg == "saved" else ""
    return get_header("View School") + render_admin_sidebar('school') + f"""<div class='content'><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;"><h2 style="margin:0;">View School Details</h2><a href="/school-management" style="color:#0d47a1; font-weight:bold; text-decoration:none;">⬅️ Back</a></div>{alert}<div class="box"><table><tr><td><b>School Name:</b></td><td>{s.get('name','')}</td></tr><tr><td><b>Code (User ID):</b></td><td>{s.get('code','')}</td></tr><tr><td><b>Password:</b></td><td style='color:red; font-weight:bold;'>{s.get('password','')}</td></tr><tr><td><b>Headmaster:</b></td><td>{s.get('hm_name','')} (📞 {s.get('hm_mobile','')})</td></tr><tr><td><b>Address:</b></td><td>{s.get('address','')}, {s.get('state','')}</td></tr><tr><td><b>School UPI ID:</b></td><td>{s.get('school_upi','Not Set')}</td></tr><tr><td><b>Student Fee:</b></td><td>₹{s.get('student_fee','0')}</td></tr><tr><td><b>Logo / Sign / Cert BG:</b></td><td>Logo: {logo_str} &nbsp;|&nbsp; Sign: {sign_str} &nbsp;|&nbsp; Cert BG: {cert_bg_str}</td></tr><tr><td><b>Registration UTR:</b></td><td style='color:blue; font-weight:bold;'>{s.get('utr_no','Not Provided')}</td></tr></table><div style="display:flex; gap:10px; margin-top:20px;"><a href="/verify-payment/{s['code']}/Approve" class="btn" style="background:#27ae60;">✅ Approve</a><a href="/verify-payment/{s['code']}/Reject" class="btn" style="background:#f39c12;">⚠️ Reject</a><a href="/edit-school/{s['code']}" class="btn" style="background:#2980b9;">✏️ Edit Data & Setup Images</a><a href="/delete-school/{s['code']}" class="btn" style="background:#c0392b;" onclick="return confirm('Delete completely?');">🗑️ Delete</a></div></div></div></body></html>"""

@app.get("/verify-payment/{code}/{action}", response_class=HTMLResponse)
async def verify_payment(code: str, action: str):
    for s in schools:
        if s["code"] == code:
            s["pay_status"] = "Approved" if action=="Approve" else "Rejected"
            s["status"] = "Active" if action=="Approve" else "Inactive"
    save_db()
    return RedirectResponse(url=f"/view-school/{code}", status_code=303)

@app.get("/delete-school/{code}", response_class=HTMLResponse)
async def delete_school(code: str):
    global schools
    schools = [s for s in schools if s["code"] != code]
    db["schools"] = schools
    save_db()
    return RedirectResponse(url="/school-management", status_code=303)

@app.get("/edit-school/{code}", response_class=HTMLResponse)
async def edit_school(code: str):
    s = next((x for x in schools if x["code"] == code), None)
    if not s: return "Not found"
    st_opts = "".join([f"<option {'selected' if s.get('state')==st else ''}>{st}</option>" for st in states_list])
    return get_header("Edit School") + render_admin_sidebar('school') + f"""<div class='content'><h2>Edit School: {s['name']}</h2><div class='box'><form action='/update-school/{code}' method='post' enctype='multipart/form-data'><div class='grid-2'><div><label>Name</label><input type='text' name='name' value='{s.get('name','')}' required></div><div><label>Email</label><input type='email' name='email' value='{s.get('email','')}' required></div><div><label>Password</label><input type='text' name='password' value='{s.get('password','')}' required></div><div><label>HM Name</label><input type='text' name='hm_name' value='{s.get('hm_name','')}' required></div><div><label>HM Mobile</label><input type='text' name='hm_mobile' value='{s.get('hm_mobile','')}' required></div><div><label>Address</label><input type='text' name='address' value='{s.get('address','')}' required></div><div><label>State</label><select name='state'>{st_opts}</select></div></div><hr><h3 style="color:#0d47a1;">School Images & Signatures (Optional)</h3><div class='grid-2'><div><label>School Logo</label><input type='file' name='school_logo' accept='image/*'></div><div><label>Headmaster Signature</label><input type='file' name='hm_sign' accept='image/*'></div><div><label>School Dashboard Background Photo</label><input type='file' name='school_bg' accept='image/*'></div><div><label>Certificate Background Photo (A4 Size)</label><input type='file' name='cert_bg' accept='image/*'></div></div><hr><h3 style="color:#0d47a1;">Payment Settings</h3><div class='grid-2'><div><label>School UPI ID</label><input type='text' name='school_upi' value='{s.get('school_upi','')}'></div><div><label>Student Reg Fee (₹)</label><input type='number' name='student_fee' value='{s.get('student_fee','0')}'></div></div><button type='submit' class='btn' style='background:#27ae60; margin-top:15px; width:100%; font-size:16px;'>Save Changes & Photos</button></form></div></div></body></html>"""

@app.post("/update-school/{code}", response_class=HTMLResponse)
async def update_school(code: str, request: Request):
    form = await request.form()
    for s in schools:
        if s["code"] == code:
            for k in ["name", "email", "password", "hm_name", "hm_mobile", "address", "state", "school_upi", "student_fee"]:
                if form.get(k) is not None: s[k] = form.get(k)
            for img_key in ["school_logo", "hm_sign", "school_bg", "cert_bg"]:
                img_file = form.get(img_key)
                if img_file and hasattr(img_file, "filename") and img_file.filename:
                    c = await img_file.read()
                    s[img_key] = f"data:{img_file.content_type};base64,{base64.b64encode(c).decode('utf-8')}"
            break
    save_db()
    return RedirectResponse(url=f"/view-school/{code}?msg=saved", status_code=303)

@app.get("/admin-manage-students", response_class=HTMLResponse)
async def admin_manage_students():
    rows = "".join([f"<tr style='background:white;'><td>{st.get('st_name','')}</td><td>{st.get('id','')}</td><td>{st.get('school_code','')}</td><td>{st.get('pay_status','')} <br><span style='font-size:10px; color:blue;'>UTR: {st.get('utr_no','N/A')}</span></td><td><a href='/edit-student/admin/{st.get('id','')}' class='btn' style='background:#3498db;'>✏️ Form</a> <a href='/manage-marks/admin/{st.get('id','')}' class='btn' style='background:#9b59b6;'>📘 Marks</a> <a href='/certificate/admin/{st.get('id','')}' class='btn' style='background:#e67e22;'>📜 Marksheet</a> <a href='/delete-student/admin/{st.get('id','')}' class='btn' style='background:#e74c3c;' onclick='return confirm(\"Delete?\")'>🗑️</a></td></tr>" for st in students if st.get('id')])
    return get_header("Manage All Students") + render_admin_sidebar('students') + f"<div class='content'><h2>Admin: Manage All Students</h2><div class='box'><table><tr><th>Name</th><th>Student ID</th><th>School Code</th><th>Pay Status (UTR)</th><th>Actions</th></tr>{rows}</table></div></div></body></html>"

@app.get("/home-ground-setup", response_class=HTMLResponse)
async def home_ground_setup():
    nl_text = home_settings.get("notice_link_text", "Click here for latest updates")
    nl_url = home_settings.get("notice_link_url", "#")
    return get_header("Home Ground Setup") + render_admin_sidebar('home') + f"<div class='content'><h2>Home Ground Setup</h2><div class='box'><form action='/update-home-ground' method='post' enctype='multipart/form-data'><label>Main Scrolling Notice:</label><input type='text' name='notice' value='{home_settings['notice']}' required><br><label>Running Link Text (Clickable):</label><input type='text' name='notice_link_text' value='{nl_text}' required><br><label>Running Link URL (Where it opens):</label><input type='text' name='notice_link_url' value='{nl_url}' required><br><label>Background Image:</label><input type='file' name='bg_file'><br><button type='submit' class='btn' style='background:green; margin-top:10px;'>Update Home Page</button></form></div></div></body></html>"

@app.post("/update-home-ground", response_class=HTMLResponse)
async def update_home_ground(request: Request):
    form = await request.form()
    home_settings["notice"] = form.get("notice")
    home_settings["notice_link_text"] = form.get("notice_link_text")
    url = form.get("notice_link_url", "")
    if url and not url.startswith("http") and url != "#": url = "https://" + url
    home_settings["notice_link_url"] = url
    if form.get("bg_file") and getattr(form.get("bg_file"), "filename", None):
        c = await form.get("bg_file").read()
        home_settings["bg_image"] = f"data:image/jpeg;base64,{base64.b64encode(c).decode('utf-8')}"
    save_db()
    return RedirectResponse(url="/home-ground-setup", status_code=303)

@app.get("/payment", response_class=HTMLResponse)
async def payment():
    p_mid = admin_data.get('payu_merchant_id', '')
    p_salt = admin_data.get('payu_salt', '')
    ptm_mid = admin_data.get('paytm_mid', '')
    ptm_key = admin_data.get('paytm_key', '')
    i_api = admin_data.get('instamojo_api_key', '')
    i_auth = admin_data.get('instamojo_auth_token', '')
    return get_header("Payment Setup") + render_admin_sidebar('pay') + f"<div class='content'><h2>Admin Payment Settings</h2><div class='box' style='max-width:500px;'><form action='/update-payment' method='post'><label style='font-weight:bold; color:black;'>UPI ID (For Auto QR):</label><br><input type='text' name='upi' value='{admin_data.get('upi_id','')}' required><br><hr style='margin:20px 0; border:0; border-top:1px solid #ddd;'><h4 style='color:#d35400; margin-top:0;'>PayU Real Money Settings</h4><label>PayU Merchant Key:</label><input type='text' name='payu_merchant_id' value='{p_mid}' placeholder='e.g., gtKFFx'><br><label>PayU Merchant Salt (Secret):</label><input type='password' name='payu_salt' value='{p_salt}' placeholder='e.g., eCwWELxi'><br><hr style='margin:20px 0; border:0; border-top:1px solid #ddd;'><h4 style='color:#00b9f5; margin-top:0;'>Paytm Real Money Settings</h4><label>Paytm Merchant ID (MID):</label><input type='text' name='paytm_mid' value='{ptm_mid}' placeholder='Enter Paytm MID'><br><label>Paytm Merchant Key:</label><input type='password' name='paytm_key' value='{ptm_key}' placeholder='Enter Paytm Key'><br><hr style='margin:20px 0; border:0; border-top:1px solid #ddd;'><h4 style='color:#8e44ad; margin-top:0;'>Instamojo Real Money Settings</h4><label>Instamojo Private API Key:</label><input type='password' name='instamojo_api_key' value='{i_api}' placeholder='e.g., 6fa42...'><br><label>Instamojo Private Auth Token:</label><input type='password' name='instamojo_auth_token' value='{i_auth}' placeholder='e.g., 83f0b...'><br><hr style='margin:20px 0; border:0; border-top:1px solid #ddd;'><label style='font-weight:bold; color:black;'>Reg Fee (Amount to charge):</label><br><input type='text' name='reg_fee' value='{admin_data.get('reg_fee','10')}' required><br><button type='submit' class='btn' style='background:blue; width:100%; margin-top:10px; font-size:15px;'>Save All Settings</button></form></div></div></body></html>"

@app.post("/update-payment", response_class=HTMLResponse)
async def update_payment(upi: str=Form(""), reg_fee: str=Form(""), payu_merchant_id: str=Form(""), payu_salt: str=Form(""), paytm_mid: str=Form(""), paytm_key: str=Form(""), instamojo_api_key: str=Form(""), instamojo_auth_token: str=Form("")):
    admin_data["upi_id"] = upi
    admin_data["reg_fee"] = reg_fee
    admin_data["payu_merchant_id"] = payu_merchant_id
    admin_data["payu_salt"] = payu_salt
    admin_data["paytm_mid"] = paytm_mid
    admin_data["paytm_key"] = paytm_key
    admin_data["instamojo_api_key"] = instamojo_api_key
    admin_data["instamojo_auth_token"] = instamojo_auth_token
    save_db()
    return RedirectResponse(url="/payment", status_code=303)

@app.get("/profile", response_class=HTMLResponse)
async def profile():
    return get_header("Profile") + render_admin_sidebar('prof') + f"<div class='content'><h2>Manage Profile</h2><div class='box' style='max-width:400px;'><form action='/update-profile' method='post'><label>Name</label><input type='text' name='username' value='{admin_data['username']}'><label>Email</label><input type='email' name='email' value='{admin_data.get('email','')}'><label>Mobile</label><input type='text' name='mobile' value='{admin_data.get('mobile','')}'><label>New Pass</label><input type='password' name='password'><button type='submit' class='btn' style='background:green; width:100%; margin-top:10px;'>Save Changes</button></form></div></div></body></html>"

@app.post("/update-profile", response_class=HTMLResponse)
async def update_profile(username: str=Form(...), email: str=Form(...), mobile: str=Form(...), password: str=Form(None)):
    admin_data["username"] = username
    admin_data["email"] = email
    admin_data["mobile"] = mobile
    if password: admin_data["password"] = password
    save_db()
    return RedirectResponse(url="/profile", status_code=303)

# ----------------- SCHOOL LOGIN & DASHBOARD -----------------
@app.get("/school-login", response_class=HTMLResponse)
async def school_login_page(error: str = None):
    err = f"<p style='color:red; text-align:center;'>{error}</p>" if error else ""
    st_opts = "".join([f"<option value='{s}'>{s}</option>" for s in states_list])
    return f"""<html><head><script>
    let capCode=""; function genCap(){{ capCode = Math.random().toString(36).substring(2, 7).toUpperCase(); document.getElementById('capBox').innerText = capCode; document.getElementById('capIn').value=""; }} window.onload=genCap; function valLog(){{ if(document.getElementById('capIn').value.toUpperCase() !== capCode){{ alert("Invalid Captcha!"); genCap(); return false; }} return true; }}
    </script></head><body style="font-family:Arial; background:#f0f2f5; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
    <div style="background:white; padding:30px; border-radius:10px; width:300px; box-shadow:0 4px 8px rgba(0,0,0,0.1);">
        <h2 style="text-align:center; color:#11998e;">🏫 School Login</h2>{err}
        <form action="/s-login-submit" method="post">
            <select name="state" style="width:100%; padding:10px; margin-bottom:10px; border-radius:5px; border:1px solid #ccc;" required><option value="">--Select State--</option>{st_opts}</select>
            <input type="text" name="code" placeholder="School Code (User ID)" style="width:100%; padding:10px; margin-bottom:10px; border-radius:5px; border:1px solid #ccc;" required>
            <input type="password" name="password" placeholder="Password" style="width:100%; padding:10px; margin-bottom:10px; border-radius:5px; border:1px solid #ccc;" required>
            <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                <div id="capBox" style="background:#eee; padding:10px; font-weight:bold; letter-spacing:4px; font-family:monospace; width:65%; text-align:center; border-radius:5px;"></div>
                <button type="button" onclick="genCap()" style="background:#3498db; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer; font-weight:bold;">🔄</button>
            </div>
            <input type="text" id="capIn" placeholder="Enter Captcha" style="width:100%; padding:10px; margin-bottom:15px; border-radius:5px; border:1px solid #ccc;" required>
            <button type="submit" onclick="return valLog()" style="width:100%; padding:10px; background:#11998e; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">Login</button>
        </form>
        <div style="text-align:center; margin-top:15px;"><a href="/school-forgot" style="color:#e74c3c; font-size:13px; text-decoration:none; font-weight:bold;">Forgot Password?</a></div>
        <a href="/" style="display:block; text-align:center; margin-top:15px; color:green; font-weight:bold; text-decoration:none;">🏠 Home Portal</a>
    </div></body></html>"""

@app.post("/s-login-submit", response_class=HTMLResponse)
async def s_login_submit(state: str=Form(...), code: str=Form(...), password: str=Form(...)):
    for s in schools:
        if s["code"] == code and s.get("password") == password:
            if s.get("state") != state: return RedirectResponse(url="/school-login?error=State mismatch for this School ID!", status_code=303)
            if s.get("status") != "Active": return RedirectResponse(url="/school-login?error=Account is Inactive or Pending Admin Approval", status_code=303)
            return RedirectResponse(url=f"/school-dashboard/{code}", status_code=303)
    return RedirectResponse(url="/school-login?error=Invalid Code or Password", status_code=303)

@app.get("/school-forgot", response_class=HTMLResponse)
async def school_forgot(error: str = None):
    err = f"<p style='color:red;'>{error}</p>" if error else ""
    return f"<html><body style='background:#f4f6f9; display:flex; justify-content:center; align-items:center; height:100vh; font-family:Arial;'><div style='background:white; padding:30px; border-radius:10px; box-shadow:0 4px 10px rgba(0,0,0,0.1); width:350px; text-align:center;'><h2 style='color:#11998e;'>School Forgot Password</h2>{err}<form action='/school-forgot-submit' method='post'><input type='text' name='code' placeholder='Enter School Code (User ID)' required style='width:100%; padding:10px; margin-bottom:15px; border-radius:5px; border:1px solid #ccc;'><button type='submit' style='width:100%; padding:12px; background:#11998e; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;'>Find Account</button></form><a href='/school-login' style='display:block; margin-top:15px; text-decoration:none; color:gray; font-weight:bold;'>⬅️ Back to Login</a></div></body></html>"

@app.post("/school-forgot-submit", response_class=HTMLResponse)
async def school_forgot_submit(code: str=Form(...)):
    s = next((x for x in schools if x["code"] == code), None)
    if not s: return RedirectResponse(url="/school-forgot?error=School Code Not Found!", status_code=303)
    return RedirectResponse(url=f"/school-reset?code={code}", status_code=303)

@app.get("/school-reset", response_class=HTMLResponse)
async def school_reset(code: str, error: str = None):
    s = next((x for x in schools if x["code"] == code), None)
    if not s: return "Invalid Request"
    email = s.get('email', 'admin@example.com')
    masked_email = email[:3] + "****" + email[email.find("@"):] if "@" in email else email
    err = f"<p style='color:red;'>{error}</p>" if error else ""
    return f"<html><body style='background:#f4f6f9; display:flex; justify-content:center; align-items:center; height:100vh; font-family:Arial;'><div style='background:white; padding:30px; border-radius:10px; box-shadow:0 4px 10px rgba(0,0,0,0.1); width:350px; text-align:center;'><h2 style='color:#11998e;'>Reset School Password</h2><p style='font-size:14px; color:gray;'>OTP sent to {masked_email}<br>(Demo OTP: <b>1234</b>)</p>{err}<form action='/school-reset-submit' method='post'><input type='hidden' name='code' value='{code}'><input type='text' name='otp' placeholder='Enter 4-Digit OTP' required style='width:100%; padding:10px; margin-bottom:15px; border-radius:5px; border:1px solid #ccc;'><input type='password' name='new_pass' placeholder='New Password' required style='width:100%; padding:10px; margin-bottom:15px; border-radius:5px; border:1px solid #ccc;'><input type='password' name='conf_pass' placeholder='Confirm Password' required style='width:100%; padding:10px; margin-bottom:15px; border-radius:5px; border:1px solid #ccc;'><button type='submit' style='width:100%; padding:12px; background:#27ae60; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;'>Reset & Save</button></form></div></body></html>"

@app.post("/school-reset-submit", response_class=HTMLResponse)
async def school_reset_submit(code: str=Form(...), otp: str=Form(...), new_pass: str=Form(...), conf_pass: str=Form(...)):
    if otp != "1234": return RedirectResponse(url=f"/school-reset?code={code}&error=Invalid OTP!", status_code=303)
    if new_pass != conf_pass: return RedirectResponse(url=f"/school-reset?code={code}&error=Passwords do not match!", status_code=303)
    for s in schools:
        if s["code"] == code:
            s["password"] = new_pass
            break
    save_db()
    return f"<html><body style='background:#f4f6f9; display:flex; justify-content:center; align-items:center; height:100vh; font-family:Arial;'><div style='background:white; padding:40px; border-radius:10px; text-align:center;'><h2 style='color:green;'>✅ Password Changed Successfully!</h2><a href='/school-login' style='display:inline-block; margin-top:15px; padding:10px 20px; background:#11998e; color:white; text-decoration:none; border-radius:5px; font-weight:bold;'>Go to Login</a></div></body></html>"

@app.get("/school-dashboard/{code}", response_class=HTMLResponse)
async def school_dash(code: str):
    sch = next((s for s in schools if s["code"] == code), None)
    bg_img = sch.get('school_bg') if sch else None
    sch_students = [st for st in students if st.get("school_code") == code]
    total_stu = len(sch_students)
    pend_stu = sum(1 for st in sch_students if st.get("status") == "Pending")
    stats_html = f"<div class='grid-2' style='margin-top:20px;'><div class='box' style='border-left:5px solid #2ecc71;'><h3 style='margin-top:0; color:#2ecc71;'>🎓 Total Students (Registered)</h3><h1 style='margin:0; font-size:36px;'>{total_stu}</h1></div><div class='box' style='border-left:5px solid #f39c12;'><h3 style='margin-top:0; color:#f39c12;'>⏳ Pending Approvals</h3><h1 style='margin:0; font-size:36px;'>{pend_stu}</h1></div></div>"
    return get_header("School Dashboard", bg_img) + render_school_sidebar('dash', code) + f"<div class='content'><h2>School Dashboard</h2><p>Welcome to your portal! Here is your school's student data summary:</p>{stats_html}</div></body></html>"

@app.get("/school-manage-students/{code}", response_class=HTMLResponse)
async def school_manage_students(code: str):
    sch = next((s for s in schools if s["code"] == code), None)
    bg_img = sch.get('school_bg') if sch else None
    pend = [st for st in students if st.get("school_code") == code and st.get("status") == "Pending"]
    rows = "".join([f"<tr style='background:white;'><td>{st.get('st_name','')}</td><td>{st.get('roll_no','')}</td><td>{st.get('class_section','')}</td><td><span style='color:orange; font-weight:bold;'>{st.get('pay_status','Pending')}</span><br><span style='font-size:10px; color:blue;'>UTR: {st.get('utr_no','N/A')}</span></td><td><a href='/school-approve-student/{code}/{st['id']}/Approve' class='btn' style='background:#27ae60;'>Approve</a> <a href='/school-approve-student/{code}/{st['id']}/Reject' class='btn' style='background:#e74c3c;'>Reject</a> <a href='/edit-student/{code}/{st['id']}' class='btn' style='background:#f39c12;'>Edit</a> <a href='/delete-student/{code}/{st['id']}' class='btn' style='background:#c0392b;' onclick='return confirm(\"Delete?\")'>🗑️</a></td></tr>" for st in pend if st.get('id')])
    return get_header("Manage Students", bg_img) + render_school_sidebar('manage', code) + f"<div class='content'><h2>Pending Applications (Check UTR Before Approval)</h2><div class='box'><table><tr><th>Name</th><th>Roll No</th><th>Class</th><th>Pay Status (UTR)</th><th>Action</th></tr>{rows}</table></div></div></body></html>"

@app.get("/school-approve-student/{code}/{st_id}/{action}", response_class=HTMLResponse)
async def school_approve_st(code: str, st_id: str, action: str):
    for st in students:
        if st.get("id") == st_id and st.get("school_code") == code:
            st["status"] = "Approved" if action == "Approve" else "Rejected"
            st["pay_status"] = "Approved" if action == "Approve" else "Rejected"
    save_db()
    return RedirectResponse(url=f"/school-manage-students/{code}", status_code=303)

@app.get("/school-my-students/{code}", response_class=HTMLResponse)
async def school_my_students(code: str):
    sch = next((s for s in schools if s["code"] == code), None)
    bg_img = sch.get('school_bg') if sch else None
    appr = [st for st in students if st.get("school_code") == code and st.get("status") == "Approved"]
    rows = "".join([f"<tr style='background:white;'><td><img src='{st.get('photo','')}' style='width:40px;height:40px;border-radius:50%; object-fit:cover;'></td><td>{st.get('st_name','')}</td><td>{st.get('roll_no','')}</td><td>{st.get('class_section','')}</td><td><a href='/edit-student/{code}/{st['id']}' class='btn' style='background:#3498db;'>✏️ Edit</a> <a href='/manage-marks/{code}/{st['id']}' class='btn' style='background:#9b59b6;'>📘 Marks</a> <a href='/certificate/{code}/{st['id']}' class='btn' style='background:#e67e22;'>📜 Marksheet</a> <a href='/delete-student/{code}/{st['id']}' class='btn' style='background:#e74c3c;' onclick='return confirm(\"Delete?\")'>🗑️</a></td></tr>" for st in appr if st.get('id')])
    return get_header("My Students", bg_img) + render_school_sidebar('my', code) + f"<div class='content'><h2>My Students (Approved)</h2><div class='box'><table><tr><th>Photo</th><th>Name</th><th>Roll No</th><th>Class</th><th>Manage Data</th></tr>{rows}</table></div></div></body></html>"

@app.get("/school-add-student/{code}", response_class=HTMLResponse)
async def school_add_student(code: str):
    sch = next((s for s in schools if s["code"] == code), None)
    bg_img = sch.get('school_bg') if sch else None
    return get_header("Add Student", bg_img) + render_school_sidebar('add', code) + f"<div class='content'><h2>Add New Student</h2><div class='box'>{generate_18_point_form(f'/school-save-student/{code}', school_code_fixed=code)}</div></div></body></html>"

@app.post("/school-save-student/{code}", response_class=HTMLResponse)
async def school_save_student(code: str, request: Request):
    form = await request.form()
    st_id = uuid.uuid4().hex[:8].upper()
    student_data = dict(form)
    student_data["id"] = st_id
    student_data["pay_status"] = "Approved" 
    student_data["status"] = "Approved" 
    student_data["school_code"] = code
    student_data["subjects"] = {}
    photo = form.get("photo")
    if photo and hasattr(photo, "filename") and photo.filename:
        c = await photo.read()
        student_data["photo"] = f"data:{photo.content_type};base64,{base64.b64encode(c).decode('utf-8')}"
    else: student_data["photo"] = ""
    students.append(student_data)
    save_db()
    return RedirectResponse(url=f"/school-my-students/{code}", status_code=303)

@app.get("/school-auto-import/{code}", response_class=HTMLResponse)
async def school_auto_import(code: str, error: str = None):
    err = f"<p style='color:red;'>{error}</p>" if error else ""
    sch = next((s for s in schools if s["code"] == code), None)
    bg_img = sch.get('school_bg') if sch else None
    return get_header("Auto Import", bg_img) + render_school_sidebar('import', code) + f"<div class='content'><h2>Auto Import Student from Board Database</h2>{err}<div class='box' style='max-width:500px;'><form action='/process-auto-import/{code}' method='post'><label>Enter Board Roll Number (e.g., 175CB0077, 175CB0078)</label><input type='text' name='roll_no' required><button type='submit' class='btn' style='background:#8e44ad; width:100%;'>Fetch & Save Data</button></form></div></div></body></html>"

@app.post("/process-auto-import/{code}", response_class=HTMLResponse)
async def process_auto_import(code: str, request: Request):
    form = await request.form()
    roll_no = form.get("roll_no", "").strip().upper()
    if roll_no not in BOARD_DB: return RedirectResponse(url=f"/school-auto-import/{code}?error=Roll Number {roll_no} not found in Board Database!", status_code=303)
    b_data = BOARD_DB[roll_no]
    st_id = uuid.uuid4().hex[:8].upper()
    new_student = {"id": st_id, "school_code": code, "roll_no": roll_no, "st_name": b_data["st_name"], "gender": b_data["gender"], "dob": b_data["dob"], "mother_name": b_data["mother_name"], "father_name": b_data["father_name"], "pen_no": b_data["pen_no"], "apar_id": b_data["apar_id"], "category": b_data["category"], "aadhaar": b_data["aadhaar"], "class_section": "X Pass Out", "status": "Approved", "pay_status": "Approved", "subjects": b_data["subjects"], "photo": "", "mobile": "", "blood_group": "", "minority": "", "address": "", "pin_code": "", "state": "Odisha", "district": "BHADRAK", "language": "Odia", "email": ""}
    students.append(new_student)
    save_db()
    return RedirectResponse(url=f"/school-my-students/{code}", status_code=303)

# ----------------- SCHOOL REGISTRATION FLOW -----------------
@app.get("/school-reg-portal", response_class=HTMLResponse)
async def school_reg_portal():
    return get_header("School Registration Portal") + render_school_reg_sidebar('') + f"<div class='content'><h2>Welcome to School Registration Portal</h2><p>Please select an option from the sidebar to Apply or Check Status.</p></div></body></html>"

@app.get("/school-reg-apply", response_class=HTMLResponse)
async def school_reg_apply(error: str = None):
    err = f"<p style='color:red;'>{error}</p>" if error else ""
    st_opts = "".join([f"<option value='{s}'>{s}</option>" for s in states_list])
    return get_header("School Registration") + render_school_reg_sidebar('apply') + f"<div class='content'><h2>New School Registration Form</h2>{err}<div class='box'><form action='/school-reg-submit' method='post'><div class='grid-2'><div><label>School Name</label><input type='text' name='name' required></div><div><label>School Code (User ID)</label><input type='text' name='code' required></div><div><label>Email ID</label><input type='email' name='email' required></div><div><label>Headmaster Name</label><input type='text' name='hm_name' required></div><div><label>Mobile Number</label><input type='text' name='hm_mobile' required></div><div><label>Address</label><input type='text' name='address' required></div><div><label>State</label><select name='state' required><option value=''>--Select State--</option>{st_opts}</select></div><div><label>Password</label><input type='password' name='password' required></div><div><label>Confirm Password</label><input type='password' name='c_password' required></div></div><button type='submit' class='btn' style='background:#f7971e; margin-top:15px; width:100%; font-size:16px;'>Submit & Get OTP</button></form></div></div></body></html>"

@app.post("/school-reg-submit", response_class=HTMLResponse)
async def school_reg_submit(request: Request):
    form = await request.form()
    code = form.get("code")
    user_email = form.get("email")
    if form.get("password") != form.get("c_password"): return RedirectResponse(url="/school-reg-apply?error=Passwords do not match", status_code=303)
    if any(s["code"] == code for s in schools): return RedirectResponse(url="/school-reg-apply?error=School Code already exists!", status_code=303)
    
    generated_otp = str(uuid.uuid4().int)[:4] 
    temp_regs[code] = dict(form)
    temp_regs[code]["real_otp"] = generated_otp
    save_db()
    send_real_otp_email(user_email, generated_otp, admin_data.get("email"))

    return f"<html><body style='{H_BODY}'><div style='{H_BOX}'><h2 style='color:#0d47a1;'>Verify Email OTP</h2><p style='color:green; font-weight:bold;'>A Real OTP has been sent to {user_email}</p><p style='font-size:13px; color:gray;'>(For demo/testing purpose you can also use: <b>1234</b>)</p><form action='/school-verify-otp' method='post'><input type='hidden' name='code' value='{code}'><input type='text' name='otp' placeholder='Enter 4-digit OTP' required style='{H_INP}'><button type='submit' style='{H_BTN} background:#27ae60;'>Verify OTP</button></form><form action='/resend-school-otp' method='post' style='margin-top:10px;'><input type='hidden' name='code' value='{code}'><button type='submit' style='{H_BTN} background:#f39c12;'>🔄 Resend OTP</button></form></div></body></html>"

@app.post("/resend-school-otp", response_class=HTMLResponse)
async def resend_school_otp(code: str=Form(...)):
    if code in temp_regs:
        user_email = temp_regs[code].get("email", "")
        real_otp = temp_regs[code].get("real_otp", "1234")
        send_real_otp_email(user_email, real_otp, admin_data.get("email"))
        return f"<html><body style='{H_BODY}'><div style='{H_BOX}'><h2 style='color:#0d47a1;'>Verify Email OTP</h2><p style='color:green; font-weight:bold;'>✅ OTP Resent Successfully to {user_email}</p><p style='font-size:13px; color:gray;'>(Demo OTP: <b>1234</b>)</p><form action='/school-verify-otp' method='post'><input type='hidden' name='code' value='{code}'><input type='text' name='otp' placeholder='Enter 4-digit OTP' required style='{H_INP}'><button type='submit' style='{H_BTN} background:#27ae60;'>Verify OTP</button></form><form action='/resend-school-otp' method='post' style='margin-top:10px;'><input type='hidden' name='code' value='{code}'><button type='submit' style='{H_BTN} background:#f39c12;'>🔄 Resend OTP</button></form></div></body></html>"
    return "Error"

@app.post("/school-verify-otp", response_class=HTMLResponse)
async def school_verify_otp(code: str=Form(...), otp: str=Form(...)):
    if code in temp_regs:
        real_otp = temp_regs[code].get("real_otp", "1234")
        if otp == real_otp or otp == "1234":
            return f"<html><body style='{H_BODY}'><div style='{H_BOX}'><h2 style='color:#0d47a1;'>Declaration</h2><form action='/school-payment-page' method='post'><input type='hidden' name='code' value='{code}'><div style='text-align:left; background:#fff3cd; padding:15px; border-radius:5px; margin-bottom:20px; font-size:14px; border:1px solid #ffeeba;'><input type='checkbox' required id='decl'> <label for='decl'>I hereby declare that all the information submitted is correct. I understand the terms and conditions of the School Portal.</label></div><button type='submit' style='{H_BTN} background:#d35400;'>Proceed to Payment</button></form></div></body></html>"
    return "<html><body><h2 style='text-align:center; color:red;'>Invalid OTP.</h2></body></html>"

@app.post("/school-payment-page", response_class=HTMLResponse)
async def school_payment_page(request: Request, code: str=Form(...)):
    if code not in temp_regs: return "Error"
    d = temp_regs[code]
    upi = admin_data.get("upi_id", "")
    inst_key = admin_data.get("instamojo_api_key", "")
    payu_merchant = admin_data.get("payu_merchant_id", "")
    payu_salt = admin_data.get("payu_salt", "")
    paytm_mid = admin_data.get("paytm_mid", "")
    fee = admin_data.get("reg_fee", "10")
    qr = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=upi://pay?pa={upi}%26am={fee}"
    txnid = uuid.uuid4().hex[:15]
    payu_hash = get_payu_hash(payu_merchant, payu_salt, txnid, fee, "School Registration", d['name'], d['email'])
    base_url = str(request.base_url).rstrip("/").replace("http://", "https://")
    surl = f"{base_url}/payu-success-school?code={code}"
    furl = f"{base_url}/payu-failure"

    return f"""<html><head><style>body{{{H_BODY}}} .pay-box{{{H_BOX}}} .pay-tabs{{display:flex; flex-wrap:wrap; border-bottom:2px solid #ccc; margin-bottom:20px;}} .pay-tab{{flex:1; padding:8px 5px; cursor:pointer; font-weight:bold; font-size:13px; background:#eee; border-radius:5px 5px 0 0; margin-right:2px; text-align:center;}} .pay-tab.active{{background:#27ae60; color:white;}} .pay-content{{display:none; text-align:left;}} .pay-content.active{{display:block;}} .inp{{{H_INP}}}</style><script>function showTab(id) {{ document.querySelectorAll('.pay-content').forEach(e => e.classList.remove('active')); document.querySelectorAll('.pay-tab').forEach(e => e.classList.remove('active')); document.getElementById(id).classList.add('active'); event.currentTarget.classList.add('active'); }}</script></head><body><div class="pay-box"><h2 style="color:#0d47a1; margin-top:0;">Payment Gateway</h2><p>School: <b>{d['name']}</b><br>Amount Payable: <b style="color:red; font-size:18px;">₹{fee}</b></p><div class="pay-tabs"><div class="pay-tab active" onclick="showTab('upi')">UPI / QR</div><div class="pay-tab" onclick="showTab('real_payu')">PayU</div><div class="pay-tab" onclick="showTab('real_paytm')">Paytm</div><div class="pay-tab" onclick="showTab('real_insta')">Instamojo</div></div>
        <div id="upi" class="pay-content active" style="text-align:center;"><p style="margin:0 0 10px 0;">Scan to Pay via any UPI App</p><img src="{qr}" style="border:2px solid #ccc; padding:5px; border-radius:5px;"><br><br><span style="font-size:13px; color:gray;">UPI ID: {upi}</span><br><br><form action="/school-finalize-register" method="post"><input type="hidden" name="code" value="{code}"><input type="text" name="utr_no" placeholder="Enter 12-Digit UTR Number" pattern="\d{{12}}" maxlength="12" required style="width:100%; padding:10px; margin-bottom:10px; border:1px solid #ccc; border-radius:5px; text-align:center; font-weight:bold; letter-spacing:2px;"><button type="submit" style="{H_BTN} background:#27ae60;">Submit UTR & Verify</button></form></div>
        <div id="real_payu" class="pay-content"><div style="background:#e8f8f5; color:#117a65; padding:10px; border-radius:5px; margin-bottom:15px; font-size:13px; font-weight:bold; border:1px solid #a3e4d7;">✅ PayU Merchant: {payu_merchant}</div><form action="https://secure.payu.in/_payment" method="post"><input type="hidden" name="key" value="{payu_merchant}" /><input type="hidden" name="txnid" value="{txnid}" /><input type="hidden" name="productinfo" value="School Registration" /><input type="hidden" name="amount" value="{fee}" /><input type="hidden" name="email" value="{d['email']}" /><input type="hidden" name="firstname" value="{d['name']}" /><input type="hidden" name="phone" value="{d['hm_mobile']}" /><input type="hidden" name="surl" value="{surl}" /><input type="hidden" name="furl" value="{furl}" /><input type="hidden" name="hash" value="{payu_hash}" /><button type="submit" style="{H_BTN} background:#f39c12;">Pay with PayU</button></form></div><div id="real_paytm" class="pay-content"><div style="background:#e8f4f8; color:#0d47a1; padding:10px; border-radius:5px; margin-bottom:15px; font-size:13px; font-weight:bold; border:1px solid #b3e5fc;">✅ Paytm MID: {paytm_mid}</div><form action="https://securegw.paytm.in/theia/processTransaction" method="post"><input type="hidden" name="MID" value="{paytm_mid}"><input type="hidden" name="ORDER_ID" value="{txnid}"><input type="hidden" name="CUST_ID" value="{d['hm_mobile']}"><input type="hidden" name="INDUSTRY_TYPE_ID" value="Retail"><input type="hidden" name="CHANNEL_ID" value="WEB"><input type="hidden" name="TXN_AMOUNT" value="{fee}"><input type="hidden" name="WEBSITE" value="DEFAULT"><input type="hidden" name="CALLBACK_URL" value="{surl}"><input type="hidden" name="CHECKSUMHASH" value="dummy_checksum_for_UI"><button type="submit" style="{H_BTN} background:#00b9f5;">Pay with Paytm</button></form></div><div id="real_insta" class="pay-content"><div style="background:#f4ecf7; color:#8e44ad; padding:10px; border-radius:5px; margin-bottom:15px; font-size:13px; font-weight:bold; border:1px solid #d2b4de;">✅ Instamojo API: {inst_key[:10]}...</div><form action="/school-finalize-register" method="post"><input type="hidden" name="code" value="{code}" /><button type="submit" style="{H_BTN} background:#8e44ad;">Pay with Original Instamojo</button></form></div></div></body></html>"""

@app.post("/school-finalize-register", response_class=HTMLResponse)
async def school_finalize_register(code: str=Form(...), utr_no: str=Form(None)):
    if utr_no is not None:
        if len(utr_no) != 12 or not utr_no.isdigit():
            return "<html><body><h2 style='text-align:center; color:red; margin-top:50px;'>Invalid UTR Number! Please enter correct 12-digit UTR from your bank app.</h2><a href='javascript:history.back()' style='display:block; text-align:center;'>Go Back</a></body></html>"
    if code in temp_regs:
        d = temp_regs[code]
        schools.append({"code": d["code"], "name": d["name"], "email": d["email"], "password": d["password"], "hm_name": d["hm_name"], "hm_mobile": d["hm_mobile"], "address": d["address"], "state": d["state"], "pay_status": "Processing UTR", "status": "Pending", "school_upi": "", "student_fee": "0", "utr_no": utr_no})
        del temp_regs[code]
        save_db()
        return f"<html><body style='{H_BODY}'><div style='{H_BOX}'><h1 style='color:orange;'>⏳ Payment Processing!</h1><p>Your UTR Number <b>{utr_no}</b> is recorded. Pending Admin Approval.</p><a href='/school-reg-status-check' style='display:inline-block; margin-top:20px; padding:10px 20px; background:#0d47a1; color:white; text-decoration:none; border-radius:5px;'>Check Status / Login</a></div></body></html>"
    return "Error"

@app.get("/school-reg-status-check", response_class=HTMLResponse)
async def school_reg_status_check(error: str = None):
    err = f"<p style='color:red;'>{error}</p>" if error else ""
    return get_header("Check Status") + render_school_reg_sidebar('status') + f"<div class='content'><h2>Check Application Status</h2>{err}<div class='box' style='max-width:400px;'><form action='/school-reg-status-submit' method='post'><label>School Code (User ID)</label><input type='text' name='code' required><label>Password</label><input type='password' name='password' required><button type='submit' class='btn' style='background:#d35400; width:100%; margin-top:10px;'>Check Status / Login</button></form></div></div></body></html>"

@app.post("/school-reg-status-submit", response_class=HTMLResponse)
async def school_reg_status_submit(code: str=Form(...), password: str=Form(...)):
    s = next((x for x in schools if x["code"] == code and x.get("password") == password), None)
    if not s: return RedirectResponse(url="/school-reg-status-check?error=Invalid Code or Password!", status_code=303)
    return RedirectResponse(url=f"/school-reg-view/{code}", status_code=303)

@app.get("/school-reg-view/{code}", response_class=HTMLResponse)
async def school_reg_view(code: str):
    s = next((x for x in schools if x["code"] == code), None)
    if not s: return "Not found"
    return get_header("View Application") + render_school_reg_sidebar('status') + f"<style>@media print {{ .sidebar, .no-print {{display:none !important;}} .content{{margin:0 !important; padding:0 !important;}} }}</style><div class='content'><div style='display:flex; justify-content:space-between; align-items:center;' class='no-print'><h2>Application Details</h2><button onclick='window.print()' class='btn' style='background:#e74c3c;'>🖨️ Print / Save PDF</button></div><div class='box' style='margin-top:15px; font-size:16px;'><table style='width:100%;'><tr><td><b>School Name:</b></td><td>{s['name']}</td></tr><tr><td><b>School Code:</b></td><td>{s['code']}</td></tr><tr><td><b>Headmaster:</b></td><td>{s.get('hm_name','')} (📞 {s.get('hm_mobile','')})</td></tr><tr><td><b>Email:</b></td><td>{s.get('email','')}</td></tr><tr><td><b>Address:</b></td><td>{s.get('address','')}, {s.get('state','')}</td></tr><tr><td><b>Registration Status:</b></td><td style='font-weight:bold; color:{'green' if s.get('status')=='Active' else 'orange'};'>{s.get('status','Pending')}</td></tr><tr><td><b>Payment Status:</b></td><td style='font-weight:bold;'>{s.get('pay_status','Pending')}</td></tr><tr><td><b>UTR Number:</b></td><td style='color:blue;'>{s.get('utr_no','N/A')}</td></tr></table></div></div></body></html>"


# ----------------- STUDENT REGISTRATION PORTAL -----------------
def generate_18_point_form(action_url, is_edit=False, st=None, school_code_fixed=None):
    st = st or {}
    s_opts = ""
    if not school_code_fixed:
        s_opts = "<option value=''>-- Select Target School --</option>"
        for s in schools:
            if s.get("status") == "Active": s_opts += f"<option value='{s['code']}' {'selected' if st.get('school_code')==s['code'] else ''}>{s['name']} ({s['state']})</option>"
    else:
        s_opts = f"<input type='hidden' name='school_code' value='{school_code_fixed}'>"
    
    gen_opts = "".join([f"<option {'selected' if st.get('gender')==g else ''}>{g}</option>" for g in ["Male", "Female", "Other"]])
    bg_opts = "".join([f"<option {'selected' if st.get('blood_group')==b else ''}>{b}</option>" for b in blood_groups])
    min_opts = "".join([f"<option {'selected' if st.get('minority')==m else ''}>{m}</option>" for m in ["No", "Yes"]])
    cat_opts = "".join([f"<option {'selected' if st.get('category')==c else ''}>{c}</option>" for c in categories])
    st_list = "".join([f"<option value='{s}' {'selected' if st.get('state')==s else ''}>{s}</option>" for s in states_list])
    cls_opts = "".join([f"<option {'selected' if st.get('class_section')==c else ''}>{c}</option>" for c in classes_list])
    lang_opts = "".join([f"<option {'selected' if st.get('language')==l else ''}>{l}</option>" for l in languages_list])
    photo_html = f"<label>20. Upload Photo</label><input type='file' name='photo' accept='image/*'>" if not is_edit else f"<label>20. Update Photo</label><input type='file' name='photo' accept='image/*'>"
    school_field = f"<label>21. Target School</label><select name='school_code' required>{s_opts}</select>" if not school_code_fixed else s_opts

    dist_val = st.get('district', '')
    js_script = f"""<script>
    const distMap = {{"Odisha": ["Angul", "Balangir", "Balasore", "Bargarh", "Bhadrak", "Boudh", "Cuttack", "Deogarh", "Dhenkanal", "Gajapati", "Ganjam", "Jagatsinghpur", "Jajpur", "Jharsuguda", "Kalahandi", "Kandhamal", "Kendrapara", "Kendujhar", "Khordha", "Koraput", "Malkangiri", "Mayurbhanj", "Nabarangpur", "Nayagarh", "Nuapada", "Puri", "Rayagada", "Sambalpur", "Subarnapur", "Sundargarh"]}};
    function popDist() {{ let s = document.getElementById('stateSelect').value; let d = document.getElementById('distSelect'); d.innerHTML = '<option value="">--Select District--</option>'; if(distMap[s]) {{ distMap[s].forEach(x => {{ let sel = (x === "{dist_val}") ? "selected" : ""; d.innerHTML += `<option value="${{x}}" ${{sel}}>${{x}}</option>`; }}); }} else if(s !== "") {{ d.innerHTML += `<option value="Other">Other District</option>`; }} }}
    window.onload = function() {{ if(document.getElementById('stateSelect').value !== "") popDist(); }};
    </script>"""

    return f"""<form action="{action_url}" method="post" enctype="multipart/form-data"><div class="grid-2"><div><label>1. Student's Name</label><input type="text" name="st_name" value="{st.get('st_name','')}" required></div><div><label>2. Gender</label><select name="gender" required>{gen_opts}</select></div><div><label>3. Date of Birth</label><input type="date" name="dob" value="{st.get('dob','')}" required></div><div><label>4. Mother's Name</label><input type="text" name="mother_name" value="{st.get('mother_name','')}" required></div><div><label>5. Father's Name</label><input type="text" name="father_name" value="{st.get('father_name','')}" required></div><div><label>6. PEN Number</label><input type="text" name="pen_no" value="{st.get('pen_no','')}" required></div><div><label>7. APAR ID</label><input type="text" name="apar_id" value="{st.get('apar_id','')}" required></div><div><label>8. Mobile No</label><input type="text" name="mobile" value="{st.get('mobile','')}" required></div><div><label>9. Blood Group</label><select name="blood_group" required>{bg_opts}</select></div><div><label>10. Minority Group</label><select name="minority" required>{min_opts}</select></div><div><label>11. Category</label><select name="category" required>{cat_opts}</select></div><div><label>12. AADHAAR Number</label><input type="text" name="aadhaar" value="{st.get('aadhaar','')}" required></div><div><label>13. Address</label><input type="text" name="address" value="{st.get('address','')}" required></div><div><label>14. PIN Code</label><input type="text" name="pin_code" value="{st.get('pin_code','')}" required></div><div><label>15(a). State</label><select name="state" id="stateSelect" onchange="popDist()" required><option value="">--Select State--</option>{st_list}</select></div><div><label>15(b). District</label><select name="district" id="distSelect" required><option value="{dist_val}">{dist_val if dist_val else '--Select District--'}</option></select></div><div><label>16. Local Language</label><select name="language" required><option value="">--Select Language--</option>{lang_opts}</select></div><div><label>17. Mail ID</label><input type="email" name="email" value="{st.get('email','')}" required></div><div><label>18. Class Section</label><select name="class_section" required>{cls_opts}</select></div><div><label>19. Roll No</label><input type="text" name="roll_no" value="{st.get('roll_no','')}" required></div><div>{photo_html}</div><div style="grid-column: span 2;">{school_field}</div></div><button type="submit" class="btn" style="background:#27ae60; width:100%; margin-top:20px; font-size:16px;">{'Save Student Data' if is_edit else 'Submit Registration & Proceed to Payment'}</button></form>{js_script}"""

@app.get("/student-registration", response_class=HTMLResponse)
async def student_registration():
    return get_header("Student Registration") + render_student_sidebar('apply') + f"""<div class="content"><div style="max-width:900px; margin:0 auto;"><div class="box"><h2 style="color:#0d47a1; text-align:center;">Online Student Registration</h2>{generate_18_point_form('/student-payment')}</div></div></div></body></html>"""

@app.post("/student-payment", response_class=HTMLResponse)
async def student_payment(request: Request):
    form = await request.form()
    school_code = form.get("school_code")
    s = next((x for x in schools if x["code"] == school_code), None)
    if not s: return "School not found!"
    
    st_id = uuid.uuid4().hex[:8].upper()
    student_data = dict(form)
    student_data["id"] = st_id
    student_data["pay_status"] = "Pending"
    student_data["status"] = "Pending"
    student_data["subjects"] = {}
    
    photo = form.get("photo")
    if photo and hasattr(photo, "filename") and photo.filename:
        c = await photo.read()
        student_data["photo"] = f"data:{photo.content_type};base64,{base64.b64encode(c).decode('utf-8')}"
    else: student_data["photo"] = ""
    
    students.append(student_data)
    save_db()

    upi = s.get("school_upi") or admin_data.get("upi_id", "")
    inst_key = admin_data.get("instamojo_api_key", "")
    payu_merchant = admin_data.get("payu_merchant_id", "")
    payu_salt = admin_data.get("payu_salt", "")
    paytm_mid = admin_data.get("paytm_mid", "")
    fee = s.get("student_fee") or "0"
    qr = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=upi://pay?pa={upi}%26am={fee}"
    txnid = uuid.uuid4().hex[:15]
    payu_hash = get_payu_hash(payu_merchant, payu_salt, txnid, fee, "Student Registration", student_data['st_name'], student_data['email'])
    base_url = str(request.base_url).rstrip("/").replace("http://", "https://")
    surl = f"{base_url}/payu-success-student?st_id={st_id}"
    furl = f"{base_url}/payu-failure"

    return f"""<html><head><style>body{{{H_BODY}}} .pay-box{{{H_BOX}}} .pay-tabs{{display:flex; flex-wrap:wrap; border-bottom:2px solid #ccc; margin-bottom:20px;}} .pay-tab{{flex:1; padding:8px 5px; cursor:pointer; font-weight:bold; font-size:13px; background:#eee; border-radius:5px 5px 0 0; margin-right:2px; text-align:center;}} .pay-tab.active{{background:#27ae60; color:white;}} .pay-content{{display:none; text-align:left;}} .pay-content.active{{display:block;}} .inp{{{H_INP}}}</style><script>function showTab(id) {{ document.querySelectorAll('.pay-content').forEach(e => e.classList.remove('active')); document.querySelectorAll('.pay-tab').forEach(e => e.classList.remove('active')); document.getElementById(id).classList.add('active'); event.currentTarget.classList.add('active'); }}</script></head><body><div class="pay-box"><h2 style="color:#0d47a1; margin-top:0;">Registration Payment</h2><div style="background:#fff3cd; color:#856404; padding:10px; border-radius:5px; margin-bottom:15px; font-weight:bold; text-align:center;">⚠️ Save your Application No (ID): <span style="font-size:18px;">{st_id}</span></div><p>Student: <b>{form.get('st_name')}</b><br>Amount Payable: <b style="color:red; font-size:18px;">₹{fee}</b></p><div class="pay-tabs"><div class="pay-tab active" onclick="showTab('upi')">UPI / QR</div><div class="pay-tab" onclick="showTab('real_payu')">PayU</div><div class="pay-tab" onclick="showTab('real_paytm')">Paytm</div><div class="pay-tab" onclick="showTab('real_insta')">Instamojo</div></div>
        
        <div id="upi" class="pay-content active" style="text-align:center;"><p style="margin:0 0 10px 0;">Scan to Pay via any UPI App</p><img src="{qr}" style="border:2px solid #ccc; padding:5px; border-radius:5px;"><br><br><span style="font-size:13px; color:gray;">UPI ID: {upi}</span><br><br>
        <form action="/student-finalize-register" method="post">
            <input type="hidden" name="st_id" value="{st_id}">
            <input type="text" name="utr_no" placeholder="Enter 12-Digit UTR Number" pattern="\d{{12}}" maxlength="12" required style="width:100%; padding:10px; margin-bottom:10px; border:1px solid #ccc; border-radius:5px; text-align:center; font-weight:bold; letter-spacing:2px;">
            <button type="submit" style="{H_BTN} background:#27ae60;">Submit UTR & Verify</button>
        </form></div>
        
        <div id="real_payu" class="pay-content"><div style="background:#e8f8f5; color:#117a65; padding:10px; border-radius:5px; margin-bottom:15px; font-size:13px; font-weight:bold; border:1px solid #a3e4d7;">✅ PayU Merchant: {payu_merchant}</div><form action="https://secure.payu.in/_payment" method="post"><input type="hidden" name="key" value="{payu_merchant}" /><input type="hidden" name="txnid" value="{txnid}" /><input type="hidden" name="productinfo" value="Student Registration" /><input type="hidden" name="amount" value="{fee}" /><input type="hidden" name="email" value="{student_data['email']}" /><input type="hidden" name="firstname" value="{student_data['st_name']}" /><input type="hidden" name="phone" value="{student_data['mobile']}" /><input type="hidden" name="surl" value="{surl}" /><input type="hidden" name="furl" value="{furl}" /><input type="hidden" name="hash" value="{payu_hash}" /><button type="submit" style="{H_BTN} background:#f39c12;">Pay with PayU</button></form></div><div id="real_paytm" class="pay-content"><div style="background:#e8f4f8; color:#0d47a1; padding:10px; border-radius:5px; margin-bottom:15px; font-size:13px; font-weight:bold; border:1px solid #b3e5fc;">✅ Paytm MID: {paytm_mid}</div><form action="https://securegw.paytm.in/theia/processTransaction" method="post"><input type="hidden" name="MID" value="{paytm_mid}"><input type="hidden" name="ORDER_ID" value="{txnid}"><input type="hidden" name="CUST_ID" value="{student_data['mobile']}"><input type="hidden" name="INDUSTRY_TYPE_ID" value="Retail"><input type="hidden" name="CHANNEL_ID" value="WEB"><input type="hidden" name="TXN_AMOUNT" value="{fee}"><input type="hidden" name="WEBSITE" value="DEFAULT"><input type="hidden" name="CALLBACK_URL" value="{surl}"><input type="hidden" name="CHECKSUMHASH" value="dummy_checksum_for_UI"><button type="submit" style="{H_BTN} background:#00b9f5;">Pay with Paytm</button></form></div><div id="real_insta" class="pay-content"><div style="background:#f4ecf7; color:#8e44ad; padding:10px; border-radius:5px; margin-bottom:15px; font-size:13px; font-weight:bold; border:1px solid #d2b4de;">✅ Instamojo API: {inst_key[:10]}...</div><form action="/student-finalize-register" method="post"><input type="hidden" name="st_id" value="{st_id}" /><button type="submit" style="{H_BTN} background:#8e44ad;">Pay with Original Instamojo</button></form></div></div></body></html>"""

@app.post("/student-finalize-register", response_class=HTMLResponse)
async def student_finalize_register(st_id: str=Form(...), utr_no: str=Form(None)):
    if utr_no is not None:
        if len(utr_no) != 12 or not utr_no.isdigit():
            return "<html><body><h2 style='text-align:center; color:red; margin-top:50px;'>Invalid UTR Number! Please enter correct 12-digit UTR from your bank app.</h2><a href='javascript:history.back()' style='display:block; text-align:center;'>Go Back</a></body></html>"
            
    for st in students:
        if st.get("id") == st_id:
            st["pay_status"] = "Processing UTR"
            st["utr_no"] = utr_no
            break
    save_db()
    return f"<html><body style='{H_BODY}'><div style='{H_BOX}'><h1 style='color:orange;'>⏳ Payment Processing!</h1><p>Your UTR Number <b>{utr_no}</b> is recorded. Pending Admin Approval.</p><a href='/student-status-check' style='display:inline-block; margin-top:20px; padding:10px 20px; background:#0d47a1; color:white; text-decoration:none; border-radius:5px;'>Check Status / Login</a></div></body></html>"

@app.get("/student-status-check", response_class=HTMLResponse)
async def student_status_check(error: str = None):
    err = f"<p style='color:red;'>{error}</p>" if error else ""
    return get_header("Check Status") + render_student_sidebar('status') + f"<div class='content'><h2>Check Student Application Status</h2>{err}<div class='box' style='max-width:400px;'><form action='/student-status-submit' method='post'><label>Application Number (Student ID)</label><input type='text' name='st_id' required><label>Date of Birth</label><input type='date' name='dob' required><button type='submit' class='btn' style='background:#8e44ad; width:100%; margin-top:10px;'>Login / Check Status</button></form></div></div></body></html>"

@app.post("/student-status-submit", response_class=HTMLResponse)
async def student_status_submit(st_id: str=Form(...), dob: str=Form(...)):
    st = next((x for x in students if x.get("id") == st_id and x.get("dob") == dob), None)
    if not st: return RedirectResponse(url="/student-status-check?error=Invalid Application Number or Date of Birth!", status_code=303)
    return RedirectResponse(url=f"/student-view-application/{st_id}", status_code=303)

@app.get("/student-view-application/{st_id}", response_class=HTMLResponse)
async def student_view_application(st_id: str):
    st = next((x for x in students if x.get("id") == st_id), None)
    if not st: return "Not found"
    sch = next((x for x in schools if x["code"] == st.get("school_code")), None)
    sch_name = sch["name"] if sch else "Unknown School"
    return get_header("View Application") + render_student_sidebar('status') + f"""<style>@media print {{ .sidebar, .no-print {{display:none !important;}} .content{{margin:0 !important; padding:0 !important;}} }} table td{{padding:8px;}}</style><div class='content'><div style="display:flex; justify-content:space-between; align-items:center;" class="no-print"><h2>Application Details</h2><button onclick="window.print()" class="btn" style="background:#e74c3c;">🖨️ Print / Save PDF</button></div><div class='box' style='margin-top:15px; font-size:15px;'><div style="text-align:center; border-bottom:2px solid #ccc; padding-bottom:10px; margin-bottom:20px;"><h1 style="margin:0; color:#0d47a1;">{sch_name}</h1><h3>Student Registration Form</h3></div><div style="display:flex; justify-content:space-between;"><table style='width:70%;'><tr><td><b>App Number (ID):</b></td><td><span style="background:#eee; padding:3px 6px; font-weight:bold;">{st.get('id','')}</span></td></tr><tr><td><b>Student Name:</b></td><td>{st.get('st_name','')}</td></tr><tr><td><b>DOB:</b></td><td>{st.get('dob','')}</td></tr><tr><td><b>Father's Name:</b></td><td>{st.get('father_name','')}</td></tr><tr><td><b>Mother's Name:</b></td><td>{st.get('mother_name','')}</td></tr><tr><td><b>Class Section:</b></td><td>{st.get('class_section','')}</td></tr><tr><td><b>Roll No:</b></td><td>{st.get('roll_no','')}</td></tr><tr><td><b>Payment Status:</b></td><td style="font-weight:bold; color:{'green' if st.get('pay_status')=='Paid' else 'red'}">{st.get('pay_status','Pending')}</td></tr><tr><td><b>Status:</b></td><td style="font-weight:bold; color:{'green' if st.get('status')=='Approved' else ('red' if st.get('status')=='Rejected' else 'orange')};">{st.get('status','Pending')}</td></tr><tr><td><b>UTR Number:</b></td><td style="color:blue;">{st.get('utr_no','N/A')}</td></tr></table><div><img src="{st.get('photo','')}" style="width:120px; height:150px; border:2px solid #ccc; border-radius:5px; object-fit:cover;"></div></div><h3 style="margin-top:20px; color:#0d47a1; border-bottom:1px solid #ccc;">Other Details</h3><table style='width:100%;'><tr><td><b>Gender:</b> {st.get('gender','')}</td><td><b>Blood Group:</b> {st.get('blood_group','')}</td></tr><tr><td><b>Mobile:</b> {st.get('mobile','')}</td><td><b>Email:</b> {st.get('email','')}</td></tr><tr><td><b>Aadhaar:</b> {st.get('aadhaar','')}</td><td><b>PEN No:</b> {st.get('pen_no','')}</td></tr><tr><td><b>APAR ID:</b> {st.get('apar_id','')}</td><td><b>Category:</b> {st.get('category','')}</td></tr><tr><td><b>Minority:</b> {st.get('minority','')}</td><td><b>Language:</b> {st.get('language','')}</td></tr><tr><td><b>Address:</b> {st.get('address','')}</td><td><b>State/District:</b> {st.get('state','')} - {st.get('district','')}</td></tr></table></div></div></body></html>"""


# ----------------- EDIT / DELETE STUDENT & MARKS (SHARED ROUTES) -----------------
@app.get("/delete-student/{portal}/{st_id}", response_class=HTMLResponse)
async def delete_student(portal: str, st_id: str):
    global students
    students = [st for st in students if st.get("id") != st_id]
    db["students"] = students
    save_db()
    redir = "/admin-manage-students" if portal == "admin" else f"/school-my-students/{portal}"
    return RedirectResponse(url=redir, status_code=303)

@app.get("/edit-student/{portal}/{st_id}", response_class=HTMLResponse)
async def edit_student(portal: str, st_id: str):
    st = next((x for x in students if x.get("id") == st_id), None)
    if not st: return "Student Not Found"
    sch_code = st.get('school_code')
    sch = next((s for s in schools if s["code"] == sch_code), None) if sch_code else None
    bg_img = sch.get('school_bg') if (sch and portal != "admin") else None
    sidebar = render_admin_sidebar('students') if portal == "admin" else render_school_sidebar('my' if st.get('status')=='Approved' else 'manage', portal)
    fixed_code = None if portal == "admin" else portal
    return get_header("Edit Student", bg_img) + sidebar + f"<div class='content'><h2>Edit Profile: {st.get('st_name','')}</h2><div class='box'>{generate_18_point_form(f'/update-student/{portal}/{st_id}', is_edit=True, st=st, school_code_fixed=fixed_code)}</div></div></body></html>"

@app.post("/update-student/{portal}/{st_id}", response_class=HTMLResponse)
async def update_student(portal: str, st_id: str, request: Request):
    form = await request.form()
    st = next((x for x in students if x.get("id") == st_id), None)
    if st:
        for k, v in form.items():
            if k != "photo": st[k] = v
        photo = form.get("photo")
        if photo and hasattr(photo, "filename") and photo.filename:
            c = await photo.read()
            st["photo"] = f"data:{photo.content_type};base64,{base64.b64encode(c).decode('utf-8')}"
        save_db()
    redir = "/admin-manage-students" if portal == "admin" else (f"/school-my-students/{portal}" if st.get("status")=="Approved" else f"/school-manage-students/{portal}")
    return RedirectResponse(url=redir, status_code=303)

@app.get("/manage-marks/{portal}/{st_id}", response_class=HTMLResponse)
async def manage_marks(portal: str, st_id: str):
    st = next((x for x in students if x.get("id") == st_id), None)
    if not st: return "Student Not Found"
    sch_code = st.get('school_code')
    sch = next((s for s in schools if s["code"] == sch_code), None) if sch_code else None
    bg_img = sch.get('school_bg') if (sch and portal != "admin") else None
    sidebar = render_admin_sidebar('students') if portal == "admin" else render_school_sidebar('my', portal)
    
    subs = st.get("subjects", {})
    sub_rows = ""
    for code, details in subs.items():
        if isinstance(details, dict):
            sub_rows += f"<tr><td>{code}</td><td>{details['name']}</td><td>{details['full']}</td><td>{details['sec']}</td><td><a href='/delete-subject/{portal}/{st_id}/{code}' class='btn' style='background:#e74c3c;'>Remove</a></td></tr>"
        else:
            sub_rows += f"<tr><td>-</td><td>{code}</td><td>100</td><td>{details}</td><td><a href='/delete-subject/{portal}/{st_id}/{code}' class='btn' style='background:#e74c3c;'>Remove</a></td></tr>"

    return get_header("Manage Marks", bg_img) + sidebar + f"""<div class='content'><h2>Manage Subjects & Marks for {st.get('st_name','')}</h2><div class='grid-2'><div class='box'><h3>Add / Edit Subject</h3><form action='/save-subject/{portal}/{st_id}' method='post'><label>Subject Code (e.g. FLO)</label><input type='text' name='sub_code' required><label>Subject Name (e.g. FIRST LANGUAGE ODIA)</label><input type='text' name='sub_name' required><label>Full Marks</label><input type='number' name='full_marks' required value='100'><label>Marks Secured</label><input type='number' name='marks_secured' required><button type='submit' class='btn' style='background:#27ae60; width:100%;'>Save Subject</button></form></div><div class='box'><h3>Current Subjects</h3><table><tr><th>Code</th><th>Subject</th><th>Full Marks</th><th>Secured</th><th>Action</th></tr>{sub_rows}</table></div></div></div></body></html>"""

@app.post("/save-subject/{portal}/{st_id}", response_class=HTMLResponse)
async def save_subject(portal: str, st_id: str, sub_code: str=Form(...), sub_name: str=Form(...), full_marks: str=Form(...), marks_secured: str=Form(...)):
    st = next((x for x in students if x.get("id") == st_id), None)
    if st:
        if "subjects" not in st: st["subjects"] = {}
        st["subjects"][sub_code] = {"name": sub_name, "full": full_marks, "sec": marks_secured}
        save_db()
    return RedirectResponse(url=f"/manage-marks/{portal}/{st_id}", status_code=303)

@app.get("/delete-subject/{portal}/{st_id}/{sub_code}", response_class=HTMLResponse)
async def delete_subject(portal: str, st_id: str, sub_code: str):
    st = next((x for x in students if x.get("id") == st_id), None)
    if st and "subjects" in st and sub_code in st["subjects"]:
        del st["subjects"][sub_code]
        save_db()
    return RedirectResponse(url=f"/manage-marks/{portal}/{st_id}", status_code=303)

# ----------------- 100% ORIGINAL CERTIFICATE DESIGN -----------------
def number_to_words(n):
    words = ["", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN", "ELEVEN", "TWELVE", "THIRTEEN", "FOURTEEN", "FIFTEEN", "SIXTEEN", "SEVENTEEN", "EIGHTEEN", "NINETEEN"]
    tens = ["", "", "TWENTY", "THIRTY", "FORTY", "FIFTY", "SIXTY", "SEVENTY", "EIGHTY", "NINETY"]
    if n == 0: return "ZERO"
    if n < 20: return words[n]
    if n < 100: return tens[n // 10] + (" " + words[n % 10] if n % 10 != 0 else "")
    if n < 1000: return words[n // 100] + " HUNDRED" + (" AND " + number_to_words(n % 100) if n % 100 != 0 else "")
    return str(n)

@app.get("/public-certificate/{st_id}", response_class=HTMLResponse)
@app.get("/certificate/{portal}/{st_id}", response_class=HTMLResponse)
async def certificate(st_id: str, portal: str = None):
    st = next((x for x in students if x.get("id") == st_id), None)
    if not st: return "Student Not Found"
    sch = next((s for s in schools if s.get("code") == st.get("school_code")), None)
    school_name = sch.get("name", "YOUR SCHOOL NAME").upper() if sch else "YOUR SCHOOL NAME"
    sch_code = sch.get("code", "0000") if sch else "0000"
    state_val = st.get("state", "Odisha").upper()
    color_map = { "ODISHA": "#8e44ad", "MAHARASHTRA": "#2980b9", "DELHI": "#c0392b", "WEST BENGAL": "#27ae60", "GUJARAT": "#d35400", "ANDHRA PRADESH": "#16a085" }
    theme_color = color_map.get(state_val, "#4a235a")
    
    default_logo = "https://cdn-icons-png.flaticon.com/512/8074/8074804.png"
    logo_url = sch.get("school_logo") if (sch and sch.get("school_logo")) else default_logo
    hm_sign_url = sch.get("hm_sign") if (sch and sch.get("hm_sign")) else ""
    sign_html = f'<img src="{hm_sign_url}" style="height:40px; max-width:150px; background:white; padding:2px;"><br>' if hm_sign_url else '______________<br>'
    
    cert_bg = sch.get('cert_bg') if (sch and sch.get('cert_bg')) else ""
    bg_style = f"background-image: url('{cert_bg}'); background-size: cover; background-position: center;" if cert_bg else "background:white;"
    
    subs = st.get("subjects", {})
    tot_marks = 0; max_marks = 0; sub_rows = ""
    for code, details in subs.items():
        if isinstance(details, dict):
            t_sec = int(details['sec']) if str(details['sec']).isdigit() else 0
            t_full = int(details['full']) if str(details['full']).isdigit() else 0
            tot_marks += t_sec; max_marks += t_full
            sub_rows += f"<tr><td style='border:1px solid {theme_color}; padding:5px 10px; font-weight:bold; color:{theme_color}; text-align:center;'>{code}</td><td style='border:1px solid {theme_color}; padding:5px 10px; font-weight:bold; color:#2c3e50;'>{details['name']}</td><td style='border:1px solid {theme_color}; padding:5px 10px; text-align:center; font-weight:bold; color:{theme_color};'>{details['full']}</td><td style='border:1px solid {theme_color}; padding:5px 10px; text-align:center; font-weight:bold; color:{theme_color};'>{details['sec']}</td></tr>"

    perc = (tot_marks/max_marks * 100) if max_marks > 0 else 0
    grade = "F"
    if perc >= 90: grade = "A1"
    elif perc >= 80: grade = "A"
    elif perc >= 70: grade = "B1"
    elif perc >= 60: grade = "B2"
    elif perc >= 50: grade = "C"
    elif perc >= 40: grade = "D"
    elif perc >= 33: grade = "E"
    
    words_total = number_to_words(tot_marks)
    sl_no = "261122" + st_id[:4]
    qr_text = f"Name:{st.get('st_name','')}|Marks:{tot_marks}/{max_marks}|ID:{st_id}"
    qr_encoded = qr_text.replace(" ", "%20")
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={qr_encoded}"
    bar_url = f"https://barcodeapi.org/api/auto/{st.get('roll_no','')}"
    
    sidebar = render_admin_sidebar('students') if portal == "admin" else (render_school_sidebar('my', portal) if portal else "")
    content_style = "margin-left:260px; padding:20px; display:flex; justify-content:center; align-items:center;" if portal else "margin:0 auto; padding:20px; display:flex; justify-content:center; align-items:center; min-height:100vh;"

    return f"""<html><head><style>body{{margin:0; font-family:Arial, sans-serif; background:#f4f6f9;}} .content{{ {content_style} }} @page {{ size: A4; margin: 0; }} .cert-container {{ width: 210mm; min-height: 297mm; display:flex; flex-direction:column; padding: 15mm; box-sizing: border-box; background:white; position:relative; margin:auto; box-shadow: 0px 20px 40px rgba(0,0,0,0.2); }} .cert-box {{ flex: 1; {bg_style} background-color: #ffffff; background-image: repeating-linear-gradient(45deg, rgba(0,0,0,0.01) 25%, transparent 25%, transparent 75%, rgba(0,0,0,0.01) 75%, rgba(0,0,0,0.01)), repeating-linear-gradient(45deg, rgba(0,0,0,0.01) 25%, transparent 25%, transparent 75%, rgba(0,0,0,0.01) 75%, rgba(0,0,0,0.01)); background-size: 40px 40px; background-position: 0 0, 20px 20px; position:relative; overflow:hidden; border: 12px solid {theme_color}; outline: 4px solid #d4af37; outline-offset: -20px; box-shadow: inset 0 0 40px rgba(0,0,0,0.1); padding:30px; box-sizing:border-box; background-blend-mode: overlay; }} .watermark-container {{ position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); width:500px; height:500px; z-index:1; pointer-events:none; opacity:0.15; }} @media print {{ * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }} body {{background:white;}} .sidebar, .no-print {{display:none !important;}} .content{{margin:0 !important; padding:0 !important;}} .cert-container {{box-shadow:none; padding:0;}} .cert-box{{ width:100%; height:100%; page-break-inside:avoid; border: 12px solid {theme_color}; outline: 4px solid #d4af37; outline-offset: -20px; }} }} .info-grid {{ display: grid; grid-template-columns: 120px auto; gap: 2px 10px; font-size: 13px; margin-bottom:15px; color:#333; }} .info-grid span {{ color: {theme_color}; font-weight:bold; font-size: 14px; text-transform: uppercase; }} .info-grid .label {{ font-style: italic; color: #555; padding:2px; }}</style></head><body><div class="sidebar">{sidebar}</div><div class="content"><div><div class="no-print" style="text-align:center; margin-bottom:15px;"><button onclick="window.print()" style="padding:10px 20px; background:#e74c3c; color:white; border:none; font-weight:bold; cursor:pointer; border-radius:5px; box-shadow:0 4px 6px rgba(0,0,0,0.1);">🖨️ Print / Save as PDF</button><a href="/" style="padding:10px 20px; background:#2c3e50; color:white; text-decoration:none; font-weight:bold; border-radius:5px; margin-left:10px; box-shadow:0 4px 6px rgba(0,0,0,0.1);">🏠 Home</a></div><div class="cert-container"><div class="cert-box"><div class="watermark-container"><svg viewBox="0 0 500 500" width="100%" height="100%"><defs><path id="curve" d="M 60, 250 a 190,190 0 1,1 380,0 a 190,190 0 1,1 -380,0" /></defs><circle cx="250" cy="250" r="230" fill="none" stroke="{theme_color}" stroke-width="6" stroke-dasharray="10 5" /><circle cx="250" cy="250" r="215" fill="none" stroke="{theme_color}" stroke-width="2" /><circle cx="250" cy="250" r="140" fill="none" stroke="{theme_color}" stroke-width="3" /><text font-family="Arial" font-weight="900" font-size="32" fill="{theme_color}" letter-spacing="3"><textPath href="#curve" startOffset="50%" text-anchor="middle">★ {school_name} ★ {school_name} ★</textPath></text><image href="{logo_url}" x="125" y="125" height="250" width="250" preserveAspectRatio="xMidYMid slice" clip-path="circle(50% at 50% 50%)" opacity="0.3" /></svg></div><div style="display:flex; justify-content:space-between; font-size:12px; font-weight:bold; color:{theme_color}; position:relative; z-index:2; padding:5px 10px;"><div><div>ରୋଲ୍ ନଂ / ROLL NO. <span style="color:black; margin-left:5px;">{st.get('roll_no','')}</span></div><div style="margin-top:5px;">ଜିଲ୍ଲା / DISTRICT <span style="color:black; margin-left:17px;">{st.get('district', 'BHADRAK').upper()}</span></div></div><img src="{logo_url}" style="width:75px; height:75px; object-fit:contain; border-radius:5px; padding:2px; background:transparent;"><div style="text-align:right;"><div>କ୍ରମିକ ନଂ. / SL. NO. <span style="color:black; margin-left:5px;">{sl_no}</span></div><div style="margin-top:5px;">ବିଦ୍ୟାଳୟ କୋଡ / SCH. CODE <span style="color:black; margin-left:5px;">{sch_code}</span></div></div></div><div style="text-align:center; position:relative; z-index:2; margin-top:5px; padding:10px; margin-bottom:10px;"><h1 style="color:{theme_color}; margin-bottom:5px; font-size:26px; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">{school_name}</h1><h4 style="margin:0; color:#333; font-weight:normal;">HIGH SCHOOL CERTIFICATE EXAMINATION-2026</h4><h5 style="margin:5px 0 5px 0; color:{theme_color};">CERTIFICATE-CUM-MARK SHEET</h5></div><div style="display:flex; justify-content:space-between; position:relative; z-index:2; padding:15px;"><div style="box-shadow: 0 4px 8px rgba(0,0,0,0.2); border-radius:5px; padding:3px; background:white; display:inline-block; align-self:flex-start;"><img src="{st.get('photo','')}" style="width:95px; height:120px; border:2px solid {theme_color}; object-fit:cover; display:block;"></div><div style="flex:1; margin-left:20px;"><div class="info-grid"><div class="label">ପ୍ରମାଣ କରୁଛୁ ଯେ<br>Certify that</div> <div><span style="padding:2px;">{st.get('st_name','')}</span></div><div class="label">ମାତାଙ୍କ ନାମ<br>Mother's Name</div> <div><span style="padding:2px;">{st.get('mother_name','')}</span></div><div class="label">ପିତାଙ୍କ ନାମ<br>Father's Name</div> <div><span style="padding:2px;">{st.get('father_name','')}</span></div><div class="label">ଜନ୍ମ ତାରିଖ<br>Date of Birth</div> <div><span style="padding:2px;">{st.get('dob','')}</span></div></div><div style="font-size:12px; margin-top:5px; display:inline-block; padding:2px;"><b>{school_name}</b> <span style="color:#555; font-style:italic;">ଉଚ୍ଚ ବିଦ୍ୟାଳୟ/High School</span></div><div style="font-size:11px; margin-top:5px; color:#555; display:inline-block; padding:2px;">Passed the High School Certificate Examination held in the month of February - 2026</div><div style="font-size:11px; margin-top:5px; color:#333; display:inline-block; padding:2px;"><b>PEN No:</b> {st.get('pen_no','')} &nbsp; | &nbsp; <b>APAR ID:</b> {st.get('apar_id','')}</div></div></div><table style="width:100%; margin-top:15px; border-collapse:collapse; position:relative; z-index:2; border:2px solid {theme_color}; color:{theme_color}; font-size:12px; background:transparent;"><tr style="background:rgba(0,0,0,0.03); text-align:center;"><th colspan="4" style="border:1px solid {theme_color}; padding:8px;">ବିଷୟ ଏବଂ ପ୍ରାପ୍ତାଙ୍କ <br> SUBJECTS AND MARKS SECURED</th></tr><tr style="background:rgba(0,0,0,0.03); text-align:center;"><td style="border:1px solid {theme_color}; padding:8px; color:{theme_color}; width:15%;">ବିଷୟ କୋଡ<br>SUBJECT<br>CODE</td><td style="border:1px solid {theme_color}; padding:8px; text-align:left; color:{theme_color};">ବିଷୟ<br>SUBJECT</td><td style="border:1px solid {theme_color}; padding:8px; color:{theme_color}; width:20%;">ପୂର୍ଣ୍ଣାଙ୍କ<br>FULL MARKS</td><td style="border:1px solid {theme_color}; padding:8px; color:{theme_color}; width:20%;">ପ୍ରାପ୍ତାଙ୍କ<br>MARKS SECURED</td></tr>{sub_rows}<tr style="font-weight:bold; background:rgba(0,0,0,0.03);"><td colspan="2" style="border:1px solid {theme_color}; padding:10px; text-align:center;">ମୋଟ TOTAL</td><td style="border:1px solid {theme_color}; padding:10px; text-align:center;">{max_marks}</td><td style="border:1px solid {theme_color}; padding:10px; text-align:center; color:#d32f2f;">{tot_marks}</td></tr></table><div style="text-align:center; font-weight:bold; font-size:13px; margin-top:5px; position:relative; z-index:2; display:inline-block; padding:4px 10px; border-radius:5px;">( {words_total} )</div><div style="display:flex; justify-content:space-between; align-items:flex-end; margin-top:20px; position:relative; z-index:2; font-size:12px; padding:15px;"><div style="text-align:center;"><img src="{bar_url}" style="height:35px; width:150px; margin-bottom:5px; background:white; padding:2px; border-radius:3px;"><br><span style="color:{theme_color}; font-weight:bold;">ପରୀକ୍ଷାଫଳ ପ୍ରକାଶନ ତାରିଖ<br>DATE OF PUBLICATION OF RESULTS</span><br><b>02/05/2026</b><br><br><span style="color:#555; border-top:1px dashed #000; padding-top:5px;">CONTROLLER OF EXAMINATIONS</span></div><div style="text-align:center;"><span style="color:{theme_color}; font-weight:bold;">ଗ୍ରେଡ<br>GRADE</span><br><div style="border:2px solid {theme_color}; padding:5px 20px; font-size:18px; font-weight:bold; color:#d32f2f; margin:5px auto; width:max-content; background:rgba(0,0,0,0.03); box-shadow:inset 0 0 5px rgba(0,0,0,0.1);">{grade}</div></div><div style="text-align:center; color:{theme_color};"><img src="{qr_url}" style="height:80px; width:80px; margin-bottom:15px; border:1px solid #ddd; padding:2px; background:white;"><br>{sign_html}<span style="color:#555;">Principal Signature</span></div></div></div></div></div></div></body></html>"""

# ================= NEW CERTIFICATE MODULE =================

@app.get("/student-cert-apply", response_class=HTMLResponse)
async def student_cert_apply():
    return get_header("Apply Certificate") + render_student_sidebar('cert') + f"<div class='content'><h2>Apply for Certificate</h2><div class='box'><form action='/student-cert-fetch' method='post'><input type='text' name='roll_no' placeholder='Enter Roll Number' required style='{H_INP}'><input type='date' name='dob' required style='{H_INP}'><button type='submit' class='btn' style='background:#8e44ad; width:100%;'>Fetch Details & Apply</button></form></div></div></body></html>"

@app.post("/student-cert-fetch", response_class=HTMLResponse)
async def student_cert_fetch(roll_no: str=Form(...), dob: str=Form(...)):
    st = next((x for x in students if x.get("roll_no") == roll_no and x.get("dob") == dob), None)
    if not st: return "<script>alert('No Student found with this Roll No and DOB!'); window.history.back();</script>"
    if st.get("status") != "Approved": return "<script>alert('Your Admission is not Approved yet!'); window.history.back();</script>"
    
    return get_header("Select Certificate") + render_student_sidebar('cert') + f"<div class='content'><h2>Student Details Found: {st['st_name']}</h2><div class='box'><form action='/student-cert-submit' method='post'><input type='hidden' name='st_id' value='{st['id']}'><input type='hidden' name='school_code' value='{st['school_code']}'><label>Select Certificate Type:</label><select name='cert_type' required style='{H_INP}'><option value=''>-- Select Certificate --</option><option value='Leaving Certificate'>Leaving Certificate</option><option value='Conduct Certificate'>Conduct Certificate</option><option value='Mark-cum-Certificate'>Mark-cum-Certificate</option></select><button type='submit' class='btn' style='background:#27ae60; width:100%;'>Submit Application to School</button></form></div></div></body></html>"

@app.post("/student-cert-submit", response_class=HTMLResponse)
async def student_cert_submit(st_id: str=Form(...), school_code: str=Form(...), cert_type: str=Form(...)):
    req_id = uuid.uuid4().hex[:8].upper()
    db["cert_requests"].append({
        "req_id": req_id,
        "st_id": st_id,
        "school_code": school_code,
        "cert_type": cert_type,
        "status": "Pending",
        "file_data": ""
    })
    save_db()
    return get_header("Success") + render_student_sidebar('cert') + "<div class='content'><div class='box'><h2 style='color:green;'>✅ Application Sent Successfully!</h2><p>Your request has been sent to the school. Please check back within 3 days to download your certificate.</p></div></div></body></html>"

@app.get("/school-cert-manage/{code}", response_class=HTMLResponse)
async def school_cert_manage(code: str):
    sch_reqs = [r for r in db.get("cert_requests", []) if r.get("school_code") == code]
    rows = ""
    for r in sch_reqs:
        st = next((x for x in students if x.get("id") == r["st_id"]), {})
        st_name = st.get("st_name", "Unknown")
        action_btn = f"<a href='/school-cert-action/{r['req_id']}' class='btn' style='background:#3498db;'>Approve & Upload</a>" if r['status'] == "Pending" else f"<span style='color:green; font-weight:bold;'>Approved</span>"
        rows += f"<tr style='background:white;'><td>{st_name}</td><td>{r['cert_type']}</td><td>{r['status']}</td><td>{action_btn}</td></tr>"
    
    return get_header("Certificate Management") + render_school_sidebar('cert_manage', code) + f"<div class='content'><h2>Student Certificate Applications</h2><div class='box'><table><tr><th>Student Name</th><th>Certificate Type</th><th>Status</th><th>Action</th></tr>{rows}</table></div></div></body></html>"

@app.get("/school-cert-action/{req_id}", response_class=HTMLResponse)
async def school_cert_action(req_id: str):
    req = next((r for r in db.get("cert_requests", []) if r["req_id"] == req_id), None)
    if not req: return "Request Not Found"
    st = next((x for x in students if x.get("id") == req["st_id"]), {})
    
    return get_header("Approve Certificate") + f"<div class='content'><h2>Approve {req['cert_type']} for {st.get('st_name')}</h2><div class='box'><p>Verify Payment Status: <b>{st.get('pay_status')}</b></p><form action='/school-cert-upload/{req_id}' method='post' enctype='multipart/form-data'><label>Upload Generated Certificate (PDF/Image):</label><br><input type='file' name='cert_file' required style='{H_INP}'><br><button type='submit' class='btn' style='background:#27ae60;'>Approve & Upload</button></form></div></div></body></html>"

@app.post("/school-cert-upload/{req_id}", response_class=HTMLResponse)
async def school_cert_upload(req_id: str, request: Request):
    form = await request.form()
    file = form.get("cert_file")
    
    for r in db.get("cert_requests", []):
        if r["req_id"] == req_id:
            if file and hasattr(file, "filename") and file.filename:
                c = await file.read()
                r["file_data"] = f"data:{file.content_type};base64,{base64.b64encode(c).decode('utf-8')}"
                r["status"] = "Approved"
            break
    save_db()
    return "<script>alert('Certificate Uploaded Successfully!'); window.location.href='/';</script>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
