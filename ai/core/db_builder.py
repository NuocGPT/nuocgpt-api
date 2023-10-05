import csv 
from ai.schemas.db_model import SensorDataLib
import datetime

async def db_builder():
    with open('sensordata.csv', 'r', encoding='utf-8') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            try:
                time = datetime.strptime(row[7], '%Y-%m-%d %H:%M:%S')
            except:
                time = datetime.strptime(row[7], '%Y-%m-%d')
            sensor_data = SensorDataLib(
                                id=row[0],
                                question=row[1],
                                answer=row[2],
                                parameter=row[3],
                                location=row[4],
                                value=float(row[5]),
                                unit=row[6],
                                time=time
                            )
        await sensor_data.create()