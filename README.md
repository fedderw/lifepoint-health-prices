# hospital-price-transparency-v2
This is our second pass at a Hospital Price Transparency dataset. To recap, on January 1, 2021, a US law was passed  forcing hospitals to publish their prices in human and machine readable format. We would like to assemble the best open dataset of hospital prices in the US to aid researchers and curious dilettantes alike.

# The Database
There are three tables participants are most likely to want to modify, hospitals, procedures, and prices.

# Hospitals table
The hospitals table is unchanged from version 1, and the data from that first version has been imported in advance. As part of the data gathered in the first version of the bounty was the chargematster URL, you can use this data to assist you in populating this second database.

* `npi_number`, the primary key
* `name`
* `url`
* `street_address`
* `city`
* `state`
* `zip_code`
* `publish_date`

# `Procedures` table
The one change here is that  npi_number is now part of the primary key, making procedures hospital specific. This used to be the cpt_hcpcs table.

* `code`, a CPT or HCPCS code
* `npi_number`, the 10 digit national provider identifier for the corresponding hospital and name is the name is the name of the hospital.
* `short_description`, which is up to 128 characters
* `long_description`, which is up to 2048 characters
The primary key is (code, npi_number).

Prices table
Three fields were added to the prices table IP_OP, caveat, and mode

* `code`, the CPT or HCPCS code from the procedures table (foreign constraint)
* `npi_number`, the npi number from the hospitals table (foreign constraint)
* `payer`
* `IP_OP`, takes on values “INPATIENT”, “OUTPATIENT”, or “UNSPECIFIED”
* `caveat`, the type of insurance plan, such as “HMO”, “PPO”, or “INDEMNITY”
* `mode`, additional information about how the price was reported, example values are “MAXIMUM”, “MINIMUM”, or “EXPECTED”
* `price`

Additional tables
There are four more tables that participants shouldn’t have to modify, these are `payers`, `modes`, `caveats`, and `IP_OPs`. They contain the legal values for their respective fields. If you need to modify any of these it’s probably best to fly it past us in the Discord. Happy Hacking!