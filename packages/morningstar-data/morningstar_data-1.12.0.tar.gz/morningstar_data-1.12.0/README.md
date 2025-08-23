# Morningstar Data Package

The morningstar_data Python package provides users quick programmatic access to Morningstar data. It is a building block for doing practical investment data analysis in Python.

# Getting Started

## Installation

### Installing via pip
```
pip install morningstar-data
```

### Installing via conda
```
conda install -c conda-forge morningstar-data
```

**Warning**: Importing the package before authenticating will produce an error. See below for authentication steps.

## Authentication
### Retrieve Authentication Token
1. Open [Analytics Lab](https://analyticslab.morningstar.com/) in your browser
2. Login with your Morningstar Direct credentials
3. On the top ribbon in the "Analytics Lab" dropdown menu select "Copy Authentication Token". This will copy your token to the clipboard.

![copy auth token](https://docs-analyticslab.morningstar.com/latest/_static/copy_auth_token.png)

### Set Authentication Token
Set the environment variable `MD_AUTH_TOKEN` using the token you retrieved previously
#### Bash

`export MD_AUTH_TOKEN="paste copied token here"`

#### Within a Python (.py) File

```
# testing_morningstar_data.py
import os
import morningstar_data as md

os.environ['MD_AUTH_TOKEN']="paste copied token here"

md.direct.get_morningstar_data_sets()
```

## Requirements

The morningstar_data package is tested with

|             | Main version (latest)
|-------------|------------------------------|
| Python      | 3.8, 3.9, 3.10, 3.11         |
| Pandas      | 1.5                          |


## Using the API

This is an example of retrieving data for a saved investment list and data set from Morningstar Direct. See more usage examples in the Python package [documentation](https://docs-analyticslab.morningstar.com/latest/index.html) and tutorial notebooks in [Analytics Lab](https://analyticslab.morningstar.com/).

```
# Define investments by retrieving your saved lists
lists = md.direct.user_items.get_investment_lists()

| id                                   | name                                       |
|--------------------------------------|--------------------------------------------|
| 8CA07FB7-DFFE-4440-9ED7-6498CC074F11 | Morningstar Prospects                      |
| AE322592-5A3E-4B31-B889-16D8E76F48D3 | Sustainable Landscape U.S. Funds Q4 2021   |
| 83D337A2-1CF2-4E66-A94D-2B8EE554AC23 | Sustainable Landscape Global Funds Q4 2021 |
| ...                                  | ...                                        |

# Specify data points by using one of Morningstar's pre-saved data sets
morningstar_data_sets = md.direct.lookup.get_morningstar_data_sets()

| datasetId | name                                          |
|-----------|-----------------------------------------------|
| 0218-0020 | Snapshot                                      |
| 0218-0446 | Sustainability: ESG Risk (Company)            |
| 0218-0481 | Sustainability: Portfolio Sustainability Risk |
| ...       | ...                                           |


# Retrieve data by using the investment list and data set IDs from above
data = md.direct.get_investment_data(investments=lists["id"][0], data_points=morningstar_data_sets["datasetId"][0])

| Id            | Name                                    | Base Currency | ... |
|---------------|-----------------------------------------|---------------|-----|
| F00001AHPT;FO | Hartford Schroders Sustainable Cr Bd I  | US Dollar     | ... |
| F000014ZNT;FE | iShares ESG Aware Aggressive Allc ETF   | US Dollar     | ... |
| F00000WUF1;FE | iShares MSCI Global Sust Dev Goals ETF  | US Dollar     | ... |
| ...           | ...                                     | ...           | ... |

```

### Documentation

Documentation is hosted at https://docs-analyticslab.morningstar.com/latest/index.html

Find the version you are using with `md.__version__`

### Data Retrieval

The Morningstar Data Extension in [Analytics Lab](https://analyticslab.morningstar.com/) is the most convenient tool for locating data points and various saved objects to be used in morningstar_data function calls. You can browse data points, saved investment lists, search criteria, performance reports and more. Drag and drop the object you are interested in into a notebook and the corresponding Python code will be generated for you.

![direct extension](https://docs-analyticslab.morningstar.com/latest/_static/morningstar_direct_extension.png)


# Limits

## Overview of Limits


|Type of Limit| Restriction  |
|-------------|--------------|
|Limits | Morningstar Direct is exclusively licensed for individual usage. Users of Morningstar Direct are strictly prohibited from disclosing their login credentials, deploying instances of Morningstar Direct on a server, or utilizing, distributing, or redistributing data in a manner contradictory to their organization's agreement with Morningstar. Moreover, Morningstar Direct users are prohibited from employing information in any manner that would contravene the regulations and policies established by third-party providers.|
|Call Limits | When utilizing the morningstar_data Python package for data extraction, it's important to be aware of the limitations imposed on the number of requests you can make or the amount of data you can receive. These limitations are in place to ensure efficient usage of the resources and maintain the overall performance of the system.|
|Daily Limits | Limits are in place and can be reached when making requests or receiving data within a single day. These limits are determined either by the number of requests made or the quantity of data received. It is important to keep these limitations in mind while working with the data to ensure compliance and avoid any interruptions in your data processing tasks.|
|Content Limits |Content limits are governed by entitlements, which are determined by the specific product variant and add-ons purchased. These limits are put in place to regulate the amount of content accessible within the platform. It is important to be aware of these entitlements and ensure they align with your requirements and data processing tasks.|

## Detailed Limits

|Type of Limit| For this Item | Has this limitation|
|-------------|---------------|--------------------|
|Daily Limits | Number of Cells per Day | The count of data retrieved from the morningstar_data Python package per day cannot exceed 500,000 cells per day. This count of data is summed across all client applications connected to the same Morningstar Direct instance. In the event you reach your limit, please contact your Sales Representative or Customer Success Manager at Morningstar.|
|Daily Limits | Number Of investments in an Investment List | The size of an investment list in Morningstar Direct cannot exceed 30,000 investments in a single query.|
|Daily Limits | Number of data points returned per request |Data point limits are uniform across the type of data being retrieved. That is, the limits apply to time series data, static data, and so on, but are not aggregated across all applications. A custom data set in Morningstar Direct is limited to 1,000 data points.|
|Content/Entitlement Limits | Third-pary data usage|Additional morningstar_data Python package limitations may be imposed by the providers of the underlying data content. Consult with your Customer Success Manager or Sales Representative to know what third-party provider terms may apply to your use of this data.|


## Restricted Functions
As you refer to the morningstar_data Python package documentation, you may find some utility functions and additional data query functions that are not yet available for use. Such functions are in testing by internal teams at Morningstar, and they will be available to Morningstar Direct clients in the future.

# Usage
## Usage of Python package

A Python package refers to a specialized computer program that can be imported into a development environment to facilitate easier access to specific Morningstar data and the execution of pre-built functions. It consists of a toolkit comprising a predefined collection of functions that assist users in constructing something with ease and efficiency. The utilization of the morningstar_data Python package is subject to the governance of the Apache 2.0 license. An Authorized User is explicitly prohibited from engaging in activities such as translating, disassembling, or separating components of the Python package (e.g., accessing or acquiring Product code in any manner). The sole means of granting Authorized Users permission to employ and manipulate the Python package is by referencing or providing a separate entitlement to do so. However, this permission must not override any other limitations outlined in the Click License about the utilization or distribution of the Product.

## Extraction of Data using the Python package

Since the functions (i.e., tools) within the morningstar_data package enable users to extract Morningstar data in various ways, it is imperative to ensure that users extract the data within the constraints specified for them and by the distribution licenses held by Morningstar with their respective firms.

## Sharing of Authentication Token

We authenticate a user's access to the morningstar_data package using an authentication token, which remains valid for 24 hours and can solely be obtained from Analytics Lab. Access to Analytics Lab requires possession of a Direct License. Users are strictly prohibited from sharing their authentication tokens with other individuals, as the usage of the product is tethered to the terms and agreements associated with license of Morningstar Direct.

# Terms & Conditions
The utilization of the morningstar_data Python package entails accessing certain data from Morningstar Direct. Your access and utilization of Morningstar Direct, including its morningstar_data Python package and associated data, are governed by the terms and conditions set forth in your organization’s agreement with Morningstar. Morningstar Direct is an Asset and Wealth management platform that is lawfully licensed for individual use, subject to a login session requirement. A login session is designed to control entitlements and regulate reasonable use for a singular user. To align with the workflow demands of a single user, the morningstar_data Python package imposes restrictions to safeguard the overall platform’s capacity to support the usage levels of all individual Morningstar Direct users accessing data via APIs. The document attached below provides a succinct overview of these various restrictions and elucidates the user experience when encountering them. The specific numerical values for each restriction described herein are not binding and do not create any legal obligations on the part of Morningstar. These restrictions are subject to modification at our sole discretion, without prior notice. It is your sole responsibility to furnish all necessary support pertaining to any applications developed utilizing the morningstar_data Python package. Kindly take note that if you have intentions to resell or distribute any applications or data developed using the morningstar_data Python package to third parties, it is imperative to engage in a distribution license agreement with us. Please contact your Customer Success Manager or Sales Representative at Morningstar for further information.
