import streamlit as st
import sqlite3
import json

st.set_page_config(page_title="School Home Portal - Ultimate Secure Edition", layout="wide")

DB_PATH = "database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            roll TEXT PRIMARY KEY,
            name TEXT,
            fname TEXT,
            mname TEXT,
            dob TEXT,
            mobile TEXT,
            pan TEXT,
            apar TEXT,
            class_name TEXT,
            exam_type TEXT,
            slno TEXT,
            school TEXT,
            photo TEXT,
            total REAL,
            max_marks REAL,
            grade TEXT,
            status TEXT,
            subjects TEXT
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        students_data = [
            {"roll": "175CB0077", "name": "ADYASHA SAHOO", "mname": "MAMATARANI SAHU", "fname": "UTTAM KUMAR SAHOO", "dob": "20/03/2011", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 87}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 81}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 92}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 69}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 73}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 66}], "total": 468, "max": 600, "grade": "B1", "status": "Pass", "slno": "2611220809", "pan": "21333578409", "apar": "340630618949", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0078", "name": "ALOKTIKA MISHRA", "mname": "SAROJINI MISHRA", "fname": "DEBASIS MISHRA", "dob": "14/02/2011", "gender": "FEMALE", "caste": "GENERAL", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 90}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 67}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 86}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 66}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 70}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 67}], "total": 446, "max": 600, "grade": "B1", "status": "Pass", "slno": "2611220810", "pan": "21182142821", "apar": "704082184322", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0079", "name": "ABHILIPSHA DAS", "mname": "JALPANA DAS", "fname": "HIMANSHU BHUSHAN DAS", "dob": "11/02/2010", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 46}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 34}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 38}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 30}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 39}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 43}], "total": 230, "max": 600, "grade": "E", "status": "Pass", "slno": "2611220811", "pan": "21349438955", "apar": "N/A", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0080", "name": "BAISAKHI SAMAL", "mname": "CHANCHALA SAMAL", "fname": "SUDHAKAR SAMAL", "dob": "26/12/2010", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 87}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 72}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 81}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 57}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 61}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 62}], "total": 420, "max": 600, "grade": "B1", "status": "Pass", "slno": "2611220812", "pan": "21041084790", "apar": "789783065343", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0081", "name": "BARSHA PRIYADARSHANI MOHANTY", "mname": "SUBHADRA MOHANTY", "fname": "PURNA CHANDRA MOHANTY", "dob": "01/10/2010", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 60}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 45}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 58}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 30}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 34}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 41}], "total": 268, "max": 600, "grade": "D", "status": "Pass", "slno": "2611220813", "pan": "21498662821", "apar": "913475687849", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0082", "name": "BARSHARANI KHILAR", "mname": "SANDHYARANI KHILAR", "fname": "SANTOSH KHILAR", "dob": "12/03/2011", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 30}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 33}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 39}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 38}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 30}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 34}], "total": 204, "max": 600, "grade": "E", "status": "Pass", "slno": "2611220814", "pan": "21050451252", "apar": "252741731402", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0083", "name": "BHAGYASHREE MOHANTY", "mname": "RASHMITA MOHANTY", "fname": "ARUN KUMAR MOHANTY", "dob": "11/10/2009", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 41}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 38}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 32}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 38}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 36}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 37}], "total": 222, "max": 600, "grade": "E", "status": "Pass", "slno": "2611220815", "pan": "21082361081", "apar": "642970156338", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0084", "name": "DIPTI MAYEE SETHY", "mname": "BUNI SETHY", "fname": "SANJAY SETHY", "dob": "11/01/2011", "gender": "FEMALE", "caste": "SC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 45}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 32}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 38}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 30}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 30}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 38}], "total": 213, "max": 600, "grade": "E", "status": "Pass", "slno": "2611220816", "pan": "21025149546", "apar": "503511373905", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0085", "name": "HARAPRIYA LENKA", "mname": "SARASWATI LENKA", "fname": "NILAMANI LENKA", "dob": "27/11/2010", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 64}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 51}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 76}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 34}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 50}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 53}], "total": 328, "max": 600, "grade": "C", "status": "Pass", "slno": "2611220817", "pan": "21264457196", "apar": "922843423885", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0086", "name": "JOSODA PARIDA", "mname": "GAURIBALA PARIDA", "fname": "SURENDRA PARIDA", "dob": "01/04/2011", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 73}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 40}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 60}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 31}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 39}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 57}], "total": 300, "max": 600, "grade": "C", "status": "Pass", "slno": "2611220818", "pan": "21697711277", "apar": "618622215960", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0087", "name": "JYOTI SWORUPA PADHI", "mname": "PURNIMA PADHI", "fname": "SUDHANSHU SEKHAR PADHI", "dob": "19/09/2010", "gender": "FEMALE", "caste": "GENERAL", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 62}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 43}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 59}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 39}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 39}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 46}], "total": 288, "max": 600, "grade": "D", "status": "Pass", "slno": "2611220819", "pan": "21067317375", "apar": "135620099184", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0088", "name": "JYOTSHNA RANI BISWAL", "mname": "PRATIMA BISWAL", "fname": "SRABAN KUMAR BISWAL", "dob": "13/10/2010", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 74}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 62}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 77}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 41}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 48}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 64}], "total": 366, "max": 600, "grade": "B2", "status": "Pass", "slno": "2611220820", "pan": "23364745896", "apar": "904172854667", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0089", "name": "LIPA JENA", "mname": "MAMATA JENA", "fname": "MANMATH JENA", "dob": "14/05/2010", "gender": "FEMALE", "caste": "SC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 86}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 72}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 82}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 58}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 64}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 67}], "total": 429, "max": 600, "grade": "B1", "status": "Pass", "slno": "2611220821", "pan": "21109012923", "apar": "593617329877", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0091", "name": "LIZA PADHI", "mname": "RANJITA PADHI", "fname": "RATNAKAR PADHI", "dob": "18/09/2010", "gender": "FEMALE", "caste": "GENERAL", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 70}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 53}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 62}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 42}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 52}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 52}], "total": 331, "max": 600, "grade": "C", "status": "Pass", "slno": "2611220822", "pan": "21064948534", "apar": "777043813613", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0092", "name": "LOVELY PALAI", "mname": "JHUNARANI PALAI", "fname": "PRATAP PALAI", "dob": "25/05/2010", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 48}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 38}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 50}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 32}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 32}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 42}], "total": 242, "max": 600, "grade": "D", "status": "Pass", "slno": "2611220823", "pan": "21311696258", "apar": "671413877266", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0093", "name": "MANISHA SETHY", "mname": "PURNIMA SETHY", "fname": "SUSANTA SETHY", "dob": "12/09/2010", "gender": "FEMALE", "caste": "SC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 37}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 32}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 38}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 34}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 30}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 38}], "total": 209, "max": 600, "grade": "E", "status": "Pass", "slno": "2611220824", "pan": "21106762170", "apar": "611657596631", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0094", "name": "MANISHA JENA", "mname": "SUBHASMITA JENA", "fname": "DILLIP JENA", "dob": "01/05/2010", "gender": "FEMALE", "caste": "SC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 74}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 55}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 65}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 43}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 51}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 54}], "total": 342, "max": 600, "grade": "C", "status": "Pass", "slno": "2611220825", "pan": "21025888551", "apar": "270710056668", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0095", "name": "MITASHREE JENA", "mname": "ANAPURNA JENA", "fname": "KHAGESWAR JENA", "dob": "06/04/2011", "gender": "FEMALE", "caste": "SC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 52}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 40}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 58}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 33}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 40}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 43}], "total": 266, "max": 600, "grade": "D", "status": "Pass", "slno": "2611220826", "pan": "21050476279", "apar": "790335617395", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0096", "name": "PRIYANKA PRIYADARSHINI SAMAL", "mname": "SNEHANJALI SAMAL", "fname": "MANGARAJ SAMAL", "dob": "25/04/2010", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 48}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 40}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 44}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 32}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 41}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 35}], "total": 240, "max": 600, "grade": "D", "status": "Pass", "slno": "2611220827", "pan": "21347860819", "apar": "284100557411", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0097", "name": "PUJARANI MOHANTY", "mname": "DEBAKI MOHANTY", "fname": "AMAR KUMAR MOHANTY", "dob": "08/06/2011", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 66}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 56}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 86}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 30}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 42}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 49}], "total": 329, "max": 600, "grade": "C", "status": "Pass", "slno": "2611220828", "pan": "21086864465", "apar": "408019175598", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0098", "name": "PUJARANI PRUSTY", "mname": "SASMITA PRUSTY", "fname": "RABINDRA PRUSTY", "dob": "22/03/2011", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 67}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 58}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 72}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 35}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 43}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 56}], "total": 331, "max": 600, "grade": "C", "status": "Pass", "slno": "2611220829", "pan": "21264956198", "apar": "360893477685", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0099", "name": "PURBASHA PARIDA", "mname": "JHARANA PARIDA", "fname": "HARINARAYAN PARIDA", "dob": "11/02/2010", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 70}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 41}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 59}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 38}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 38}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 54}], "total": 300, "max": 600, "grade": "C", "status": "Pass", "slno": "2611220830", "pan": "21229203899", "apar": "734196300420", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0100", "name": "RANI JENA", "mname": "KUMUDINI JENA", "fname": "RABINDRA JENA", "dob": "18/11/2010", "gender": "FEMALE", "caste": "SC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 48}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 46}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 48}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 33}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 33}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 37}], "total": 245, "max": 600, "grade": "D", "status": "Pass", "slno": "2611220831", "pan": "21421573731", "apar": "701239984481", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0101", "name": "RADHA RANI BEHERA", "mname": "TAPASWINI BEHERA", "fname": "DEBENDRA NATH BEHERA", "dob": "08/03/2011", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 75}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 68}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 77}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 40}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 43}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 57}], "total": 360, "max": 600, "grade": "B2", "status": "Pass", "slno": "2611220832", "pan": "21402389757", "apar": "724381829344", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0102", "name": "RASHMIREKHA DAS", "mname": "SASMITA DAS", "fname": "NRUSINGHA DAS", "dob": "05/12/2010", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 76}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 62}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 80}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 37}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 50}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 62}], "total": 367, "max": 600, "grade": "B2", "status": "Pass", "slno": "2611220833", "pan": "21050388749", "apar": "919157141678", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0103", "name": "RINU MOHANTY", "mname": "MANORAMA MOHANTY", "fname": "SIBA MOHANTY", "dob": "15/08/2010", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 70}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 55}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 74}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 38}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 43}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 53}], "total": 333, "max": 600, "grade": "C", "status": "Pass", "slno": "2611220834", "pan": "21558866778", "apar": "161232284559", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0104", "name": "ROJALIN PANDA", "mname": "RANJITA PANDA", "fname": "PRATAP KUMAR PANDA", "dob": "17/07/2010", "gender": "FEMALE", "caste": "GENERAL", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 84}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 69}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 82}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 48}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 63}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 57}], "total": 403, "max": 600, "grade": "B2", "status": "Pass", "slno": "2611220835", "pan": "21197126707", "apar": "486947073442", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0105", "name": "SAROJNI BEHERA", "mname": "MEERARANI BEHERA", "fname": "MADAN BEHERA", "dob": "25/12/2010", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 51}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 35}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 48}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 38}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 34}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 34}], "total": 240, "max": 600, "grade": "D", "status": "Pass", "slno": "2611220836", "pan": "21024509156", "apar": "377751563500", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0106", "name": "SHRABANI SAHOO", "mname": "DIPALI SAHOO", "fname": "BIDYADHAR SAHOO", "dob": "29/07/2010", "gender": "FEMALE", "caste": "GENERAL", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 81}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 73}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 84}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 77}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 54}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 58}], "total": 427, "max": 600, "grade": "B1", "status": "Pass", "slno": "2611220837", "pan": "21031034330", "apar": "536352323335", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0107", "name": "SHRIYA PARIDA", "mname": "JYOTSNARANI PARIDA", "fname": "ASHOK KUMAR PARIDA", "dob": "04/06/2010", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 64}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 38}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 62}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 31}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 31}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 46}], "total": 272, "max": 600, "grade": "D", "status": "Pass", "slno": "2611220838", "pan": "21704868439", "apar": "833200620741", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0108", "name": "SMRUTIREKHA KHILLAR", "mname": "SABITA KHILLAR", "fname": "CHHABINDRA KHILLAR", "dob": "08/03/2011", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 42}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 44}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 40}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 38}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 37}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 39}], "total": 240, "max": 600, "grade": "D", "status": "Pass", "slno": "2611220839", "pan": "21515201906", "apar": "856403020289", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0109", "name": "SMRUTIREKHA SAHOO", "mname": "PRAMILA SAHOO", "fname": "BIJAY KUMAR SAHOO", "dob": "09/11/2009", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 82}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 69}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 75}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 54}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 56}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 62}], "total": 398, "max": 600, "grade": "B2", "status": "Pass", "slno": "2611220840", "pan": "21158801854", "apar": "845483054020", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0110", "name": "SRUTINGYA KHILAR", "mname": "SABITRI KHILAR", "fname": "BISWANATH KHILAR", "dob": "09/12/2010", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 82}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 71}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 94}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 66}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 65}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 80}], "total": 458, "max": 600, "grade": "B1", "status": "Pass", "slno": "2611220841", "pan": "21013751501", "apar": "240564234821", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0111", "name": "SUBHADRA BEHERA", "mname": "REENARANI BEHERA", "fname": "AJAYA BEHERA", "dob": "13/03/2011", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 67}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 66}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 74}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 44}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 52}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 65}], "total": 368, "max": 600, "grade": "B2", "status": "Pass", "slno": "2611220842", "pan": "21697498328", "apar": "346161684808", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0112", "name": "SUBHASMITA PANDA", "mname": "HEMALATA PANDA", "fname": "NARAYAN PANDA", "dob": "07/09/2010", "gender": "FEMALE", "caste": "GENERAL", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 66}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 52}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 56}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 31}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 44}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 51}], "total": 300, "max": 600, "grade": "C", "status": "Pass", "slno": "2611220843", "pan": "21013361804", "apar": "549518813294", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0113", "name": "SHUBHASMITA SAMANTA", "mname": "SASMITA SAMANTA", "fname": "BHASKAR CHANDRA SAMANTA", "dob": "26/02/2010", "gender": "FEMALE", "caste": "GENERAL", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 57}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 42}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 56}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 31}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 38}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 50}], "total": 274, "max": 600, "grade": "D", "status": "Pass", "slno": "2611220844", "pan": "21077897450", "apar": "939307473716", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0114", "name": "SWAPNARANI PARIDA", "mname": "RADHARANI PARIDA", "fname": "HAREKRUSHNA PARIDA", "dob": "21/12/2010", "gender": "FEMALE", "caste": "GENERAL", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 61}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 50}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 69}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 34}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 46}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 62}], "total": 322, "max": 600, "grade": "C", "status": "Pass", "slno": "2611220845", "pan": "21060625257", "apar": "807530411559", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0115", "name": "SWOPNA JENA", "mname": "BASANTI JENA", "fname": "MUKTIKANTA JENA", "dob": "09/08/2010", "gender": "FEMALE", "caste": "SC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 35}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 32}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 31}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 32}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 34}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 34}], "total": 198, "max": 600, "grade": "E", "status": "Pass", "slno": "2611220846", "pan": "21073087895", "apar": "795235253070", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0116", "name": "TRUPTI REKHA BARIK", "mname": "RANJULATA BARIK", "fname": "RABINDRA BARIK", "dob": "01/02/2010", "gender": "FEMALE", "caste": "SEBC", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 62}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 45}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 57}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 38}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 40}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 42}], "total": 284, "max": 600, "grade": "D", "status": "Pass", "slno": "2611220847", "pan": "21358384708", "apar": "393771061550", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0117", "name": "UME SALMA", "mname": "FAIZUN NESHA", "fname": "SHAH MD QUAMRUDDIN", "dob": "19/04/2010", "gender": "FEMALE", "caste": "GENERAL", "category": "SR", "subjects": [{"code": "FLU", "name": "FIRST LANGUAGE URDU", "max": 100, "sec": 60}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 55}, {"code": "TLH", "name": "THIRD LANGUAGE HINDI", "max": 100, "sec": 48}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 33}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 42}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 48}], "total": 286, "max": 600, "grade": "D", "status": "Pass", "slno": "2611220848", "pan": "21354154825", "apar": "156117659572", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""},
            {"roll": "175CB0118", "name": "YANJYASENI DAS", "mname": "KABITA BEHURIA", "fname": "SUSANTA DAS", "dob": "01/11/2010", "gender": "FEMALE", "caste": "GENERAL", "category": "SR", "subjects": [{"code": "FLO", "name": "FIRST LANGUAGE ODIA", "max": 100, "sec": 38}, {"code": "SLE", "name": "SECOND LANGUAGE ENGLISH", "max": 100, "sec": 30}, {"code": "TLS", "name": "THIRD LANGUAGE SANSKRIT", "max": 100, "sec": 38}, {"code": "MTH", "name": "MATHEMATICS", "max": 100, "sec": 32}, {"code": "GSC", "name": "GENERAL SCIENCE", "max": 100, "sec": 35}, {"code": "SSC", "name": "SOCIAL SCIENCE", "max": 100, "sec": 34}], "total": 207, "max": 600, "grade": "E", "status": "Pass", "slno": "2611220849", "pan": "21072379693", "apar": "147250355555", "school": "LAXMI NARAYAN GIRLS HIGH SCHOOL", "class_name": "X", "exam_type": "ANNUAL", "photo": ""}
        ]
        
        for s in students_data:
            cursor.execute("INSERT OR REPLACE INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (s['roll'], s['name'], s['fname'], s['mname'], s['dob'], s.get('mobile', ''), s['pan'], s['apar'], 
                            s['class_name'], s['exam_type'], s['slno'], s['school'], s.get('photo', ''), s['total'], s['max'], s['grade'], s['status'], json.dumps(s['subjects'])))

    conn.commit()
    conn.close()

init_db()

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT * FROM students")
rows = cursor.fetchall()
students_list = []
for r in rows:
    d = dict(r)
    try:
        d['subjects'] = json.loads(d['subjects'])
    except:
        d['subjects'] = []
    students_list.append(d)
conn.close()

students_json = json.dumps(students_list)
students_json_escaped = students_json.replace("'", "\\\\'")

html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>School Home Portal - Ultimate Secure Edition</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
    <style>
        /* ================= HIGH SECURITY & FULL SCREEN CSS ================= */
        #MainMenu, header, [data-testid="stHeader"], footer, .viewerBadge_container, .stDeployButton {{ display: none !important; }}
        html, body, .stApp, [data-testid="stAppViewContainer"], .main, .block-container {{ background-color: transparent !important; padding: 0 !important; margin: 0 !important; max-width: 100% !important; }}
        body {{ background: url('https://images.unsplash.com/photo-1523050854058-8df90110c9f1?q=80&w=1920&auto=format&fit=crop') no-repeat center center fixed !important; background-size: cover !important; color: #333; min-height: 100vh; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; box-sizing: border-box; overflow-x: hidden; margin: 0; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        .glass-panel {{ background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(8px); border: 1px solid rgba(255, 255, 255, 0.5); border-radius: 20px; padding: 30px; box-shadow: 0 15px 35px rgba(0,0,0,0.2); margin-bottom: 25px; }}
        .header {{ background: linear-gradient(90deg, rgba(13,59,102,0.85), rgba(29,78,216,0.85)); padding: 20px 30px; border-radius: 16px; color: white; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 10px 25px rgba(0,0,0,0.3); margin-bottom: 25px; border: 1px solid rgba(255,255,255,0.2); }}
        .header h2 {{ font-size: 24px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); margin:0;}}
        .header p {{ font-style: italic; font-size: 16px; margin:0;}}
        .scrolling-notice-container {{ background: rgba(254, 240, 138, 0.9); border: 1px solid #f59e0b; border-radius: 12px; padding: 10px 20px; margin-bottom: 25px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); display: flex; align-items: center; overflow: hidden; white-space: nowrap; }}
        .notice-title {{ font-weight: bold; color: #b45309; margin-right: 15px; font-size: 16px; white-space: nowrap; }}
        .scrolling-text {{ color: #854d0e; font-size: 15px; font-weight: 500; display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite; }}
        @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
        .home-action-bar {{ display: flex; justify-content: center; gap: 20px; margin-top: 25vh; flex-wrap: wrap; align-items: center; }}
        .action-pill {{ padding: 20px 20px; border-radius: 20px; color: white; font-weight: bold; font-size: 15px; text-align: center; cursor: pointer; box-shadow: 0 10px 20px rgba(0,0,0,0.3); transition: transform 0.3s, box-shadow 0.3s; flex: 1; min-width: 150px; max-width: 220px; border: 2px solid rgba(255,255,255,0.4); backdrop-filter: blur(8px); }}
        .action-pill:hover {{ transform: translateY(-8px); box-shadow: 0 15px 30px rgba(0,0,0,0.5); }}
        .action-pill .icon-lg {{ font-size: 30px; margin-bottom: 8px; display: block; }}
        .pill-magenta {{ background: linear-gradient(135deg, rgba(219,39,119,0.9), rgba(157,23,77,0.9)); }} 
        .pill-blue {{ background: linear-gradient(135deg, rgba(2,132,199,0.9), rgba(3,105,161,0.9)); }}
        .pill-green {{ background: linear-gradient(135deg, rgba(22,163,74,0.9), rgba(21,128,61,0.9)); }}
        .btn-login {{ width: 100%; padding: 16px; border-radius: 14px; font-weight: bold; font-size: 18px; color: white; border: none; cursor: pointer; margin-bottom: 15px; }}
        .btn-admin {{ background: linear-gradient(135deg, #22c55e, #16a34a); }}
        .btn-school {{ background: linear-gradient(135deg, #3b82f6, #2563eb); }}
        .content-section {{ display: none; }}
        .content-section.active {{ display: block; }}
        .back-btn {{ background: #64748b; color: white; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 20px; box-shadow:0 4px 10px rgba(0,0,0,0.2);}}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; display: block; overflow-x: auto; white-space: nowrap; }}
        th, td {{ padding: 10px 12px; border: 1px solid rgba(203,213,225, 0.6); text-align: left; font-size: 13px; vertical-align: middle; }}
        th {{ background: rgba(30,58,138,0.9); color: white; backdrop-filter: blur(5px); }}
        .badge-pass {{ background: #dcfce7; color: #166534; padding: 4px 10px; border-radius: 6px; font-weight: bold; }}
        .badge-fail {{ background: #fee2e2; color: #b91c1c; padding: 4px 10px; border-radius: 6px; font-weight: bold; }}
        .input-box {{ width: 100%; padding: 10px; border: 1px solid rgba(203,213,225,0.8); border-radius: 8px; font-size: 14px; outline: none; background: rgba(255,255,255,0.9); }}
        .modal {{ display: none; position: fixed; z-index: 100; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.6); justify-content: center; align-items: center; }}
        .modal-content {{ background: rgba(255,255,255,0.95); padding: 30px; border-radius: 20px; width: 500px; max-width: 95%; box-shadow: 0 25px 50px rgba(0,0,0,0.4); }}
        #marksheet-print-area {{ display: none; width: 800px; max-width: 100%; background-color: white; margin: 0 auto; position: relative; padding: 20px; font-family: 'Times New Roman', Times, serif; color: #3b0764; box-sizing: border-box; }}
        .cert-border {{ border: 12px solid #d8b4e2; border-image: repeating-linear-gradient(45deg, #d8b4e2, #d8b4e2 10px, #e8d0ef 10px, #e8d0ef 20px) 15; height: 100%; padding: 15px; position: relative; z-index: 2; display: flex; flex-direction: column; justify-content: space-between; }}
        .cert-watermark {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); opacity: 0.05; font-size: 60px; font-weight: bold; color: #3b0764; z-index: 1; pointer-events: none; user-select: none; white-space: pre; text-align: center; line-height: 1.2; width: 100%; word-wrap: break-word; }}
        .cert-header {{ text-align: center; margin-bottom: 10px; }}
        .cert-header img {{ width: 60px; margin-bottom: 5px; opacity: 0.8;}}
        .cert-header h1 {{ font-size: 20px; margin: 0; color: #4c1d95; text-transform: uppercase; line-height: 1.2; padding: 0 10px;}}
        .cert-header h2 {{ font-size: 14px; margin-top: 5px; color: #3b0764; }}
        .cert-top-info {{ display: flex; justify-content: space-between; font-size: 12px; font-weight: bold; margin-bottom: 10px; border-top: 1px solid #4c1d95; border-bottom: 1px solid #4c1d95; padding: 5px 0; }}
        .cert-middle-section {{ display: flex; gap: 20px; align-items: flex-start; margin-bottom: 10px; z-index: 5; position: relative; }}
        .cert-photo-box {{ width: 90px; height: 110px; border: 2px solid #4c1d95; background-color: #f1f5f9; display: flex; justify-content: center; align-items: center; font-size: 10px; color: #94a3b8; overflow: hidden; flex-shrink: 0; }}
        .cert-details {{ flex-grow: 1; font-size: 13px; line-height: 1.5; }}
        .cert-details .row {{ display: flex; margin-bottom: 5px; }}
        .cert-details .label {{ width: 140px; font-weight: bold; }}
        .cert-details .value {{ font-weight: bold; text-transform: uppercase; border-bottom: 1px dotted #4c1d95; flex: 1; padding-left: 5px;}}
        .cert-table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; border: 2px solid #4c1d95; table-layout: fixed; z-index: 5; position: relative;}}
        .cert-table th, .cert-table td {{ border: 1px solid #4c1d95; padding: 5px; text-align: center; font-size: 12px; font-weight: bold; }}
        .cert-table th {{ background-color: #f3e8ff !important; color: #4c1d95 !important; }}
        .cert-table th:nth-child(1) {{ width: 15%; }}
        .cert-table th:nth-child(2) {{ width: 45%; text-align: left; padding-left: 10px; }}
        .cert-table th:nth-child(3) {{ width: 20%; }}
        .cert-table th:nth-child(4) {{ width: 20%; }}
        .cert-table td:nth-child(2) {{ text-align: left; padding-left: 10px; }}
        .cert-footer-info {{ display: flex; justify-content: space-between; align-items: flex-end; margin-top: 5px; z-index: 5; position: relative;}}
        .cert-grade-box {{ border: 2px solid #4c1d95; padding: 5px 15px; text-align: center; font-weight: bold; background-color: #f3e8ff !important; font-size: 14px;}}
        .cert-signatures {{ display: flex; justify-content: space-between; margin-top: 30px; font-weight: bold; font-size: 11px; text-align: center; z-index: 5; position: relative;}}
        .cert-signatures div {{ border-top: 1px dashed #4c1d95; padding-top: 5px; width: 180px; }}
        @media print {{
            * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important; }}
            body {{ background: white !important; margin: 0; padding: 0; }}
            body * {{ visibility: hidden; }}
            .container {{ display: none !important; }}
            #marksheet-print-area, #marksheet-print-area * {{ visibility: visible; }}
            #marksheet-print-area {{ position: absolute; left: 0; top: 0; width: 100% !important; max-width: 100% !important; display: block !important; margin: 0; padding: 10px; box-shadow: none; border: none; }}
            .no-print {{ display: none !important; }}
        }}
    </style>
</head>
<body id="main-body">
    <script>
        try {{
            if (window.parent && window.parent.document) {{
                let parentStyle = window.parent.document.createElement('style');
                parentStyle.innerHTML = `
                    html, body, [data-testid="stAppViewContainer"], .main, .block-container, .stApp {{
                        background-color: transparent !important; padding: 0 !important; margin: 0 !important; max-width: 100% !important;
                    }}
                    header[data-testid="stHeader"], .stDeployButton, #MainMenu, footer, .viewerBadge_container {{ 
                        display: none !important; height: 0 !important; overflow: hidden !important; visibility: hidden !important;
                    }}
                `;
                window.parent.document.head.appendChild(parentStyle);
            }}
        }} catch(e) {{}}
    </script>

    <div class="container">
        <div class="header">
            <h2>🏫 SCHOOL HOME PORTAL</h2>
            <p>Better Education, Brighter Future</p>
        </div>

        <div id="home-view" class="content-section active">
            <div class="scrolling-notice-container">
                <span class="notice-title">📢 Important Notice Board:</span>
                <span class="scrolling-text" id="display-notice">• Official Marksheet & Portal System is live. | NEW: Permanent Online Database Synchronized!</span>
            </div>

            <div class="home-action-bar">
                <div class="action-pill pill-magenta" onclick="openResultsModal()">
                    <span class="icon-lg">📄</span>Check Results
                </div>
                <div class="action-pill pill-blue" onclick="openPage('admin-login')">
                    <span class="icon-lg">👤</span>Admin Login
                </div>
                <div class="action-pill pill-green" onclick="openPage('school-login')">
                    <span class="icon-lg">🏫</span>School Login
                </div>
            </div>
        </div>

        <div id="school-login" class="content-section glass-panel">
            <button class="back-btn" onclick="goHome()">⬅️ Back to Home</button>
            <div style="max-width: 500px; margin: 0 auto; text-align: center;">
                <h3 style="margin-bottom:10px; color:#0d3b66;">🏫 School Portal Login</h3>
                <p style="color: #64748b; margin-bottom: 20px;">Use your Official School Code and Password.</p>
                <input type="text" id="school-login-id" placeholder="Enter School Code (e.g. 257CB)" class="input-box" style="margin-bottom:15px; text-align:center;">
                <input type="password" id="school-login-pass" placeholder="Enter Password" class="input-box" style="margin-bottom:15px; text-align:center;">
                <button class="btn-login btn-school" onclick="validateSchoolLogin()">Login ➡️</button>
            </div>
        </div>

        <div id="school-dashboard" class="content-section glass-panel">
            <button class="back-btn" onclick="goHome()">🚪 Logout</button>
            <h2 id="school-dash-title" style="color: #0d3b66; margin-bottom: 5px;">🏫 School Dashboard</h2>
            <p id="school-dash-sub" style="color: #64748b; margin-bottom: 20px;"></p>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; gap:10px;">
                <h3>🎓 Approved Students & Records</h3>
                <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                    <label style="font-weight: bold; color: #0d3b66;">Filter by Class:</label>
                    <select id="school-class-filter" class="input-box" style="padding: 8px; width: auto; border:1px solid #0d3b66;" onchange="renderSchoolStudents()">
                        <option value="ALL">-- All Classes --</option>
                        <option value="X">Class X</option>
                    </select>
                </div>
            </div>
            <table style="background: rgba(255,255,255,0.9); border-radius:8px;">
                <thead>
                    <tr><th>Roll No</th><th>Student Name</th><th>Class</th><th>Exam Type</th><th>Total Marks</th><th>% & Grade</th><th>Status</th><th>Actions</th></tr>
                </thead>
                <tbody id="school-student-table-body"></tbody>
            </table>
        </div>

        <div id="admin-login" class="content-section glass-panel">
            <button class="back-btn" onclick="goHome()">⬅️ Back to Home</button>
            <div style="max-width: 500px; margin: 0 auto; text-align: center;">
                <h3 style="margin-bottom:10px; color:#0d3b66;">👑 Master Administrator Login</h3>
                <p style="margin: 10px 0 20px 0; color: #64748b;">Username: <b id="display-admin-user">KULU123</b></p>
                <input type="text" id="admin-user" placeholder="Master Username" class="input-box" style="margin-bottom:15px; text-align:center;">
                <input type="password" id="admin-pass" placeholder="Master Password" class="input-box" style="margin-bottom:15px; text-align:center;">
                <button class="btn-login btn-admin" onclick="validateAdmin()">Login 🚀</button>
            </div>
        </div>

        <div id="admin-dashboard" class="content-section glass-panel">
            <button class="back-btn" onclick="goHome()">🚪 Logout & Home</button>
            <h2 style="color: #0d3b66; margin-bottom: 15px;">👑 Master Admin Dashboard</h2>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; gap:10px;">
                <h3>🎓 Complete Student Database</h3>
            </div>
            <table style="background: rgba(255,255,255,0.9); border-radius:8px;">
                <thead>
                    <tr><th>Roll No</th><th>Student Name</th><th>Class</th><th>School Name</th><th>Total Marks</th><th>Actions</th></tr>
                </thead>
                <tbody id="admin-student-table-body"></tbody>
            </table>
        </div>

        <div id="marksheet-print-area">
            <div class="cert-border">
                <div class="cert-watermark" id="pm-watermark">SCHOOL<br>MARKSHEET</div>
                <div class="cert-header">
                    <img src="https://cdn-icons-png.flaticon.com/512/167/167707.png" crossorigin="anonymous" alt="School Logo">
                    <h1 id="pm-header-school-name">SCHOOL NAME HERE</h1>
                    <h2 id="pm-exam-title" style="font-family: Arial, sans-serif;">HIGH SCHOOL CERTIFICATE EXAMINATION - 2026</h2>
                    <h2 style="font-size: 14px; margin-top:5px; color:#3b0764;">CERTIFICATE-CUM-MARK SHEET</h2>
                </div>
                <div class="cert-top-info">
                    <div>
                        <p>ରୋଲ୍ ନଂ / ROLL NO : <span id="pm-roll" style="color:black;"></span></p>
                        <p>ଜିଲ୍ଲା / DISTRICT : <span style="color:black;">BHADRAK</span></p>
                    </div>
                    <div style="text-align:right;">
                        <p>କ୍ରମିକ ନଂ / SL NO : <span id="pm-slno" style="color:black;"></span></p>
                        <p>ବିଦ୍ୟାଳୟ କୋଡ୍ / SCHOOL CODE : <span id="pm-school-code" style="color:black;">CODE</span></p>
                    </div>
                </div>
                <div class="cert-middle-section">
                    <div class="cert-photo-box">
                        <img id="pm-photo" src="" crossorigin="anonymous" style="width:100%; height:100%; object-fit:cover; display:none;">
                        <span id="pm-photo-text">Photo</span>
                    </div>
                    <div class="cert-details">
                        <div class="row"><div class="label">ପ୍ରମାଣ କରାଯାଉଛି ଯେ<br>Certify that</div><div class="value" id="pm-name"></div></div>
                        <div class="row"><div class="label">ମାତାଙ୍କ ନାମ<br>Mother's Name</div><div class="value" id="pm-mname"></div></div>
                        <div class="row"><div class="label">ପିତାଙ୍କ ନାମ<br>Father's Name</div><div class="value" id="pm-fname"></div></div>
                        <div class="row"><div class="label">ଜନ୍ମ ତାରିଖ<br>Date of Birth</div><div class="value" id="pm-dob"></div></div>
                        <div class="row"><div class="label">ଶ୍ରେଣୀ<br>Class</div><div class="value" id="pm-class" style="color:#b45309;"></div></div>
                        <div class="row"><div class="label">ପ୍ୟାନ୍ ନମ୍ବର<br>PEN No</div><div class="value" id="pm-pan"></div></div>
                        <div class="row"><div class="label">ଆପାର୍ ଆଇଡି<br>APAR ID</div><div class="value" id="pm-apar"></div></div>
                        <div class="row" style="margin-top:5px;"><div class="value" style="width:100%; border-bottom:1px dashed #4c1d95; padding-bottom:5px;" id="pm-school">SCHOOL NAME</div></div>
                        <div class="row" style="margin-top:5px; color:#4c1d95; font-size:12px;" id="pm-pass-text">
                            ଫେବୃଆରୀ ୨୦୨୬ ରେ ଅନୁଷ୍ଠିତ ମାଧ୍ୟମିକ ଉଚ୍ଚ ବିଦ୍ୟାଳୟ ପ୍ରମାଣପତ୍ର ପରୀକ୍ଷାରେ ଉତ୍ତୀର୍ଣ୍ଣ ହୋଇଛନ୍ତି।<br>
                            Passed the High School Certificate Examination held in the month of February - 2026.
                        </div>
                    </div>
                </div>
                <table class="cert-table" id="pm-marks-table">
                    <thead>
                        <tr><th colspan="4">ବିଷୟ ଏବଂ ପ୍ରାପ୍ତାଙ୍କ / SUBJECTS AND MARKS SECURED</th></tr>
                        <tr><th>ବିଷୟ କୋଡ୍<br>SUBJECT CODE</th><th>ବିଷୟ<br>SUBJECT</th><th>ମୋଟାଙ୍କ<br>FULL MARKS</th><th>ପ୍ରାପ୍ତାଙ୍କ<br>MARKS SECURED</th></tr>
                    </thead>
                    <tbody id="pm-marks-body"></tbody>
                    <tfoot>
                        <tr><th colspan="2" style="text-align:right; padding-right:15px;">ମୋଟ / TOTAL</th><th id="pm-total-max">600</th><th id="pm-total-sec"></th></tr>
                    </tfoot>
                </table>
                <div style="text-align:center; font-weight:bold; font-size:12px; text-transform:uppercase;" id="pm-words"></div>
                <div class="cert-footer-info" style="align-items: flex-end;">
                    <div style="flex:1;">
                        <img id="pm-barcode" src="" crossorigin="anonymous" alt="Barcode" style="height:35px; margin-bottom:5px; display:block;">
                        <p style="font-size:10px; color:#4c1d95;">ଫଳାଫଳ ପ୍ରକାଶନ ତାରିଖ<br>DATE OF PUBLICATION OF RESULTS<br><b style="font-size:12px;">02/05/2026</b></p>
                    </div>
                    <div style="flex:1; text-align:center;">
                        <p style="color:#4c1d95; font-size:12px; margin-bottom:5px;">ଗ୍ରେଡ୍<br>GRADE</p>
                        <div class="cert-grade-box" id="pm-grade" style="display:inline-block;"></div>
                    </div>
                    <div style="flex:1; text-align:right;">
                        <img id="pm-qr" src="" crossorigin="anonymous" alt="QR Code" style="height:70px; width:70px; border:1px solid #4c1d95;">
                    </div>
                </div>
                <div class="cert-signatures">
                    <div><p>Controller of Examinations</p><p style="font-family: Arial, sans-serif;">ପରୀକ୍ଷା ନିୟନ୍ତ୍ରକ</p></div>
                    <div><p>Secretary</p><p style="font-family: Arial, sans-serif;">ସମ୍ପାଦକ</p></div>
                </div>
            </div>
            
            <div class="no-print" style="text-align:center; margin-top:20px;">
                <button style="background:#2563eb; color:white; padding:10px 25px; border:none; border-radius:8px; font-weight:bold; cursor:pointer;" onclick="window.print()">🖨️ Print Marksheet</button>
                <button style="background:#16a34a; color:white; padding:10px 25px; border:none; border-radius:8px; font-weight:bold; cursor:pointer; margin-left:10px;" onclick="saveAsPDF()">💾 Save as PDF</button>
                <button style="background:#64748b; color:white; padding:10px 25px; border:none; border-radius:8px; font-weight:bold; cursor:pointer; margin-left:10px;" onclick="closePrintView()">⬅️ Back</button>
            </div>
        </div>
    </div>

    <!-- Results Modal -->
    <div id="resultsModal" class="modal">
        <div class="modal-content" style="text-align: center;">
            <h3 style="color:#0d3b66; margin-bottom:15px;">🔍 Check Results</h3>
            <input type="text" id="check-roll-input" placeholder="Enter Roll Number" style="width:100%; padding:12px; margin-bottom:20px; outline:none; text-align:center;">
            <div id="result-display-area" style="text-align: left; margin-bottom: 20px;"></div>
            <button style="background:#64748b; color:white; border:none; padding:10px 20px; border-radius:8px;" onclick="document.getElementById('resultsModal').style.display='none'">Close ❌</button>
            <button style="background:#2563eb; color:white; border:none; padding:10px 25px; border-radius:8px;" onclick="fetchStudentResult()">View 📄</button>
        </div>
    </div>

    <script>
        const studentsDataStore = JSON.parse('{students_json_escaped}');

        function numberToWords(num) {{
            const a = ['','ONE ','TWO ','THREE ','FOUR ', 'FIVE ','SIX ','SEVEN ','EIGHT ','NINE ','TEN ','ELEVEN ','TWELVE ','THIRTEEN ','FOURTEEN ','FIFTEEN ','SIXTEEN ','SEVENTEEN ','EIGHTEEN ','NINETEEN '];
            const b = ['', '', 'TWENTY','THIRTY','FORTY','FIFTY', 'SIXTY','SEVENTY','EIGHTY','NINETY'];
            if ((num = num.toString()).length > 9) return 'overflow';
            n = ('000000000' + num).substr(-9).match(/^(\\d{{2}})(\\d{{2}})(\\d{{2}})(\\d{{1}})(\\d{{2}})$/);
            if (!n) return; var str = '';
            str += (n[1] != 0) ? (a[Number(n[1])] || b[n[1][0]] + ' ' + a[n[1][1]]) + 'CRORE ' : '';
            str += (n[2] != 0) ? (a[Number(n[2])] || b[n[2][0]] + ' ' + a[n[2][1]]) + 'LAKH ' : '';
            str += (n[3] != 0) ? (a[Number(n[3])] || b[n[3][0]] + ' ' + a[n[3][1]]) + 'THOUSAND ' : '';
            str += (n[4] != 0) ? (a[Number(n[4])] || b[n[4][0]] + ' ' + a[n[4][1]]) + 'HUNDRED ' : '';
            str += (n[5] != 0) ? ((str != '') ? 'AND ' : '') + (a[Number(n[5])] || b[n[5][0]] + ' ' + a[n[5][1]]) : '';
            return str.trim();
        }}

        function openPage(pageId) {{ 
            document.getElementById('home-view').style.display = 'none'; 
            let sections = document.getElementsByClassName('content-section'); 
            for (let sec of sections) {{ sec.classList.remove('active'); }} 
            document.getElementById(pageId).classList.add('active'); 
        }}
        function goHome() {{ 
            let sections = document.getElementsByClassName('content-section'); 
            for (let sec of sections) {{ sec.classList.remove('active'); }} 
            document.getElementById('home-view').style.display = 'block'; 
        }}
        function openResultsModal() {{ 
            document.getElementById('check-roll-input').value = ""; 
            document.getElementById('result-display-area').innerHTML = ""; 
            document.getElementById('resultsModal').style.display='flex'; 
        }}
        
        function fetchStudentResult() {{ 
            let roll = document.getElementById('check-roll-input').value.trim();
            if(!roll) {{ alert("Enter Roll Number"); return; }}
            let student = studentsDataStore.find(s => s.roll.toLowerCase() === roll.toLowerCase());
            let area = document.getElementById('result-display-area');
            if(student) {{
                area.innerHTML = `<div style="background:#f1f5f9; padding:15px; border-radius:10px; border-left:5px solid #2563eb; font-size:14px;"><h4 style="color:#1e3a8a; margin-bottom:8px;">📄 Result Found: ${{student.name}}</h4><p><b>Roll No:</b> ${{student.roll}}</p><p><b>Total:</b> ${{student.total}}/${{student.max}} (${{student.grade}})</p><p><b>Status:</b> ${{student.status}}</p><button style="background:#1e3a8a; color:white; border:none; padding:8px 15px; border-radius:4px; margin-top:10px; cursor:pointer;" onclick="document.getElementById('resultsModal').style.display='none'; printStudent('${{student.roll}}')">🖨️ View Original Marksheet</button></div>`;
            }} else {{ 
                area.innerHTML = `<p style="color:red; font-weight:bold; text-align:center;">❌ Roll Number not found.</p>`;
            }}
        }}

        function validateSchoolLogin() {{ 
            let sId = document.getElementById('school-login-id').value.trim(); 
            let pass = document.getElementById('school-login-pass').value.trim(); 
            if(sId === "257CB" && pass === "school456") {{ 
                openPage('school-dashboard');
                document.getElementById('school-dash-title').innerText = `🏫 LAXMI NARAYAN GIRLS HIGH SCHOOL`; 
                document.getElementById('school-dash-sub').innerText = `ID: 257CB | HM: HEADMASTER`; 
                renderSchoolStudents(); 
            }} else {{ 
                alert('Invalid School ID or Password!'); 
            }} 
        }}

        function renderSchoolStudents() {{
            let tbody = document.getElementById('school-student-table-body');
            tbody.innerHTML = "";
            let classFilter = document.getElementById('school-class-filter').value;
            studentsDataStore.forEach(s => {{
                if(s.school === "LAXMI NARAYAN GIRLS HIGH SCHOOL") {{
                    if (classFilter === "ALL" || s.class_name === classFilter) {{
                        let statHtml = s.status === "Pass" ? `<span class="badge-pass">Pass ✅</span>` : `<span class="badge-fail">Fail ❌</span>`;
                        let actBtn = `<button style="background:#1e3a8a; color:white; border:none; padding:5px 8px; border-radius:4px; cursor:pointer;" onclick="printStudent('${{s.roll}}')">Print Marksheet</button>`;
                        tbody.innerHTML += `<tr><td><b>${{s.roll}}</b></td><td>${{s.name}}</td><td>${{s.class_name}}</td><td>${{s.exam_type}}</td><td><b style="color:#16a34a;">${{s.total}} / ${{s.max}}</b></td><td>${{((s.total/s.max)*100).toFixed(2)}}% (${{s.grade}})</td><td>${{statHtml}}</td><td>${{actBtn}}</td></tr>`;
                    }}
                }}
            }});
        }}

        function validateAdmin() {{ 
            let u = document.getElementById('admin-user').value.trim(); 
            let p = document.getElementById('admin-pass').value.trim(); 
            if (u === "KULU123" && p === "Admin@2026") {{ 
                openPage('admin-dashboard'); 
                renderAdminStudents();
            }} else {{ 
                alert('Invalid Admin Username or Password!'); 
            }} 
        }}

        function renderAdminStudents() {{
            let tbody = document.getElementById('admin-student-table-body');
            tbody.innerHTML = "";
            studentsDataStore.forEach(s => {{
                let actBtn = `<button style="background:#1e3a8a; color:white; border:none; padding:5px 8px; border-radius:4px; cursor:pointer;" onclick="printStudent('${{s.roll}}')">Print Marksheet</button>`;
                tbody.innerHTML += `<tr><td><b>${{s.roll}}</b></td><td>${{s.name}}</td><td>${{s.class_name}}</td><td>${{s.school}}</td><td><b style="color:#16a34a;">${{s.total}} / ${{s.max}}</b></td><td>${{actBtn}}</td></tr>`;
            }});
        }}

        function printStudent(roll) {{
            let student = studentsDataStore.find(s => s.roll === roll);
            if(!student) return;

            document.getElementById('pm-exam-title').innerText = "HIGH SCHOOL CERTIFICATE EXAMINATION - 2026";
            document.getElementById('pm-pass-text').innerHTML = "ଫେବୃଆରୀ ୨୦୨୬ ରେ ଅନୁଷ୍ଠିତ ମାଧ୍ୟମିକ ଉଚ୍ଚ ବିଦ୍ୟାଳୟ ପ୍ରମାଣପତ୍ର ପରୀକ୍ଷାରେ ଉତ୍ତୀର୍ଣ୍ଣ ହୋଇଛନ୍ତି।<br>Passed the High School Certificate Examination held in the month of February - 2026.";

            document.getElementById('pm-header-school-name').innerText = student.school || "SCHOOL NAME";
            document.getElementById('pm-school').innerText = student.school || "N/A";
            document.getElementById('pm-watermark').innerHTML = (student.school || "SCHOOL MARKSHEET").replace(/ /g, '<br>');

            document.getElementById('pm-roll').innerText = student.roll;
            document.getElementById('pm-name').innerText = student.name;
            document.getElementById('pm-fname').innerText = student.fname;
            document.getElementById('pm-mname').innerText = student.mname || "N/A";
            document.getElementById('pm-dob').innerText = student.dob || "N/A";
            document.getElementById('pm-pan').innerText = student.pan || "N/A";
            document.getElementById('pm-apar').innerText = student.apar || "N/A";
            document.getElementById('pm-class').innerText = student.class_name || "N/A";
            document.getElementById('pm-slno').innerText = student.slno || "2611220000";
            
            document.getElementById('pm-school-code').innerText = "257CB";

            document.getElementById('pm-total-max').innerText = student.max;
            document.getElementById('pm-total-sec').innerText = student.total;
            document.getElementById('pm-grade').innerText = student.grade;
            document.getElementById('pm-words').innerText = `( ${{numberToWords(student.total)}} )`;
            
            document.getElementById('pm-barcode').src = `https://barcode.tec-it.com/barcode.ashx?data=${{student.roll}}&code=Code128&translate-esc=on`;
            let qrData = `Name: ${{student.name}}%0ARoll: ${{student.roll}}%0ATotal: ${{student.total}}/${{student.max}}%0AGrade: ${{student.grade}}`;
            document.getElementById('pm-qr').src = `https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=${{qrData}}`;

            let tbody = document.getElementById('pm-marks-body'); tbody.innerHTML = "";
            if (student.subjects && student.subjects.length > 0) {{
                student.subjects.forEach(sub => tbody.innerHTML += `<tr><td>${{sub.code}}</td><td style="text-align:left; padding-left:15px;">${{sub.name}}</td><td>${{sub.max}}</td><td>${{sub.sec}}</td></tr>`);
            }} else {{ tbody.innerHTML = `<tr><td colspan="4">Marks detailed breakdown not available.</td></tr>`; }}

            let sections = document.getElementsByClassName('content-section');
            for (let sec of sections) {{ sec.classList.remove('active'); }}
            document.getElementById('home-view').style.display = 'none';
            document.getElementById('marksheet-print-area').style.display = 'block';
        }}
        
        function closePrintView() {{
            document.getElementById('marksheet-print-area').style.display = 'none'; 
            if(document.getElementById('admin-user').value === "KULU123") {{ openPage('admin-dashboard'); }} else {{ openPage('school-dashboard'); }} 
        }}

        function saveAsPDF() {{
            window.scrollTo(0, 0); 
            const element = document.getElementById('marksheet-print-area');
            const btnDiv = element.querySelector('.no-print');
            btnDiv.style.display = 'none'; 
            const opt = {{ margin: 5, filename: 'Marksheet_' + document.getElementById('pm-roll').innerText + '.pdf', image: {{ type: 'jpeg', quality: 1 }}, html2canvas: {{ scale: 2, useCORS: true, scrollY: 0, windowHeight: element.scrollHeight }}, jsPDF: {{ unit: 'mm', format: 'a4', orientation: 'portrait' }} }};
            setTimeout(() => {{ html2pdf().set(opt).from(element).save().then(() => btnDiv.style.display = 'block').catch(err => {{ btnDiv.style.display = 'block'; alert("PDF Generation Failed."); }}); }}, 500); 
        }}
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=900, scrolling=True)
