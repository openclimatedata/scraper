import logging
import os
import pandas as pd
import sqlite3
import sys

from countrynames import to_alpha_3
from datetime import datetime

logging.basicConfig()
log = logging.getLogger("openclimatedata-scraper")
log.setLevel(logging.INFO)

treaty_collection_url = ("https://treaties.un.org/Pages/" +
                         "showDetails.aspx?objid=0800000280458f37")

# Ratification and Signature status from the UN treaty collection.
try:
    log.info("Fetching ratification data from web")
    tables = pd.read_html(treaty_collection_url, encoding="UTF-8")
except ValueError as e:
    log.error("Error: %s", e)
    log.info("Maybe https://treaties.un.org/Pages/ViewDetails.aspx?"
             "src=TREATY&mtdsg_no=XXVII-7-d&chapter=27&clang=_en is down?")
    sys.exit()

status = tables[6]
status.columns = status.loc[0]
status = status.reindex(status.index.drop(0))

status.index = status.Participant.apply(to_alpha_3, fuzzy=True)
status.index.name = "Code"

names = status.Participant.drop_duplicates()
status = status[status.Action.isin(
    ["Ratification", "Acceptance", "Approval", "Accession",
     "Signature"])]

signature = status.loc[status.Action == "Signature"]
signature = signature.rename(columns={
    "Date of Notification/Deposit": "Signature"
})
signature = pd.DataFrame(signature.Signature)

ratification = status.loc[status.Action != "Signature"]
ratification = ratification.rename(columns={
    "Action": "Kind",
    "Date of Notification/Deposit": "Ratification",
    "Date of Effect": "Date-Of-Effect"
    })

status = ratification.join(signature, how="outer")
status["Name"] = names

status = status[["Name", "Signature", "Ratification",
                 "Kind", "Date-Of-Effect"]]
status.Signature = pd.to_datetime(status.Signature, dayfirst=True)
status["Ratification"] = pd.to_datetime(
    status["Ratification"], dayfirst=True)
status["Date-Of-Effect"] = pd.to_datetime(
    status["Date-Of-Effect"], dayfirst=True)

# Add Entry Into Force date for first ratification parties.
status.loc[status["Ratification"].notnull() &
           status["Date-Of-Effect"].isnull(),
           "Date-Of-Effect"] = datetime(2016, 11, 4)

# Rename Czechia
status.Name = status.Name.replace(
    "Czech Republic", "Czechia")

conn = sqlite3.connect("data.sqlite")
status.to_sql("data", conn, if_exists="replace")
log.info("Wrote data to database")
