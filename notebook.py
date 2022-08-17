#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os 
import hashlib

import time

import requests
import yaml


# In[ ]:


AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
MAILCHIMP_TOKEN = os.getenv('MAILCHIMP_TOKEN')

CONFIG_FILE = os.getenv('CONFIG_FILE', 'config.yaml')


# In[ ]:


with open(CONFIG_FILE) as f_in:
    config = yaml.load(f_in, Loader=yaml.BaseLoader)


# In[ ]:


def md5(email):
    email = email.strip().lower()
    result = hashlib.md5(email.encode('utf-8')).hexdigest()
    return result


# In[ ]:


AIRTABLE_URL_TEMPLATE = "https://api.airtable.com/v0/{database_name}/{table_name}"

def mark_records_processed(database, table, batch):
    url = AIRTABLE_URL_TEMPLATE.format(
        database_name=database,
        table_name=table,
    )
    
    patch_records = []
    
    for record in batch:
        patch_records.append({
            "id": record["id"],
            "fields": {"processed": True}
        })
    
    data = {
        "records": patch_records
    }

    headers = {
        'Authorization': f'Bearer {AIRTABLE_TOKEN}'
    }
    
    response = requests.patch(url, json=data, headers=headers)
    print(f'{url} {response.status_code}')
    print(f'maked {len(batch)} as processed')
    return response


def get_records_batched(database, table, view, page_size=100, include_sleep=True):
    url = AIRTABLE_URL_TEMPLATE.format(
        database_name=database,
        table_name=table,
    )

    params = {
        'view': view,
        'pageSize': page_size,
    }

    headers = {
        'Authorization': f'Bearer {AIRTABLE_TOKEN}'
    }
    
    response = requests.get(url, params=params, headers=headers)
    print(f'{url} {response.status_code}')
    result = response.json()
    records = result['records']
    
    yield records
    
    while 'offset' in result:
        if include_sleep:
            time.sleep(0.2)

        offset = result['offset']

        params = {
            'view': view,
            'pageSize': page_size,
            'offset': offset
        }

        response = requests.get(url, params=params, headers=headers)
        print(f'{url} {response.status_code}')
        result = response.json()
        records = result['records']

        yield records    


# In[ ]:


def add_update_contact(list_id, email):
    data = {
        "email_address": email,
        "status_if_new": "subscribed", 
    }

    mc_url_template = 'https://us19.api.mailchimp.com/3.0/lists/{list_id}/members/{subscriber}'
    
    subscriber = md5(email)
    mc_url = mc_url_template.format(list_id=list_id, subscriber=subscriber)
    
    mc_auth = ('anystring', MAILCHIMP_TOKEN)
    mc_headers = {'Content-Type': 'application/json'}
    
    response = requests.put(mc_url, auth=mc_auth, headers=mc_headers, json=data)
    print(f'{mc_url} {response.status_code}')
    print(f'add_update_contact({list_id}, {subscriber})')
    return response


# In[ ]:


def add_tag(list_id, email, tag):
    mc_tag_url_template = 'https://us19.api.mailchimp.com/3.0/lists/{list_id}/members/{subscriber}/tags'

    subscriber = md5(email)
    mc_tag_url = mc_tag_url_template.format(list_id=list_id, subscriber=subscriber)
    
    tags_data = {
        "tags": [{"name": tag, "status": "active"}],
        "is_syncing": False
    }
    
    mc_auth = ('anystring', MAILCHIMP_TOKEN)
    mc_headers = {'Content-Type': 'application/json'}

    response = requests.post(mc_tag_url, auth=mc_auth, headers=mc_headers, json=tags_data)
    print(f'{mc_tag_url} {response.status_code}')
    print(f'add_tag({list_id}, {subscriber}, {tag})')
    return response


# In[ ]:


list_id = config['list_id']
page_size = config['page_size']


# In[ ]:


tables = config['tables']

for table in tables:
    print(f'processing {table}...')
    
    tag = table['tag']
    
    batch_iterator = get_records_batched(
        database=table['database'],
        table=table['table'],
        view=table['view'],
        page_size=page_size
    )

    for batch in batch_iterator:
        for record in batch:
            fields = record['fields']
            email = fields['email']
            add_update_contact(list_id, email)
            add_tag(list_id, email, tag)

        mark_records_processed(
            database=table['database'],
            table=table['table'],
            batch=batch
        )

        print(f'processed {len(batch)} records')


# In[ ]:





# In[ ]:




