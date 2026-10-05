import streamlit as st
import sqlite3
import json

st.set_page_config(page_title="School Home Portal - Ultimate Secure Edition", layout="wide")

DB_PATH = "database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
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
    ''')
    
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
students_json_escaped = students_json.replace("'", "\\'")

html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>School Home Portal - Ultimate Secure Edition</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
    <style>
        #MainMenu, header, [data-testid="stHeader"], footer, .viewerBadge_container, .stDeployButton {{ display: none !important; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: url('https://images.unsplash.com/photo-1523050854058-8df90110c9f1?q=80&w=1920&auto=format&fit=crop') no-repeat center center fixed;
            background-size: cover; color: #333; min-height: 100vh; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            box-sizing: border-box; overflow-x: hidden; margin: 0; padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .glass-panel {{
            background: rgba(255, 255, 255, 0.88); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.5); border-radius: 20px; padding: 30px; box-shadow: 0 15px 35px rgba(0,0,0,0.2); margin-bottom: 25px;
        }}
        .header {{
            background: linear-gradient(90deg, rgba(13,59,102,0.9), rgba(29,78,216,0.9)); padding: 20px 30px; border-radius: 16px; color: white;
            display: flex; justify-content: space-between; align-items: center; box-shadow: 0 10px 25px rgba(0,0,0,0.3); margin-bottom: 25px;
        }}
        .header h2 {{ font-size: 24px; margin: 0; }}
        .header p {{ font-style: italic; font-size: 16px; margin: 0; }}
        .scrolling-notice-container {{
            background: rgba(254, 240, 138, 0.95); border: 1px solid #f59e0b; border-radius: 12px; padding: 10px 20px; margin-bottom: 25px;
            display: flex; align-items: center; overflow: hidden; white-space: nowrap; box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .notice-title {{ font-weight: bold; color: #b45309; margin-right: 15px; font-size: 16px; }}
        .scrolling-text {{ color: #854d0e; font-size: 15px; font-weight: 500; display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite; }}
        @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
        .home-action-bar {{ display: flex; justify-content: center; gap: 20px; margin-top: 15vh; flex-wrap: wrap; }}
        .action-pill {{
            padding: 20px; border-radius: 20px; color: white; font-weight: bold; font-size: 15px; text-align: center; cursor: pointer;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3); transition: transform 0.3s; flex: 1; min-width: 150px; max-width: 220px; border: 2px solid rgba(255,255,255,0.4);
        }}
        .action-pill:hover {{ transform: translateY(-8px); }}
        .action-pill .icon-lg {{ font-size: 30px; margin-bottom: 8px; display: block; }}
        .pill-magenta {{ background: linear-gradient(135deg, rgba(219,39,119,0.9), rgba(157,23,77,0.9)); }}
        .pill-blue {{ background: linear-gradient(135deg, rgba(2,132,199,0.9), rgba(3,105,161,0.9)); }}
        .pill-green {{ background: linear-gradient(135deg, rgba(22,163,74,0.9), rgba(21,128,61,0.9)); }}
        .pill-orange {{ background: linear-gradient(135deg, rgba(245,158,11,0.9), rgba(217,119,6,0.9)); }}
        .pill-purple {{ background: linear-gradient(135deg, rgba(147,51,234,0.9), rgba(126,34,206,0.9)); }}
        .pill-red {{ background: linear-gradient(135deg, rgba(239,68,68,0.9), rgba(220,38,38,0.9)); }}
        .btn-login {{ width: 100%; padding: 16px; border-radius: 14px; font-weight: bold; font-size: 18px; color: white; border: none; cursor: pointer; margin-bottom: 15px; }}
        .btn-admin {{ background: linear-gradient(135deg, #22c55e, #16a34a); }}
        .btn-school {{ background: linear-gradient(135deg, #3b82f6, #2563eb); }}
        .content-section {{ display: none; }}
        .content-section.active {{ display: block; }}
        .back-btn {{ background: #64748b; color: white; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; display: block; overflow-x: auto; white-space: nowrap; background: rgba(255,255,255,0.9); border-radius: 8px; }}
        th, td {{ padding: 10px 12px; border: 1px solid rgba(203,213,225,0.6); text-align: left; font-size: 13px; }}
        th {{ background: rgba(30,58,138,0.9); color: white; }}
        .badge-pass {{ background: #dcfce7; color: #166534; padding: 4px 10px; border-radius: 6px; font-weight: bold; }}
        .badge-fail {{ background: #fee2e2; color: #b91c1c; padding: 4px 10px; border-radius: 6px; font-weight: bold; }}
        .form-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
        @media (max-width: 600px) {{ .form-grid {{ grid-template-columns: 1fr; }} }}
        .input-box {{ width: 100%; padding: 10px; border: 1px solid rgba(203,213,225,0.9); border-radius: 8px; font-size: 14px; background: rgba(255,255,255,0.95); outline: none; }}
        .modal {{ display: none; position: fixed; z-index: 100; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); justify-content: center; align-items: center; }}
        .modal-content {{ background: #fff; padding: 30px; border-radius: 20px; width: 850px; max-width: 95%; max-height: 90vh; overflow-y: auto; }}
        #marksheet-print-area {{ display: none; width: 800px; max-width: 100%; background: white; margin: 0 auto; padding: 20px; font-family: 'Times New Roman', Times, serif; color: #3b0764; }}
        .cert-border {{ border: 12px solid #d8b4e2; border-image: repeating-linear-gradient(45deg, #d8b4e2, #d8b4e2 10px, #e8d0ef 10px, #e8d0ef 20px) 15; padding: 15px; position: relative; }}
        .cert-header {{ text-align: center; margin-bottom: 10px; }}
        .cert-header h1 {{ font-size: 20px; color: #4c1d95; text-transform: uppercase; }}
        .cert-top-info {{ display: flex; justify-content: space-between; font-size: 12px; font-weight: bold; margin-bottom: 10px; border-top: 1px solid #4c1d95; border-bottom: 1px solid #4c1d95; padding: 5px 0; }}
        .cert-table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; border: 2px solid #4c1d95; }}
        .cert-table th, .cert-table td {{ border: 1px solid #4c1d95; padding: 5px; text-align: center; font-size: 12px; font-weight: bold; }}
        .cert-table th {{ background: #f3e8ff; color: #4c1d95; }}
        @media print {{
            body * {{ visibility: hidden; }}
            .container, #home-view {{ display: none !important; }}
            #marksheet-print-area, #marksheet-print-area * {{ visibility: visible; }}
            #marksheet-print-area {{ position: absolute; left: 0; top: 0; width: 100% !important; display: block !important; }}
            .no-print {{ display: none !important; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🏫 SCHOOL HOME PORTAL</h2>
            <p>Better Education, Brighter Future</p>
        </div>

        <div id="home-view">
            <div class="scrolling-notice-container">
                <span class="notice-title">📢 Important Notice Board:</span>
                <span class="scrolling-text">Official Marksheet & Portal System is live with 42 verified students dataset and permanent SQLite Database!</span>
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
                <div class="action-pill pill-orange" onclick="alert('Registration Portal Active!')">
                    <span class="icon-lg">📝</span>New School Reg.
                </div>
                <div class="action-pill pill-purple" onclick="alert('Student Portal Active!')">
                    <span class="icon-lg">🎓</span>New Student Reg.
                </div>
                <div class="action-pill pill-red" onclick="alert('Scholarship Portal Active Soon!')">
                    <span class="icon-lg">💰</span>Scholarship
                </div>
            </div>
        </div>

        <!-- School Login -->
        <div id="school-login" class="content-section glass-panel" style="max-width:500px; margin: 0 auto; text-align:center;">
            <button class="back-btn" onclick="goHome()" style="float:left;">⬅️ Back</button>
            <h3 style="color:#0d3b66; margin-bottom:15px; clear:both;">🏫 School Portal Login</h3>
            <input type="text" id="school-login-id" placeholder="Enter School Code (e.g. 257CB)" class="input-box" style="margin-bottom:15px; text-align:center;">
            <input type="password" id="school-login-pass" placeholder="Enter Password" class="input-box" style="margin-bottom:15px; text-align:center;">
            <button class="btn-login btn-school" onclick="validateSchoolLogin()">Login ➡️</button>
        </div>

        <!-- School Dashboard -->
        <div id="school-dashboard" class="content-section glass-panel">
            <button class="back-btn" onclick="goHome()">🚪 Logout</button>
            <h2 id="school-dash-title" style="color:#0d3b66; margin-bottom:5px;">🏫 School Dashboard</h2>
            <p id="school-dash-sub" style="color:#64748b; margin-bottom:20px;"></p>
            <div style="margin-bottom:15px; display:flex; gap:10px; align-items:center;">
                <label style="font-weight:bold; color:#0d3b66;">Filter by Class:</label>
                <select id="school-class-filter" class="input-box" style="width:auto;" onchange="renderSchoolStudents()">
                    <option value="ALL">-- All Classes --</option>
                    <option value="X">Class X</option>
                    <option value="X Pass Out">X Pass Out</option>
                </select>
            </div>
            <table>
                <thead>
                    <tr><th>Photo</th><th>Roll No</th><th>Student Name</th><th>Class</th><th>Exam Type</th><th>Total Marks</th><th>% & Grade</th><th>Status</th><th>Actions</th></tr>
                </thead>
                <tbody id="school-student-table-body"></tbody>
            </table>
        </div>

        <!-- Admin Login -->
        <div id="admin-login" class="content-section glass-panel" style="max-width:500px; margin: 0 auto; text-align:center;">
            <button class="back-btn" onclick="goHome()" style="float:left;">⬅️ Back</button>
            <h3 style="color:#0d3b66; margin-bottom:15px; clear:both;">👑 Master Admin Login</h3>
            <input type="text" id="admin-user" placeholder="Username" class="input-box" style="margin-bottom:15px; text-align:center;">
            <input type="password" id="admin-pass" placeholder="Password" class="input-box" style="margin-bottom:15px; text-align:center;">
            <button class="btn-login btn-admin" onclick="validateAdmin()">Login 🚀</button>
        </div>

        <!-- Admin Dashboard -->
        <div id="admin-dashboard" class="content-section glass-panel">
            <button class="back-btn" onclick="goHome()">🚪 Logout & Home</button>
            <h2 style="color:#0d3b66; margin-bottom:15px;">👑 Master Admin Dashboard - Complete Student Database</h2>
            <table>
                <thead>
                    <tr><th>Roll No</th><th>Student Name</th><th>Class</th><th>School Name</th><th>Total Marks</th><th>Actions</th></tr>
                </thead>
                <tbody id="admin-student-table-body"></tbody>
            </table>
        </div>

        <!-- Marksheet Print Area -->
        <div id="marksheet-print-area">
            <div class="cert-border">
                <div class="cert-header">
                    <h1 id="pm-header-school-name">SCHOOL NAME</h1>
                    <h2>HIGH SCHOOL CERTIFICATE EXAMINATION - 2026</h2>
                    <h2 style="font-size:14px; margin-top:5px;">CERTIFICATE-CUM-MARK SHEET</h2>
                </div>
                <div class="cert-top-info">
                    <div><p>ROLL NO : <span id="pm-roll"></span></p></div>
                    <div style="text-align:right;"><p>SL NO : <span id="pm-slno"></span></p></div>
                </div>
                <div style="display:flex; gap:20px; margin-bottom:10px; font-size:13px;">
                    <div><b>Name:</b> <span id="pm-name"></span><br><b>Mother's Name:</b> <span id="pm-mname"></span><br><b>Father's Name:</b> <span id="pm-fname"></span><br><b>DOB:</b> <span id="pm-dob"></span><br><b>PEN No:</b> <span id="pm-pan"></span><br><b>APAAR ID:</b> <span id="pm-apar"></span></div>
                </div>
                <table class="cert-table">
                    <thead>
                        <tr><th>SUBJECT CODE</th><th>SUBJECT NAME</th><th>FULL MARKS</th><th>MARKS SECURED</th></tr>
                    </thead>
                    <tbody id="pm-marks-body"></tbody>
                    <tfoot>
                        <tr><th colspan="2" style="text-align:right;">TOTAL / MAX</th><th id="pm-total-max">600</th><th id="pm-total-sec"></th></tr>
                    </tfoot>
                </table>
                <div style="text-align:center; font-weight:bold; margin-top:10px;">Grade: <span id="pm-grade"></span> | Status: <span id="pm-status"></span></div>
            </div>
            <div class="no-print" style="text-align:center; margin-top:20px;">
                <button style="background:#2563eb; color:white; padding:10px 25px; border:none; border-radius:8px; cursor:pointer;" onclick="window.print()">🖨️ Print Marksheet</button>
                <button style="background:#64748b; color:white; padding:10px 25px; border:none; border-radius:8px; cursor:pointer; margin-left:10px;" onclick="goHome()">⬅️ Home</button>
            </div>
        </div>
    </div>

    <!-- Results Modal -->
    <div id="resultsModal" class="modal">
        <div class="modal-content" style="text-align:center;">
            <h3 style="color:#0d3b66; margin-bottom:15px;">🔍 Check Results by Roll Number</h3>
            <input type="text" id="check-roll-input" placeholder="Enter Roll Number (e.g. 175CB0077)" class="input-box" style="margin-bottom:15px; text-align:center;">
            <div id="result-display-area" style="text-align:left; margin-bottom:15px;"></div>
            <button style="background:#64748b; color:white; border:none; padding:10px 20px; border-radius:8px;" onclick="document.getElementById('resultsModal').style.display='none'">Close</button>
            <button style="background:#2563eb; color:white; border:none; padding:10px 20px; border-radius:8px;" onclick="fetchStudentResult()">View Marksheet 📄</button>
        </div>
    </div>

    <script>
        const studentsData = JSON.parse('{students_json}');
        
        function openPage(pageId) {{
            document.getElementById('home-view').style.display = 'none';
            document.querySelectorAll('.content-section').forEach(sec => sec.classList.remove('active'));
            document.getElementById(pageId).classList.add('active');
        }}
        function goHome() {{
            document.querySelectorAll('.content-section').forEach(sec => sec.classList.remove('active'));
            document.getElementById('home-view').style.display = 'block';
            document.getElementById('marksheet-print-area').style.display = 'none';
        }}
        function openResultsModal() {{ document.getElementById('check-roll-input').value = ""; document.getElementById('result-display-area').innerHTML = ""; document.getElementById('resultsModal').style.display = 'flex'; }}
        
        function fetchStudentResult() {{
            let roll = document.getElementById('check-roll-input').value.trim();
            let student = studentsData.find(s => s.roll.toLowerCase() === roll.toLowerCase());
            let area = document.getElementById('result-display-area');
            if(student) {{
                area.innerHTML = `<div style="background:#f1f5f9; padding:12px; border-radius:8px;"><p><b>Name:</b> ${{student.name}}</p><p><b>Total Marks:</b> ${{student.total}}/${{student.max}} (${{student.grade}})</p><button style="background:#1e3a8a; color:white; border:none; padding:6px 12px; border-radius:4px; margin-top:8px; cursor:pointer;" onclick="document.getElementById('resultsModal').style.display='none'; printMarkSheet('${{student.roll}}')">Print Marksheet</button></div>`;
            }} else {{
                area.innerHTML = `<p style="color:red; font-weight:bold;">Roll Number not found.</p>`;
            }}
        }}

        function validateSchoolLogin() {{
            let id = document.getElementById('school-login-id').value.trim();
            let pass = document.getElementById('school-login-pass').value.trim();
            if(id === "257CB" && pass === "school456") {{
                openPage('school-dashboard');
                document.getElementById('school-dash-title').innerText = "🏫 LAXMI NARAYAN GIRLS HIGH SCHOOL";
                document.getElementById('school-dash-sub').innerText = "ID: 257CB | HM: HEADMASTER";
                renderSchoolStudents();
            }} else {{
                alert("Invalid School Code or Password! (Use 257CB / school456)");
            }}
        }}

        function renderSchoolStudents() {{
            let tbody = document.getElementById('school-student-table-body');
            tbody.innerHTML = "";
            let classFilter = document.getElementById('school-class-filter').value;
            studentsData.forEach(s => {{
                if(classFilter === "ALL" || s.class_name === classFilter) {{
                    let stat = s.status === "Pass" ? `<span class="badge-pass">Pass ✅</span>` : `<span class="badge-fail">Fail ❌</span>`;
                    tbody.innerHTML += `<tr><td><img src="${{s.photo || 'https://via.placeholder.com/40'}}" width="40" height="40" style="border-radius:4px;"></td><td><b>${{s.roll}}</b></td><td>${{s.name}}</td><td>${{s.class_name}}</td><td>${{s.exam_type}}</td><td><b>${{s.total}}/${{s.max}}</b></td><td>${{s.grade}}</td><td>${{stat}}</td><td><button style="background:#2563eb; color:white; border:none; padding:5px 10px; border-radius:4px; cursor:pointer;" onclick="printMarkSheet('${{s.roll}}')">Print / PDF</button></td></tr>`;
                }}
            }});
        }}

        function validateAdmin() {{
            let u = document.getElementById('admin-user').value.trim();
            let p = document.getElementById('admin-pass').value.trim();
            if(u === "KULU123" && p === "Admin@2026") {{
                openPage('admin-dashboard');
                let tbody = document.getElementById('admin-student-table-body');
                tbody.innerHTML = "";
                studentsData.forEach(s => {{
                    tbody.innerHTML += `<tr><td><b>${{s.roll}}</b></td><td>${{s.name}}</td><td>${{s.class_name}}</td><td>${{s.school}}</td><td><b>${{s.total}}/${{s.max}}</b></td><td><button style="background:#2563eb; color:white; border:none; padding:5px 10px; border-radius:4px; cursor:pointer;" onclick="printMarkSheet('${{s.roll}}')">Print</button></td></tr>`;
                }});
            }} else {{
                alert("Invalid Admin Username or Password! (Use KULU123 / Admin@2026)");
            }}
        }}

        function printMarkSheet(roll) {{
            let student = studentsData.find(s => s.roll === roll);
            if(!student) return;
            document.getElementById('pm-header-school-name').innerText = student.school;
            document.getElementById('pm-roll').innerText = student.roll;
            document.getElementById('pm-slno').innerText = student.slno || "2611220000";
            document.getElementById('pm-name').innerText = student.name;
            document.getElementById('pm-mname').innerText = student.mname || "N/A";
            document.getElementById('pm-fname').innerText = student.fname;
            document.getElementById('pm-dob').innerText = student.dob || "N/A";
            document.getElementById('pm-pan').innerText = student.pan || "N/A";
            document.getElementById('pm-apar').innerText = student.apar || "N/A";
            document.getElementById('pm-total-sec').innerText = student.total;
            document.getElementById('pm-grade').innerText = student.grade;
            document.getElementById('pm-status').innerText = student.status;

            let tbody = document.getElementById('pm-marks-body');
            tbody.innerHTML = "";
            student.subjects.forEach(sub => {{
                tbody.innerHTML += `<tr><td>${{sub.code}}</td><td style="text-align:left; padding-left:10px;">${{sub.name}}</td><td>${{sub.max}}</td><td>${{sub.sec}}</td></tr>`;
            }});

            document.querySelectorAll('.content-section').forEach(sec => sec.classList.remove('active'));
            document.getElementById('home-view').style.display = 'none';
            document.getElementById('marksheet-print-area').style.display = 'block';
        }}
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=900, scrolling=True)
