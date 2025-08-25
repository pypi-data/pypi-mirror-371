from entities.monitor_state import MonitorState
import pandas as pd

def transform_to(data:list) -> MonitorState:
    result = []
    for row in data:
        result.append(MonitorState(
            Site = row[0],
            Area = row[1],
            Line = row[2],
            Station = row[3],
            State = row[4],
            StartTime = row[5],
            EndTime = row[6]
        ))
        
    return result

def transform_from(states:list[MonitorState]) -> pd.DataFrame:
    result = pd.DataFrame(columns = ["Id","Site","Area","Line","Station","State","StartTime","EndTime"])
    for state in states:
        result.append([
            state.Id,
            state.Site,
            state.Area,
            state.Line,
            state.Station,
            state.State,
            state.StartTime,
            state.EndTime
        ]
        )
        
    return result