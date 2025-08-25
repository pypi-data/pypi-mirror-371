# GENERAL INDEX PYTHON SDK #

This document describes the General Index Python SDK which allows permissioned users to access GX data within
their python scripts.

Note that the SDK does not cover everything from API documentation but rather commonly used features.

The scope of the SDK:

- **GX API** - retrieves data directly from GX API endpoints
- **Datalake Handler** - downloading / uploading / reading files from the data lake

## How to install and set the package:

### Install

```text
pip3 install generalindex=={$VERSION}
```

As the library is available from pip, it can be installed as a specific version within a Python Task from within
requirements.txt just by adding:

```text
generalindex=={$VERSION}
```

The package relies on the other libraries so, in the project, the user must install this library in the requirements.txt
file.

### Environment Variables

The package uses information from the environment variables. 
If running the script locally, users must set them in the project.

Mandatory environment variables to set:
- Credentials used to generate the token so that each request is authenticated:

         - LOGIN → login received from GX
         - PASSWORD → password to log in.
          or:
         - NG_API_AUTHTOKEN → api-token received from GX 

Optional environment variables to set:
- NG_API_ENDPOINT → the URL to the GX platform API (by default, the url is set to https://api.g-x.co)

This allows to pass the authentication process and directs users' requests to the GX environment API.
--- -
# GX API

The retrieved data can be:

- streamed directly to memory as a BytesIO object, both in CSV and JSON format,
- saved as a file locally with the provided path and name, both in CSV and JSON format.

## Index endpoint

### How to read data from index endpoint?

It is possible to use the SDK to directly query the GX API endpoints for data, using the index symbol keys (code,
period, periodType, timeRef),
the datalake group it is stored on and additional params.

The retrieved data can be:

- streamed directly to memory as a BytesIO object, both in CSV and JSON format,
- saved as a file locally with the provided path and name, both in CSV and JSON format.

Extra settings are as well available to query data:
- code: Symbol code (default '*' )
-  period: Symbol period (default '*' ).
-  period_type: Symbol periodType (default '*' )
-  time_ref: Symbol timeRef (default '*' )
-  group: Name of the group (default Prod_Indexes)
-  module: Name of the IndexModule. Can't use with 'code','period','periodType' and 'timeRef' parameter
- start_from: Start date (default beginning of the day) Accepted values (where * is a number):
  - today
  - *d - specific amount of days
  - *m - specific amount of months
  - *y - specific amount of years
  - all- no specified starting point
  - {x}v- only x last values for each index
  - ISO date ex. 2022-11-21T00:00:00 
- to: End date (default end of the day) Accepted values (where * is a number):
  - today
  - *d - specific amount of days
  - *m - specific amount of months
  - *y - specific amount of years
  - ISO date ex. 2022-11-21T00:00:00
- delta: Delta will filter timeseries by insertion date instead of the actual timestamp of data (default false)
- metadata: to either return it in the response or not (default false) Accepted values: true, false, only
- metadata_fields: Filter by metadata field e.g. {"metadata.tradinghub":"NWE"} 
- order: Order of results by date (default desc)
- timezone: Timezone as string used for the timestamps in the Date column. Format: Continent/City, for example Europe/London (default UTC)
- fields: Filter by value field e.g. {"FactsheetVersion":"1"}
- headers: Additional headers, which will be sent with request for symbols e.g. {"Example-Header":"Example_header_value"}

The following code shows an example of how to query the index:

 ```python
import pandas as pd

import generalindex as gx

# Instantiate GxApi 
api = gx.GxApi()

# retrieve all available data for specified code
# and save as query.csv in test/
api.index(code=['GX0000001'], start_from='all', headers={"Example-Header":"Example_header_value"})\
    .file(file_name='test/query.csv', output_type='csv')

# The retrieved data can be read as a pandas dataframe
df = pd.read_csv("test/query.csv")

# retrieve all available data for specified code
# and stream to memory as BytesIO object
data = api.index(code=['GX0000001'], start_from='all' , headers={"Example-Header":"Example_header_value"})\
    .csv()

# read as pandas dataframe
df = pd.read_csv(data)
```
### How to read data from Index in JSON format?

To retrieve data in JSON format use json() method as follows. This

 ```python
import generalindex as gx

# Instantiate GxApi 
api = gx.GxApi()


# retrieve all available data for code
# and stream to memory as BytesIO object
json_data = api.index(code=["GX0000001"],start_from='all').json()

# retrieve all available data from group according to code
# and save as result.txt in test/
api.index(code=['GX0000001'], start_from='all', group='MyGroup')\
    .file(file_name='test/result.txt', output_type='json')
```

### How to read data from Index for specific dates?

To retrieve the data within specific time frame, user can specify the from and to params.

There are multiple options how the from and to params may look like (where * is a number): 
- from:
  - today
  - *d - specific amount of days
  - *m - specific amount of months
  - *y - specific amount of years
  - all- no specified starting point
  - {x}v- only x last values for each index
  - ISO date ex. 2022-11-21T00:00:00 
  - date ex. 2022-11-21

- to: 
  - today
  - *d - specific amount of days
  - *m - specific amount of months
  - *y - specific amount of years
  - ISO date ex. 2022-11-21T00:00:00
  - date ex. 2022-11-21


If date and time is specified then data will be retrieved exactly for the specified time frame.

Note that ISO format must be followed: YYYY-MM-DD**T**HH:mm:ss. Pay attention to the "T" letter between date and time.

 ```python
import generalindex as gx

# Instantiate GxApi 
api = gx.GxApi()

# retrieve data between from and to
# data will be retrieved between 2021-01-04 00:00:00 and 2021-02-05 23:59:59
# saved as a csv file named test.csv
api.index(code=["GX0000001"],
          group='My Group',
          start_from='2021-01-04',
          to='2021-02-05'
          ).file(file_name='test/test.csv')

# retrieve data for specific time frame
# from 2021-01-04 12:30:00
# to 2021-02-05 09:15:00
api.index(code=["GX0000001"],
          group='My Group',
          start_from='2021-01-04T12:30:00',
          to='2021-02-05T09:15:00'
          ).file(file_name='test/test.csv')

# retrieve data for general time frame
# from previous 12 months
# to now
api.index(code=["GX0000001"],
          group='My Group',
          start_from='12m'
          ).file(file_name='test/test.csv')

# retrieve data
# from first existing
# to 2021-02-05T09:15:00 
api.index(code=["GX0000001"],
          group='My Group',
          start_from='all',
          to='2021-02-05T09:15:00'
          ).file(file_name='test/test.csv')

# retrieve data for only last 2 values
api.index(code=["GX0000001"],
          group='My Group',
          start_from='2v'
          ).file(file_name='test/test.csv')
```

### How to download data with the different Time Zone?

The timestamps in the queried time series are set by default to UTC.
It is described in the Date column header between brackets (for example *Date(UTC)*)

To modify the timezone in the retrieved dataset, the timezone can be passed as a follow parameter.
Timezones are specified as per the [IANA Time Zone database ](https://data.iana.org/time-zones/tzdb-2023d/zone.tab)

```python
import generalindex as gx
import pandas as pd

# Instantiate GxApi 
api = gx.GxApi()

# retrieve all data from group available from 2 days with Data in selected timezone
# and stream to memory as BytesIO object
data = api.index(group='My Group', start_from='2d',
                 timezone='Europe/London').csv()

# read as pandas dataframe
df = pd.read_csv(data)
```

### How to get the metadata along with the data ?

It is possible to get extra columns in the retrieved data, along with the keys & column values, containing the metadata
of the symbols.
It is done by setting the argument *metadata='true'* in the retrieval function.

By default, no metadata is included in the queried data.

It is possible to get only columns containing the metadata of the symbols.
It is done by setting the argument *metadata='only'* in the retrieval function.

```python
import generalindex as gx

# Instantiate GxApi 
api = gx.GxApi()

# retrieve all data from group available from 2 days with metadata
# and stream to memory as BytesIO object
data = api.index(group='My Group', start_from='2d',
                 metadata='true').csv()

# retrieve only metadata from group available from 2 days 
# and stream to memory as BytesIO object
metadata = api.index(group='My Group', start_from='2d',
                     metadata='only').csv()

```
### How to get index codes belonging to specified module ?

The gx index codes are organized into modules.
Those can be queried using module param.

Note that  module parameter can't be used with 'code','period','periodType' and 'timeRef' parameters

```python
import generalindex as gx

# Instantiate GxApi 
api = gx.GxApi()

# retrieve all available data for 2 months and from module 'GlobalOilSelect'
#  get as json and stream to memory as BytesIO object
data = api.index(start_from="1m", module=['GlobalOilSelect']).json()
```

### How to filter the data by selected column ?

The gx index data can be queried using multiple params also by values in the columns:

By providing the dictionary of column name and column values or metadata column and value we can filter out 
data that is not needed.

```python
import generalindex as gx

# Instantiate GxApi 
api = gx.GxApi()

# retrieve all available data from group according to 2 codes and 2 months
# get only those having FactsheetVersion equals to '1'
#  get as json and stream to memory as BytesIO object
filter_fields = {"FactsheetVersion": "1"}
data = api.index(code=["GX000001", "GX000002"], start_from="2m", fields=filter_fields).json()

# retrieve all available data from group according to 2 codes and 2 months
# get only those having metadata field Currency(MD-S) equals to 'USD'
#  get as json and stream to memory as BytesIO object
metadata_fields = {"metadata.Currency": "USD"}
data = api.index(code=["GX000001", "GX000002"], start_from="2m", metadata='true', metadata_fields=metadata_fields).json()
```
----
## Catalogue endpoint
It allows to get list of all available GX Indexes organized in modules.

Extra settings available to query data:
- code: Symbol code (default '*' )
- no_module: Include indexes without index module set (default false).
- :param module: Filter by provided IndexModule name.
- fields: Filter by catalogue field e.g. {"field.status":"Live"}
- limit_fields: Limit request to specified fields e.x. 'Code,Title'

The following code shows an example of how to query the catalogue:
### How to get the list of existing gx indexes?
```python
import generalindex as gx

# Instantiate GxApi 
gx_api = gx.GxApi()

# Get all GX indexes assigned to AsiaLPG module and save as a csv file
gx_api.catalogue(module='AsiaLPG').file("indexes.csv")

# Get all GX indexes including not assigned to modules and save as a csv file
gx_api.catalogue(no_module=True).file("indexes.csv")

# Get only Code and Currency columns for all GX indexes assigned to modules
# and stream to memory as csv BytesIO object
limit_fields = ['Code', 'Currency']
gx_api.catalogue(limit_fields=limit_fields).csv()

# Get all GX indexes assigned to modules with Currency equals 'USD' 
# and stream to memory as json BytesIO object
filter_fields = {'field.Currency': 'USD'}
gx_api.catalogue(fields=filter_fields).json()
```
--- -

## Symbols endpoint

### How to get the list of existing symbols for a given group ?

Data saved in the time series database is structured by group, keys and timestamp.
Each set of keys has unique dates entries in the database, with corresponding columns values.

To explore what are the available symbols for a given group, the following method can be used:

```python
import generalindex as gx

# Instantiate GxApi 
gx_api = gx.GxApi()

# Get the list of symbols for default Prod_Indexes group
group_symbols = gx_api.get_symbols()

# Get the list of symbols for specified group
group = 'Other_Group'
group_symbols = gx_api.get_symbols(group)
```

The default size of the returned list is 1 000 items. Maximum size for this method is 10 000 symbols. If more symbols are expected please use stream

Note that the return object from the get_symbols() method is a JSON (python dict) where the keys and columns are
accessible in the *items* key of the JSON.

Streaming symbols
```python
import generalindex as gx

# Instantiate GxApi 
gx_api = gx.GxApi()

# Get the list of symbols for default Prod_Indexes group
group_symbols = gx_api.stream_symbols()

# Get the list of symbols for specified group
group = 'Other_Group'
group_symbols = gx_api.stream_symbols(group)
```

### How to query by metadata or descriptions?

In order to find the symbols querying by the metadata, column or symbol names, search parameter may be used.
It will look for passed string in the whole time series database and return the JSON with keys and columns where
searched string appears.

Note that search param is case-sensitive !

```python
import generalindex as gx

# Instantiate GxApi 
gx_api = gx.GxApi()

# Get the list of symbols for given group
search = 'symbols.Code=GX0000001'
searched_symbols = gx_api.get_symbols(search=search)
```

Passing both group_name and search_for parameters of the get_symbols() method allows to narrow down the results from
selected group.

If trying to get the list of symbols from a group that contains more than 1 000 items, the results will be paginated (by
default into chunks of 1 000 items).
To navigate in the large results the *get_symbols()* method takes as extra arguments the size of the returned list and
the from page:

```python
import generalindex as gx

# Instantiate GxApi 
gx_api = gx.GxApi()

# Get the results into chunks of 200 items for page 5
# meaning the results from the 1000th till the 1200th 
group_symbols = gx_api.get_symbols(size=200, start_from=5)
```

By default, these parameters are _size=1000 (the maximum limit for the items lengths) and _from=0.

--- - 
# Datalake Handler

### How to download or read a file from data lake by its ID ?

In the case that the file ID is known, it can be directly downloaded/read as follows:

```python
import generalindex as gx
import pandas as pd

# Instantiate the Datalake Handler
dh = gx.DatalakeHandler()

# download file from data lake by its ID
# it will be saved locally with name local_name.csv
dh.download_by_id(file_id='XXXX-XXXX',
                  dest_file_name='folder/local_name.csv',
                  save=True,
                  unzip=False)

# read file from data lake by its ID
# it returns a BytesIO object
fileIO = dh.download_by_id(file_id='XXXX-XXXX',
                           dest_file_name=None,
                           save=False,
                           unzip=False)

# read the object as pandas DataFrame
df = pd.read_csv(fileIO)

```

The download methods allows to either:

- download and save locally the wanted file, if *save=True*
- read the file directly from the datalake and get a BytesIO object (kept in memory only, that can for example be read
  by pandas as a dataframe directly)

Note that by default:

- the file is NOT saved locally, but returned as a BytesIO object (streamed from the datalake).
- the argument *dest_file_name=None*, which will save the downloaded file to the root folder with its original name.


### How to upload a file to the data lake?

The uploading method will upload to the given group the file at the specified path, and returns its ID on the lake.

Group name will be provided by GX Support:
```python
import generalindex as gx

# Instantiate the Datalake Handler
dh = gx.DatalakeHandler()

# upload file to data lake

file_id = dh.upload_file(file='path/local_name.csv', group_name='Provided_Name', file_upload_name='name_in_the_datalake.csv',
                         file_type='SOURCE', partial_update=False,
                         avoid_duplicates=False)
```
It is possible as well to stream a python object's content directly to the datalake from memory, without having to save
the file on the disk.

The prerequisite is to pass to the uploading method a BytesIO object as file parameter (not other objects such as pandas
Dataframe).

```python
import generalindex as gx
import io

# Instantiate the Datalake Handler
dh = gx.DatalakeHandler()

# Turn the pandas DataFrame (df) to BytesIO for streaming
fileIO = io.BytesIO(df.to_csv().encode())

# upload file to data lake
file_id = dh.upload_file(file=fileIO, group_name='My Group', file_upload_name='name_in_the_datalake.csv',
                         file_type='SOURCE', partial_update=False,
                         avoid_duplicates=False)
```
--- -

### Who do I talk to? ###

* General Index Support: info@general-index.com