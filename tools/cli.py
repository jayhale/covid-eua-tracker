from datetime import datetime
from urllib.parse import urljoin

import bs4 as bs
import click
from dateparser.search import search_dates
import requests
from yaml import dump

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper


@click.group()
@click.option('--output', type=click.File('w+'), default='euas.yaml')
@click.pass_context
def cli(ctx, output):
    ctx.obj = {'output': output}


@cli.group()
def scrape():
    """Scrape a data source"""
    pass


def get_approval_date(text):
    return min([d[1] for d in search_dates(text, languages=['en'])]).date()


def get_links_and_amendments(base_url, elements):
    """Get link data from a set of BS elements (columns in a row)"""

    link_data = []
    amend_data = []

    for e in elements:
        links = e.find_all('a')

        for link in links:
            data = {
                'title': link.get('title'),
                'href': urljoin(base_url, link.get('href')),
            }

            if 'Letter' in data['title']:
                data['type'] = 'letter of authorization'
            elif 'Providers' in data['title']:
                data['type'] = 'fact sheet for healthcare providers'
            elif 'Patients' in data['title']:
                data['type'] = 'fact sheet for patients'
            elif 'Summary' in data['title']:
                data['type'] = 'eua summary'
            elif 'Instructions' in data['title']:
                data['type'] = 'instructions for use'
            elif 'Amendment' in data['title']:
                data['type'] = 'amendment'
                amend_date = search_dates(data['title'])
                if amend_date:
                    amend_data.append(amend_date[0][1].date())

            link_data.append(data)

    return link_data, amend_data


