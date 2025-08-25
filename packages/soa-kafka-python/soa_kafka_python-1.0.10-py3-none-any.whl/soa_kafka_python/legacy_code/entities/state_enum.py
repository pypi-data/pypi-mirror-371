from enum import Enum

class StateEnum(Enum):
    Filling_Sampling = 0
    CPE_Second_Filtration_Remind_Start = 1
    CPE_Second_Filtration_Filter_Checked = 2
    CPE_Second_Filtration_Remind_End = 3