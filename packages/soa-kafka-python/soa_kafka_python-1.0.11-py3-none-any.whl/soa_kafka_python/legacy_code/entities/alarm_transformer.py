'''
Descripttion: 
version: 
Author: Author
Date: 2023-07-03 11:10:22
LastEditors: Author
LastEditTime: 2023-07-12 11:09:54
'''
from entities.alarm import Alarm
import pandas as pd

def transform_to(data:list) -> Alarm:
    result = []
    for row in data:
        result.append(Alarm(
            Site = row[0],
            Area = row[1],
            Line = row[2],
            Station = row[3],
            AlarmType = row[4],
            ReminderType = row[5],
            AlarmContent = row[6],
            Severity = int(row[7]),
            EventTime = row[8],
            CreatedTime = row[9]
        ))
        
    return result

def transform_from(alarms:list[Alarm]) -> pd.DataFrame:
    result = pd.DataFrame(columns = ["Site","Area","Line","Station","AlarmType","ReminderType","AlarmContent","Severity","EventTime","CreatedTime"])
    for alarm in alarms:
        result.append([
            alarm.Site,
            alarm.Area,
            alarm.Line,
            alarm.Station,
            alarm.AlarmType,
            alarm.ReminderType,
            alarm.AlarmContent,
            alarm.Severity,
            alarm.EventTime,
            alarm.CreatedTime
        ]
        )
        
    return result