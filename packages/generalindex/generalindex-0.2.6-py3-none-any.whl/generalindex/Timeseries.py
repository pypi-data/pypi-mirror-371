import csv
import json
import os, io
import urllib
from datetime import datetime
from io import StringIO


import pytz
from deprecated import deprecated
from pytz import UnknownTimeZoneError
from urllib import parse

from .DatalakeHandler import DatalakeHandler
from .HTTPCaller import HTTPCaller
from .utils import log


@deprecated(version='0.1.20', reason="You should use GxApi instead")
class Timeseries:
    def __init__(self):
        self.caller = HTTPCaller()
        self.uploader = DatalakeHandler()

    def get_symbols(self, search_for: str = None, group_name: str = None, _size=1000, _from=0):
        '''
        Returns a list of the symbols available on a given group or symbols within search
        '''
        formatted_search = None
        formatted_group = None

        assert (group_name not in ["", None]) or (search_for not in ["", None]), \
            'Please specify either group_name or search_for parameter of get_symbols() method'

        # format group name and search for url - changes spaces to %20 etc.
        if group_name not in ["", None]:
            formatted_group = urllib.parse.quote(group_name)
        if search_for not in ["", None]:
            formatted_search = urllib.parse.quote(search_for)

        if formatted_search is not None and formatted_group is not None:
            # both search and group passed
            query_url = '/ts/symbol/search?size={}&from={}&query={}*%26groupName.keyword%3D{}'.format(_size, _from,
                                                                                                      formatted_search,
                                                                                                      formatted_group)
        elif formatted_search is not None and formatted_group is None:
            # search passed
            query_url = '/ts/symbol/search?size={}&from={}&query={}'.format(_size, _from, formatted_search)
        else:
            # group passed
            query_url = '/ts/symbol/search?size={}&from={}&query=groupName.keyword%3D{}'.format(_size, _from,
                                                                                                formatted_group)

        # GET Request
        r = self.caller.get(path=query_url)

        return json.load(io.BytesIO(r.content))

    def retrieve_data_as_csv(self, symbols: dict, columns, group_name: str,
                             file_name: str = None, start_date: str = None, end_date: str = None,
                             timezone: str = None,
                             metadata: bool = False, allow_wildcard: bool = False, NCSV: bool = True,
                             corrections: str = 'false', delta: bool = False):

        '''
        The method retrieves the data from NG Timeseries based on symbols and columns.
        Optionally start and end dates can be specified. If no dates specified, all the available data are taken.

        :param symbols: symbols to identify data in Timeseries. Must dictionary {"symbolName": "symbolValue", ...}
        :param columns: name of column or list of columns to retrieve
        :param group_name: name of the group
        :param file_name: the name of file locally to save data to, with the proper extension passed (for example data.csv)
        :param start_date: start date of data in the format YYYY-MM-DD. If time is included, it must follow ISO format:
        YYYY-MM-DDTHH:mm:ss (note the 'T' letter separating the date and time part)
        :param end_date: end date of the data in the format YYYY-MM-DD. If time is included, it must follow ISO format:
        YYYY-MM-DDTHH:mm:ss (note the 'T' letter separating the date and time part)
        :param: timezone: timezone as string used for the timestamps in the Date column. Continent/City, for example Europe/London if None, it returns the date with the default timezone of the user, set in the application
        :param: metadata: boolean to return or not the metadata in the file, default as False
        :param: allow_wildcard: boolean to allow or not the use of wildcards '*' in the keys or columns
        :param: NCSV: boolean to specify format of response (NCSV = true ; PANDAS= false)
        :param: corrections: How to handle corrections in time series. Must be either "true", "false", "history" or "only"
        :param: delta: delta will filter timeseries by insertion date instead of the actual timestamp of data

        :return: saves file with data
        '''

        # start_date is optional: if not provided, the data are taken from the very beginning
        if start_date is not None:
            # date only
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                start_date = start_date + "T00:00:00"
            except:
                # if cannot parse to date only, it may contain time
                try:
                    datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")
                except:
                    raise Exception(f'Wrong format of date is passed for start date.'
                                    f'The accepted datetime formats are: YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss. '
                                    f'E.g., 2021-02-05 or 2021-02-05T12:30:00')

        # start_date is optional: if not provided, the data are taken from the very beginning
        if end_date is not None:
            # date only
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
                # till the end of day
                end_date = end_date + "T23:59:59"
            except:
                # if cannot parse to date only, it may contain time
                try:
                    datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S")
                except:
                    raise Exception(f'Wrong format of date is passed for end date.'
                                    f'The accepted datetime formats are: YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss.'
                                    f'E.g., 2021-02-05 or 2021-02-05T12:30:00'
                                    )

        # Cast columns argument as list
        if not isinstance(columns, list):
            columns = [columns]

        # Payload Body of the REQUEST
        body = {"startDate": start_date,
                "endDate": end_date,
                "keys": [
                    {"symbols": symbols,
                     "groupName": group_name,
                     "columns": columns,
                     "pattern": allow_wildcard
                     }
                ],
                "corrections": corrections,
                "delta": delta,
                "formatType": "NCSV" if NCSV else 'PANDAS'
                }

        # add extra fields in the payload if needed
        if timezone is not None:
            self.verify_timezone(timezone)

            body["timeZone"] = timezone
        # return metadata
        body['metadata'] = metadata

        # Check that if a wild_card was passed, the patter was set to True
        if ('*' in body['keys'][0]['symbols'].values()) and (allow_wildcard is False):
            raise ValueError('If passing a wildcard in the symbols, allow_wildcard must be True')

        # Summary
        log.debug(f'Retrieving data for symbols: {symbols} '
                  f'\nand columns: {columns}'
                  f'\nfrom date: {start_date}'
                  f'\nto date: {end_date}')

        # Request
        r = self.caller.post(path='/ts', payload=body)
        log.debug(f'Response: {r.text}')

        try:

            # Get file as NCSV API format
            if NCSV:
                # return raw bytes directly
                fileIO = io.BytesIO(r.content)

                if file_name is None:
                    # return the raw Bytes (streamed)
                    return fileIO

                else:
                    # Check that the extension is in the file, else add it as csv by default
                    file_name = file_name if '.' in file_name else file_name + '.csv'

                    # Save the downloaded data on the disk
                    with open(file_name, "w") as text_file:
                        text_file.write(r.text)

            # Get file as PANDAS API format
            else:
                # return the JSON for the Horizontal format
                file_json = json.load(io.BytesIO(r.content))['data']

                if file_name is None:
                    # return raw JSON format of the data
                    return file_json

                else:
                    # Check that the extension is in the file, else add it as csv by default
                    file_name = file_name if '.' in file_name else file_name + '.csv'

                    # Save the downloaded data on the disk
                    with open(file_name, "w") as file_to_write:
                        json.dump(file_json, file_to_write)

        except:
            # Get unique list of symbols
            raw_list = self.get_symbols(group_name)['items']
            symb_list = set([item for sublist in [list(d['symbols'].keys()) for d in raw_list] for item in sublist])

            # Raise error with symbols list
            raise ValueError(
                'Wrong Symbols or Columns passed to the query . It should match the data structure on the group: {}'.format(
                    symb_list))

        log.debug('Data are saved to file: {}'.format(file_name))

        return

    @staticmethod
    def verify_timezone(timezone):
        try:
            pytz.timezone(timezone)
            return True
        except UnknownTimeZoneError:
            raise ValueError('Wrongly formatted timezone argument. Must be for example Europe/London')

    def retrieve_data_as_csv_streaming(self, symbols: dict, columns, group_name: str,
                                       file_name: str = None, start_date: str = None, end_date: str = None,
                                       timezone: str = None,
                                       metadata: bool = False, allow_wildcard: bool = False,
                                       output_format: str = 'NCSV',
                                       corrections: str = 'false', delta: bool = False):

        '''
        The method retrieves the data from NG Timeseries based on symbols and columns with streaming function.
        Optionally start and end dates can be specified. If no dates specified, all the available data are taken.
        * IMPORTANT! Currently in streaming mode NCSV output is available.

        :param symbols: symbols to identify data in Timeseries. Must dictionary {"symbolName": "symbolValue", ...}
        :param columns: name of column or list of columns to retrieve
        :param group_name: name of the group
        :param file_name: the name of file locally to save data to, with the proper extension passed (for example data.csv)
        :param start_date: start date of data in the format YYYY-MM-DD. If time is included, it must follow ISO format:
        YYYY-MM-DDTHH:mm:ss (note the 'T' letter separating the date and time part)
        :param end_date: end date of the data in the format YYYY-MM-DD. If time is included, it must follow ISO format:
        YYYY-MM-DDTHH:mm:ss (note the 'T' letter separating the date and time part)
        :param: timezone: timezone as string used for the timestamps in the Date column. Continent/City, for example Europe/London
                        if None, it returns the date with the default timezone of the user, set in the application
        :param: metadata: boolean to return or not the metadata in the file, default as False
        :param: allow_wildcard: boolean to allow or not the use of wildcards '*' in the keys or columns
        :param; output_format: The method from which "view" the data should be retrieved. Default "NCSV".
        :param: corrections: How to handle corrections in time series. Must be either "true", "false", "history" or "only"
        :param: delta: delta will filter timeseries by insertion date instead of the actual timestamp of data

        :return: saves file with data
        '''

        # start_date is optional: if not provided, the data are taken from the very beginning
        if start_date is not None:
            # date only
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                start_date = start_date + "T00:00:00"
            except:
                # if cannot parse to date only, it may contain time
                try:
                    datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")
                except:
                    raise Exception(f'Wrong format of date is passed for start date.'
                                    f'The accepted datetime formats are: YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss. '
                                    f'E.g., 2021-02-05 or 2021-02-05T12:30:00')

        # start_date is optional: if not provided, the data are taken from the very beginning
        if end_date is not None:
            # date only
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
                # till the end of day
                end_date = end_date + "T23:59:59"
            except:
                # if cannot parse to date only, it may contain time
                try:
                    datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S")
                except:
                    raise Exception(f'Wrong format of date is passed for end date.'
                                    f'The accepted datetime formats are: YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss.'
                                    f'E.g., 2021-02-05 or 2021-02-05T12:30:00'
                                    )

        # Cast columns argument as list
        if not isinstance(columns, list):
            columns = [columns]

        # Payload Body of the REQUEST
        body = {"startDate": start_date,
                "endDate": end_date,
                "keys": [
                    {"symbols": symbols,
                     "groupName": group_name,
                     "columns": columns,
                     "pattern": allow_wildcard
                     }
                ],
                "corrections": corrections,
                "delta": delta,
                "formatType": output_format
                }

        # add extra fields in the payload if needed
        if timezone is not None:
            self.verify_timezone(timezone)

            # return dates in wanted timezone
            body["timeZone"] = timezone

        # return metadata
        body['metadata'] = metadata

        # Check that if a wild_card was passed, the patter was set to True
        if ('*' in body['keys'][0]['symbols'].values()) and (allow_wildcard is False):
            raise ValueError('If passing a wildcard in the symbols, allow_wildcard must be True')

        # Summary
        log.debug(f'Retrieving data for symbols: {symbols} '
                  f'\nand columns: {columns}'
                  f'\nfrom date: {start_date}'
                  f'\nto date: {end_date}')

        # Request
        r = self.caller.post(path='/ts/stream', payload=body)

        log.debug(f'Response: {r.text}')

        try:

            # Get file as NCSV API format
            if output_format == 'NCSV':
                # return raw bytes directly
                fileIO = StringIO(str(r.content, encoding='utf-8'))

                if file_name is None:
                    # return the raw Bytes (streamed)
                    return fileIO

                else:
                    # Check that the extension is in the file, else add it as csv by default
                    file_name = file_name if '.' in file_name else file_name + '.csv'

                    # Save the downloaded data on the disk
                    with open(file_name, "w") as text_file:
                        text_file.write(r.text)

            else:
                raise ValueError(
                    '{} format of the timeseries output is not supported. Please use NCSV, PANDAS or STANDARD'.format(
                        output_format))

        except:
            # Get unique list of symbols
            raw_list = self.get_symbols(group_name)['items']
            symb_list = set([item for sublist in [list(d['symbols'].keys()) for d in raw_list] for item in sublist])

            # Raise error with symbols list
            raise ValueError(
                'Wrong Symbols or Columns passed to the query . It should match the data structure on the group: {}'.format(
                    symb_list))

        log.debug('Data are saved to file: {}'.format(file_name))

        return

    def retrieve_data_as_json(self, symbols: dict, columns, group_name: str,
                              file_name: str = None, start_date: str = None, end_date: str = None,
                              timezone: str = None,
                              metadata: bool = False, allow_wildcard: bool = False, output_format: str = 'NCSV',
                              corrections: str = 'false', delta: bool = False):

        '''
        The method retrieves the data from NG Timeseries based on symbols and columns with streaming function.
        Optionally start and end dates can be specified. If no dates specified, all the available data are taken.
        * IMPORTANT! Currently NCSV output_format returns the same as for streaming functions. STANDARD, PANDAS, UI return json.

        :param file_name: the name of file locally to save data to, with the proper extension passed (for example data.csv)
        :param symbols: symbols to identify data in Timeseries. Must dictionary {"symbolName": "symbolValue", ...}
        :param columns: name of column or list of columns to retrieve
        :param group_name: name of the group
        :param start_date: start date of data in the format YYYY-MM-DD. If time is included, it must follow ISO format:
        YYYY-MM-DDTHH:mm:ss (note the 'T' letter separating the date and time part)
        :param end_date: end date of the data in the format YYYY-MM-DD. If time is included, it must follow ISO format:
        YYYY-MM-DDTHH:mm:ss (note the 'T' letter separating the date and time part)

        :param: timezone: timezone as string used for the timestamps in the Date column. Continent/City, for example Europe/London
                        if None, it returns the date with the default timezone of the user, set in the application
        :param: corrections: How to handle corrections in time series. Must be either "true", "false" or "only"
        :param: delta: delta will filter timeseries by insertion date instead of the actual timestamp of data
        :param: metadata: boolean to return or not the metadata in the file, default as False
        :param: allow_wildcard: boolean to allow or not the use of wildcards '*' in the keys or columns
        :param: corrections: How to handle corrections in time series. Must be either "true", "false", "history" or "only"
        :param: delta: delta will filter timeseries by insertion date instead of the actual timestamp of data
        :param; output_format: The method from which "view" the data should be retrieved. Default "NCSV".

        :return: saves file with data
        '''

        # start_date is optional: if not provided, the data are taken from the very beginning
        if start_date is not None:
            # date only
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                start_date = start_date + "T00:00:00"
            except:
                # if cannot parse to date only, it may contain time
                try:
                    datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")
                except:
                    raise Exception(f'Wrong format of date is passed for start date.'
                                    f'The accepted datetime formats are: YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss. '
                                    f'E.g., 2021-02-05 or 2021-02-05T12:30:00')

        # start_date is optional: if not provided, the data are taken from the very beginning
        if end_date is not None:
            # date only
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
                # till the end of day
                end_date = end_date + "T23:59:59"
            except:
                # if cannot parse to date only, it may contain time
                try:
                    datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S")
                except:
                    raise Exception(f'Wrong format of date is passed for end date.'
                                    f'The accepted datetime formats are: YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss.'
                                    f'E.g., 2021-02-05 or 2021-02-05T12:30:00'
                                    )

        # Cast columns argument as list
        if not isinstance(columns, list):
            columns = [columns]

        # Payload Body of the REQUEST
        body = {"startDate": start_date,
                "endDate": end_date,
                "keys": [
                    {"symbols": symbols,
                     "groupName": group_name,
                     "columns": columns,
                     "pattern": allow_wildcard
                     }
                ],
                "corrections": corrections,
                "delta": delta,
                "formatType": output_format
                }

        # add extra fields in the payload if needed
        if timezone is not None:
            # Check the format for the timezone
            self.verify_timezone(timezone)

            # return dates in wanted timezone
            body["timeZone"] = timezone

        # return metadata
        body['metadata'] = metadata

        # Check that if a wild_card was passed, the patter was set to True
        if ('*' in body['keys'][0]['symbols'].values()) and (allow_wildcard is False):
            raise ValueError('If passing a wildcard in the symbols, allow_wildcard must be True')

        # Summary
        log.debug(f'Retrieving data for symbols: {symbols} '
                  f'\nand columns: {columns}'
                  f'\nfrom date: {start_date}'
                  f'\nto date: {end_date}')

        # Request
        r = self.caller.post(path='/ts', payload=body)

        log.debug(f'Response: {r.text}')

        try:

            # Get file as NCSV API format
            if output_format == 'NCSV':
                # return raw bytes directly
                fileIO = StringIO(str(r.content, encoding='utf-8'))

                if file_name is None:
                    # return the raw Bytes (streamed)
                    return fileIO

                else:
                    # Check that the extension is in the file, else add it as csv by default
                    file_name = file_name if '.' in file_name else file_name + '.csv'

                    # Save the downloaded data on the disk
                    with open(file_name, "w") as text_file:
                        text_file.write(r.text)

            # Get file as STANDARD API format
            elif output_format == 'STANDARD':
                # return the JSON for the Horizontal format
                file = json.load(io.BytesIO(r.content))['values']

                if file_name is None:
                    # return raw JSON format of the data
                    return file

                else:
                    # Check that the extension is in the file, else add it as csv by default
                    file_name = file_name if '.' in file_name else file_name + '.csv'

                    # Save the downloaded data on the disk
                    with open(file_name, "w") as file_to_write:
                        json.dump(file, file_to_write)

            # Get file as PANDAS API format
            elif output_format == 'PANDAS':
                # return the JSON for the Horizontal format
                file = json.load(io.BytesIO(r.content))['data']

                if file_name is None:
                    # return raw JSON format of the data
                    return file

                else:
                    # Check that the extension is in the file, else add it as csv by default
                    file_name = file_name if '.' in file_name else file_name + '.csv'

                    # Save the downloaded data on the disk
                    with open(file_name, "w") as file_to_write:
                        json.dump(file, file_to_write)

            # Get file as UI API format
            elif output_format == 'UI':
                # return the JSON for the Horizontal format
                file = json.load(io.BytesIO(r.content))['values']

                if file_name is None:
                    # return raw JSON format of the data
                    return file

                else:
                    # Check that the extension is in the file, else add it as csv by default
                    file_name = file_name if '.' in file_name else file_name + '.csv'

                    # Save the downloaded data on the disk
                    with open(file_name, "w") as file_to_write:
                        json.dump(file, file_to_write)

            else:
                raise ValueError(
                    '{} format of the timeseries output is not supported. Please use NCSV, PANDAS or STANDARD'.format(
                        output_format))

        except:
            # Get unique list of symbols
            raw_list = self.get_symbols(group_name)['items']
            symb_list = set([item for sublist in [list(d['symbols'].keys()) for d in raw_list] for item in sublist])

            # Raise error with symbols list
            raise ValueError(
                'Wrong Symbols or Columns passed to the query . It should match the data structure on the group: {}'.format(
                    symb_list))

        log.debug('Data are saved to file: {}'.format(file_name))

        return

    def upload_data(self, file_name, symbols_columns, date_column, group_name):
        '''
        The methods uploads data to Timeseries by re-arranging the columns order and uploading the new file as NCSV.
        :param file_name: csv file to be upload to Timeseries
        :param symbols_columns: columns to be used as symbols
        :param date_column: date column in the file; is renamed to DateTime as expected by NCSV
        :param group_name: group name for the NCSV file to upload
        :return: id of the NCSV file uploaded
        '''

        # get all column names form csv file
        with open(file_name) as csv_file:
            csv_reader = csv.DictReader(csv_file)
            dict_from_csv = dict(list(csv_reader)[0])
            all_cols = list(dict_from_csv.keys())

        log.debug(f'Original file {file_name} contains columns: {all_cols}')

        assert len(all_cols) != 0, "No columns in csv"
        assert all([x in all_cols for x in symbols_columns]), f"Symbols are not in columns list {symbols_columns}"
        assert date_column in all_cols, f"No column {date_column} in the list"

        # create new order of columns => symbols, date column, value columns
        key = symbols_columns + ['DateTime']
        value_columns = [x for x in all_cols if x not in key and x != date_column]
        final_cols = key + value_columns

        log.debug(f'Columns will be re-ordered to NCSV format: {final_cols}')

        # to keep file in the same place where the original file is
        parent_folder = os.path.dirname(file_name)
        temp_file = os.path.join(parent_folder, 'temp.csv')

        # write reordered csv to the temporary file
        with open(file_name, 'r') as infile, open(temp_file, 'a') as outfile:
            reader = csv.DictReader(infile)
            writer = csv.writer(outfile)

            # write header
            writer.writerow(final_cols)
            for row in reader:
                # change date_column to DateTime
                row['DateTime'] = row.pop(date_column)

                # prepare new line as per new columns order
                line = [row[x] for x in final_cols]
                writer.writerow(line)
        log.debug(f'File with re-ordered column is saved as {temp_file}')

        # upload file as NCSV to the specified group
        fid = self.uploader.upload_file(file=temp_file, group_name=group_name, file_type='NCSV')
        log.debug(f'File is uploaded as NCSV: {fid}')

        os.remove(temp_file)
        log.debug(f'Temporary file {temp_file} is removed.')
        return fid
