# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pandas as pd
import numpy as np
import json
import csv
import urllib.request, json
from collections import OrderedDict, defaultdict
from pandas_read_xml import flatten, fully_flatten, auto_separate_tables
import pandas_read_xml as pdx


# %%
# define dictionary for hospital npi number: file location
xmls = {
    "1063713659": "lifepoint_xmls/27-3633811_CLINTON_MEMORIAL_HOSPITAL_StandardCharges.xml",
    "1831284280": "lifepoint_xmls/36-4850536_LOURDES_HEALTH_StandardCharges.xml",
    "1477874337": "lifepoint_xmls/27-2451336_NORTH_ALABAMA_MEDICAL_CENTER_StandardCharges.xml",
    "1699096552": "lifepoint_xmls/27-2451336_SHOALS_HOSPITAL_StandardCharges.xml",
    "1033160049": "lifepoint_xmls/62-1771866_SAINT_MARYS_REGIONAL_HEALTH_SYSTEM_StandardCharges.xml",
}


# %%

for npi_number, raw_xml in xmls.items():
    # read xml from path and unpack xml tree
    df = pdx.read_xml(
        pdx.read_xml_from_path(raw_xml, "utf8"),
        ["StandardCharges", "Facility"],
    )

    # add column for npi number
    df["npi_number"] = npi_number

    # flatten the xml tree structure to get code, description, and standard charges
    for i in range(6):
        df = df.pipe(flatten)

    def col_clean(data):
        """clean column names of pd dataframe"""

        data.columns = (
            data.columns.str.lower()
            .str.replace(" ", "_", regex=False)
            .str.replace("-", "_", regex=False)
            .str.replace("@", "", regex=False)
            .str.replace("|", "_", regex=False)
        )
        return data

    # clean columns
    df = col_clean(df)

    # create dictionary of xml names to column names
    COLSDICT = {
        "name": "name",
        # these will go to procedures table
        "patient_charge_item_code": "code",
        "patient_charge_item_description": "long_description",
        # these are de-identified prices which will be processed separetly
        # from payer negotiated prices
        "patient_charge_item_discountcashcharge": "self_pay",
        "patient_charge_item_grosscharge": "gross",
        "patient_charge_item_maxnegotiatedcharge": "max",
        "patient_charge_item_minnegotiatedcharge": "min",
        # payer negotiated prices
        "patient_charge_item_contracts_contract_charge": "price",
        "patient_charge_item_contracts_contract_payer": "payer",
    }

    # TODO maybe we've done this wrong?
    # select only CPT/HCPCS codes
    df = df[df["patient_charge_type"] == "HCPCS"]
    df = df.dropna(subset=["patient_charge_item_code"])

    # define hospital name, for debugging
    name = df.name.max()
    lower_name = (
        df.name.str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
        .str.replace("@", "", regex=False)
        .str.replace("|", "_", regex=False)
        .max()
    )

    # remove commas from prices and make numeric
    df[
        [
            "patient_charge_item_discountcashcharge",
            "patient_charge_item_grosscharge",
            "patient_charge_item_maxnegotiatedcharge",
            "patient_charge_item_minnegotiatedcharge",
        ]
    ] = (
        df[
            [
                "patient_charge_item_discountcashcharge",
                "patient_charge_item_grosscharge",
                "patient_charge_item_maxnegotiatedcharge",
                "patient_charge_item_minnegotiatedcharge",
            ]
        ]
        .replace({",": ""}, regex=False)
        .apply(pd.to_numeric, 1)
    )
    # rename columns
    df.rename(columns=COLSDICT, inplace=True)

    # due to primary key constaints in the dolt db, we need to add ',1' then ',2' etc.
    # for any duplicate procedure/description combinations. hospitals will often
    # use different description for procedures in different circumstances that still use the same'
    # category I/II cpt code
    incremented = df["code"].copy()

    counter = defaultdict(int)
    for k, v in incremented.items():
        counter[v] += 1
        if counter[v] > 1:
            pre = v
            post = str("," + str(counter[v] - 1))
            incremented[k] = "%s%s" % (pre, post)

    # replace code column with new incremented version
    df["code"] = incremented

    # ----------------------------- procedures table ----------------------------- #

    # create procedures df to create csv which will map to procedures table in DB
    procedures = df[["code", "npi_number", "long_description"]].copy()
    procedures["short_description"] = np.nan

    # clean

    # set columns in right order
    PROC_COLS = ["code", "npi_number", "short_description", "long_description"]

    procedures = procedures[PROC_COLS]

    # create procedures csv
    new_filename = "procedures\\" + lower_name + "_" + str(npi_number) + ".csv"
    procedures.to_csv(new_filename, index=False)

    # --------------------------- de-identified charges -------------------------- #
    # select only payer-non specific charge info
    CHARGE_COLS = [
        "npi_number",
        "code",
        # "short_description",
        "self_pay",
        "gross",
        "max",
        "min",
    ]
    # create df to convert deidentified charges to prices table
    charges = df[CHARGE_COLS].copy()
    # rename columns
    charges.rename(columns=COLSDICT, inplace=True)

    # melt charges
    def clean_melted_charges(dataframe):
        """used specifically to conver the metled non-payer specific charges to match prices schema"""

        # do the melting
        dataframe = dataframe.melt(id_vars=["npi_number", "code"], value_name="price")
        # set marker for inpatient & outpaitent prices
        dataframe["IP_OP"] = "UNSPECIFIED"
        dataframe["payer"] = "UNSPECIFIED"
        dataframe["caveat"] = "NONE"
        dataframe["mode"] = np.NaN

        def replace_value(col, value_dict):
            for k, v in value_dict.items():
                dataframe.loc[dataframe.variable == k, col] = v

        # define melted variable name : variable new value
        payers = {
            "gross": "Gross Charge",
            "self_pay": "Discounted Cash Charge",
            "min": "De-identifiedMin",
            "max": "De-identifiedMax",
        }
        # replace payers with the above dict
        replace_value("payer", payers)

        # define melted variable name : variable new value
        modes = {
            "gross": "GROSS",
            "self_pay": "MINIMUM",
            "min": "MAXIMUM",
            "max": "EXPECTED",
        }
        # replace modes with the above dict
        replace_value("mode", modes)

        # return dataframe
        return dataframe[
            [
                "code",
                "npi_number",
                "payer",
                "IP_OP",
                "caveat",
                "mode",
                "price",
            ]
        ]

    new_charges = clean_melted_charges(charges)

    # ------------------------ clean data for prices table ----------------------- #
    # # flatten the xml tree structure to get payer and charge out to each row
    for i in range(4):
        # print(df.columns)
        df = df.pipe(flatten)

    # clean newly flattened columns
    df = col_clean(df)
    # rename columns
    df.rename(columns=COLSDICT, inplace=True)

    # remove commas from prices and make numeric
    df["price"] = df["price"].replace({",": ""}, regex=False).apply(pd.to_numeric, 1)

    # drop unnecessary columns
    df.drop(
        columns=[
            # "short_description",
            "long_description",
            # "patient_charge_item_dept",
            "self_pay",
            "gross",
            "max",
            "min",
            # "patient_charge_item_note",
            "patient_charge_item_qtytype",
            "patient_charge_type",
            "createddate",
            # "disclaimer",
        ],
        inplace=True,
    )

    # add nans as caveat
    df["IP_OP"] = "UNSPECIFIED"
    df["mode"] = "EXPECTED"
    df["caveat"] = "NONE"

    prices = pd.concat(
        [
            df[["code", "npi_number", "payer", "IP_OP", "caveat", "mode", "price"]],
            new_charges,
        ]
    )
    # create prices csv
    new_filename = "prices\\" + lower_name + "_" + str(npi_number) + ".csv"
    prices.to_csv(new_filename, index=False)

    # create csv for unique payers to upload as PK of `payers` table, which is FK of `prices`
    new_filename = "payers\\" + lower_name + "_" + str(npi_number) + ".csv"
    payers = pd.DataFrame(prices.payer.unique())
    payers.columns = ["payer"]
    payers.to_csv(new_filename, index=False)

    print(
        "\n succesful: "
        + name
        + " - "
        + str(npi_number)
        + " price nrows: "
        + str(len(prices))
    )
