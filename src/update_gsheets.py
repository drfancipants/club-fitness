import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sqlalchemy import create_engine
from sqlalchemy import exists
import datetime
import pymysql
import json
import pdb
from sqlalchemy import Column, Text, Numeric, BigInteger, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time

GSHEET_DICT = {
    'id': 1,
    'activity_id': 2,
    'athlete': 3,
    'data_updated_at': 4,
    'elapsed_time': 5,
    'distance': 6,
    'name': 7,
    'db_creation_date': 8,
    'start_date_local': 9
}

STAT_COL_ROW = 1

def write_header(sheet):
    for key, value in GSHEET_DICT.items():
        sheet.update_cell(1, value, key)

def write_activity_entry(data, stats, row_data):
    row = int(stats.cell(2, STAT_COL_ROW).value) + 2
    for key, value in GSHEET_DICT.items():
        if key == 'distance':
            data.update_cell(row, value, float(row_data[value-1]))
        elif key == 'start_date_local':
            data.update_cell(row, value, row_data[value-1].strftime('%Y-%m-%d %H:%M:%S.%f %Z'))
        elif key == 'db_creation_date':
            data.update_cell(row, value, row_data[value-1].strftime('%Y-%m-%d %H:%M:%S.%f %Z'))            
        else:
            data.update_cell(row, value, row_data[value-1])

    stats.update_cell(2, STAT_COL_ROW, row - 1)

if __name__ == "__main__":
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('.secret/client_secret.json', scope)
    client = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet_data    = client.open("TTD Club Challenge").worksheet('activity-data')
    sheet_stats   = client.open("TTD Club Challenge").worksheet('stats')
    sheet_summary = client.open("TTD Club Challenge").worksheet('summary')
    
    # Create a database session
    with open('.secret/api_credentials.json') as json_file:
        credentials = json.load(json_file)

    # Create SQLAlchemy engine to connect to MySQL Database
    engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
			   .format(host = credentials['db_host'],
                                   db   = credentials['db_name'],
                                   user = credentials['db_user'],
                                   pw   = credentials['db_pass']))

    dbConnection = engine.connect()
    
    Session = sessionmaker(bind=dbConnection)
    session = Session()

    # Write header
    write_header(sheet_data)
    
    # Grab latest data from database
    # see if table entry already exists
    result = dbConnection.execute('SELECT * FROM club_activity')

    count = 0
    skip = 0
    for re in result:
        # See of entry exists    
        try:
            cell = sheet_data.find(str(re[GSHEET_DICT['activity_id']-1]), in_column=GSHEET_DICT['activity_id'])
            print('Entry ' + str(re[GSHEET_DICT['activity_id']-1]) + ' found in row ' + str(cell.row) + ', skipping')
            skip = skip + 1
            if not skip % 50:
                print('Skip  = ' + str(skip) + ' Pausing.') 
                time.sleep(90)
        except:
            write_activity_entry(sheet_data, sheet_stats, re)

            # pause to avoid exceeding goolge sheet quota
            count = count + 1
            if not count % 5:
                print('Count = ' + str(count) + ' Pausing.')
                time.sleep(90)
    