@scrape.command()
@click.option('--ivd-ag-table-index', default=2)
@click.option('--ivd-lab-table-index', default=1)
@click.option('--ivd-mgt-table-index', default=4)
@click.option('--ivd-mol-table-index', default=0)
@click.option('--ivd-ser-table-index', default=3)
@click.option(
    '--ivd-url',
    default='https://www.fda.gov/medical-devices/coronavirus-disease-2019-covid-19-emergency-use-authorizations-medical-devices/vitro-diagnostics-euas',
)
@click.pass_context
def ivd(
    ctx,
    ivd_ag_table_index,
    ivd_lab_table_index,
    ivd_mgt_table_index,
    ivd_mol_table_index,
    ivd_ser_table_index,
    ivd_url,
):
    """Scrape in-virto diagnostic data"""

    output = ctx.obj['output']

    click.echo('Gathering in-vitro diagnostic data')
    ivd_data = []

    # Fetch the IVD HTML data
    r = requests.get(ivd_url)
    ivd_soup = bs.BeautifulSoup(r.text, 'html.parser')
    click.echo(' - Fetched html')

    tables = ivd_soup.find_all('table')
    ivd_mol_table = tables[ivd_mol_table_index]
    ivd_lab_table = tables[ivd_lab_table_index]
    ivd_ag_table = tables[ivd_ag_table_index]
    ivd_ser_table = tables[ivd_ser_table_index]
    ivd_mgt_table = tables[ivd_mgt_table_index]

    # Locate the molecular diagnostics table
    ivd_mol_rows = ivd_mol_table.find_all('tr')
    click.echo(f' - Found {len(ivd_mol_rows)-1} molecular diagnostic records')

    # Process the molecular diagnostics
    iterrows = iter(ivd_mol_rows)
    next(iterrows)

    for row in iterrows:
        cols = row.find_all('td')

        # Easy fields
        d = {
            'method': 'molecular',
            'last_update': datetime.strptime(cols[0].text.strip(), '%m/%d/%Y').date(),
            'entity': cols[1].text.strip(),
            'technology': cols[3].text.strip(),
            'settings': cols[4].text.strip().split(', '),
        }

        # Complex fields
        d['diagnostic'] = cols[2].find('a').text.strip()
        d['approval_date'] = get_approval_date(cols[2].text.strip())

        link_data, amend_data = get_links_and_amendments(ivd_url, cols)
        if link_data:
            d['links'] = link_data
        if amend_data:
            d['amendments'] = amend_data

        # Append the entry to the master list
        ivd_data.append(d)

    # Locate the lab diagnostics table
    ivd_lab_rows = ivd_lab_table.find_all('tr')
    click.echo(f' - Found {len(ivd_lab_rows)-1} lab molecular diagnostic records')

    # Process the lab diagnostics
    iterrows = iter(ivd_lab_rows)
    next(iterrows)

    for row in iterrows:
        cols = row.find_all('td')

        # Easy fields
        d = {
            'method': 'molecular',
            'last_update': datetime.strptime(cols[0].text.strip(), '%m/%d/%Y').date(),
            'entity': cols[1].text.strip(),
            'settings': ['H'],
        }

        # Complex fields
        d['diagnostic'] = cols[2].find('a').text.strip()
        d['approval_date'] = get_approval_date(cols[2].text.strip())

        link_data, amend_data = get_links_and_amendments(ivd_url, cols)
        if link_data:
            d['links'] = link_data
        if amend_data:
            d['amendments'] = amend_data

        # Append the entry to the master list
        ivd_data.append(d)

    # Locate the antigen diagnostics table
    ivd_ag_rows = ivd_ag_table.find_all('tr')
    click.echo(f' - Found {len(ivd_ag_rows)-1} antigen diagnostic records')

    # Process the antigen diagnostics
    iterrows = iter(ivd_ag_rows)
    next(iterrows)

    for row in iterrows:
        cols = row.find_all('td')

        # Easy fields
        d = {
            'method': 'antigen',
            'last_update': datetime.strptime(cols[0].text.strip(), '%m/%d/%Y').date(),
            'entity': cols[1].text.strip(),
            'technology': cols[3].text.strip(),
            'settings': cols[4].text.strip().split(', '),
        }

        # Complex fields
        d['diagnostic'] = cols[2].find('a').text.strip()
        d['approval_date'] = get_approval_date(cols[2].text.strip())

        link_data, amend_data = get_links_and_amendments(ivd_url, cols)
        if link_data:
            d['links'] = link_data
        if amend_data:
            d['amendments'] = amend_data

        # Append the entry to the master list
        ivd_data.append(d)

    # Locate the serological dianostics table
    ivd_ser_rows = ivd_ser_table.find_all('tr')
    click.echo(f' - Found {len(ivd_ser_rows)-1} serological diagnostic records')

    # Process the serological diagnostics
    iterrows = iter(ivd_ser_rows)
    next(iterrows)

    for row in iterrows:
        cols = row.find_all('td')

        # Easy fields
        d = {
            'method': 'serological',
            'last_update': datetime.strptime(cols[0].text.strip(), '%m/%d/%Y').date(),
            'entity': cols[1].text.strip(),
            'technology': cols[3].text.strip(),
            'settings': cols[4].text.strip().split(', '),
        }

        # Complex fields
        d['diagnostic'] = cols[2].find('a').text.strip()
        d['approval_date'] = get_approval_date(cols[2].text.strip())

        link_data, amend_data = get_links_and_amendments(ivd_url, cols)
        if link_data:
            d['links'] = link_data
        if amend_data:
            d['amendments'] = amend_data

        # Append the entry to the master list
        ivd_data.append(d)

    # Locate the management diagnostics table
    ivd_mgt_rows = ivd_mgt_table.find_all('tr')
    click.echo(f' - Found {len(ivd_mgt_rows)-1} management diagnostic records')

    # Process the management diagnostics
    iterrows = iter(ivd_mgt_rows)
    next(iterrows)

    for row in iterrows:
        cols = row.find_all('td')

        # Easy fields
        d = {
            'method': 'management',
            'last_update': datetime.strptime(cols[0].text.strip(), '%m/%d/%Y').date(),
            'entity': cols[1].text.strip(),
            'technology': cols[3].text.strip(),
            'settings': cols[4].text.strip().split(', '),
        }

        # Complex fields
        d['diagnostic'] = cols[2].find('a').text.strip()
        d['approval_date'] = get_approval_date(cols[2].text.strip())

        link_data, amend_data = get_links_and_amendments(ivd_url, cols)
        if link_data:
            d['links'] = link_data
        if amend_data:
            d['amendments'] = amend_data

        # Append the entry to the master list
        ivd_data.append(d)

    # Save the results to disk
    data = dump(ivd_data, Dumper=Dumper)
    output.write(data)
