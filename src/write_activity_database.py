from sqlalchemy import create_engine
from sqlalchemy import exists
import datetime
import pandas as pd
import pymysql
import json
import pdb
from sqlalchemy import Column, Text, Numeric, BigInteger, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
Base = declarative_base()

class Activity(Base):
    __tablename__ = 'club_activity'
    id=Column(Integer, primary_key=True)
    created_date=Column(DateTime, default=datetime.datetime.utcnow)
    activity_id=Column('activityID', BigInteger)
    athlete=Column('athlete', Text)
    data_updated_at=Column('data_updated_at', BigInteger)
    elapsed_time=Column('elapsed_time', Integer)
    distance = Column('distance', Numeric)
    name=Column('name', Text)
    start_date_local=Column('start_date_local', DateTime)

    #----------------------------------------------------------------------
    def __init__(self,
                 activity_id,
                 athlete,
                 data_updated_at,
                 elapsed_time,
                 distance,
                 name,
                 start_date_local):
        """"""
        self.activity_id = activity_id
        self.athlete = athlete
        self.data_updated_at = data_updated_at
        self.elapsed_time = elapsed_time
        self.distance = distance
        self.name = name
        self.start_date_local = start_date_local

    
if __name__ == "__main__":
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

    strava_df = pd.read_csv('strava_activities.csv')

    for index, row in strava_df.iterrows():

        # see if table entry already exists
        result = dbConnection.execute('SELECT * FROM club_activity WHERE activityID = ' + str(row['id']))

        if result.first() is None:

            if(row.isnull().any()):
                print('Null Entry Found, skipping')

            else:
                dt = datetime.datetime.strptime(row['start_date_local'], '%Y-%m-%d %H:%M:%S %Z')
        
                activity = Activity(row['id'],
                                    row['athlete'],
                                    row['data-updated-at'],
                                    row['elapsed_time'],
                                    row['distance'],
                                    row['name'],
                                    dt)
            
                session.add(activity)

                print('Added entry ' + str(row['id']) + ' for ' + str(row['athlete']))

        else:
            print('Entry ' + str(row['id']) + ' exists, skipping')

            
        #pdb.set_trace()

        session.commit()
        

    
    



