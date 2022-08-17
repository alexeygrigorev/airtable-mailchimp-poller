import os
import requests


AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')


GET_RECORDS_URL_TEMPLATE = "https://api.airtable.com/v0/" + \
    "{database_name}/{table_name}?maxRecords={max_records}&view={view_name}"
PATCH_RECORDS_URL_TEMPLATE = "https://api.airtable.com/v0/" + \
    "{database_name}/{table_name}"


HEADERS = {
    'Authorization': f'Bearer {AIRTABLE_TOKEN}'
}


def get_records(database, table, view, max_records=10):
    url = GET_RECORDS_URL_TEMPLATE.format(
        database_name=database,
        table_name=table,
        view_name=view,
        max_records=max_records
    )

    result = requests.get(url, headers=HEADERS).json()
    return result