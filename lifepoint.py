import pandas as pd
import numpy as np
import json
import csv
import chardet
# import requests
# import seaborn as sns
# import matplotlib as plt
# import urllib.request, json
from collections import OrderedDict, defaultdict
import xml.etree.ElementTree as ET

from pandas_read_xml import flatten, fully_flatten, auto_separate_tables
import pandas_read_xml as pdx

batch1=pd.read_csv('lifepoint_batch_1.csv')
batch1.npi

xmls={'1063713659': '27-3633811_CLINTON_MEMORIAL_HOSPITAL_StandardCharges.xml',
 '1801897038': '611739000_Conemaugh_Health_System_Standard_Charges_12282020.xml',
 '1881726347': '473937528_Fleming_County_Hospital_Standard_Charges_12202020.xml',
 '1780761866': '205220956 Havasu Regional Medical Center Standard Charges 12152020.xml',
 '1396760542': '621762419_Livingston_Regional_Hospital_Standard_Charges_12192020.xml',
 '1831284280': '36-4850536_LOURDES_HEALTH_StandardCharges.xml',
 '1386720183': '202028539_Sovah_Health_Martinsville_Standard_Charges_12182020.xml',
 '1497708473': '472546387_Nason_Hospital_Standard_Charges_12202020.xml',
 '1477874337': '27-2451336_NORTH_ALABAMA_MEDICAL_CENTER_StandardCharges.xml',
 '1699096552': '27-2451336_SHOALS_HOSPITAL_StandardCharges.xml',
 '1326113762': '742791525 Palestine Regional Medical Center Standard Charges 12162020.xml',
 '1881977593': '452909143 Person Memorial Standard Charges 12152020.xml',
 '1922319037': '621762469_Riverview_Regional_Medical_Center_Standard_Charges_12182020.xml',
 '1245321181': '300811171_Rutherford_Regional_Medical_Center_Standard_Charges_12202020.xml',
 '1396842308': '621762468_Sage_West_Standard_Charges_12192020.xml',
 '1154419737': '202028539_Sovah_Health_Danville_Standard_Charges_12182020.xml',
 '1033160049': '62-1771866_SAINT_MARYS_REGIONAL_HEALTH_SYSTEM_StandardCharges.xml',
 '1134480155': '621866028_Athens_Woods_Starr_Regional_Standard_Charges_12192020.xml',
 '1467763458': '272618876_Trousdale_Medical_Center_Standard_Charges_12192020.xml',
 '1811086994': '320063628_Valley_View_Medical_Center_Standard_Charges_12192020.xml',
 '1336231232': '611275266 Western Plains Medical Complex Standard Charges 12152020.xml'}
path='lifepoint_xmls'
for k, v in xmls.items():
    xmls[k]=path+"/"+xmls[k]