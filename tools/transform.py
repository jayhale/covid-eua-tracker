import csv

import click
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


@click.command()
@click.option('--csv-output', type=click.File('w+'), default='euas.csv')
@click.option('--csv/--no-csv', 'csv_flag', default=True)
@click.pass_context
def transform(ctx, csv_flag, csv_output):
    """Transform data formats"""

    # Load the master data file
    yaml_output = ctx.obj['yaml_output']
    yaml_output.seek(0)
    yaml_data = load(yaml_output.read(), Loader=Loader)

    # Build the CSV output
    if csv_flag:
        headers = [
            'type',
            'entity',
            'device',
            'approval_date',
            'last_update',
            'diagnostic_method',
            'diagnostic_technology',
            'diagnostic_setting_H',
            'diagnostic_setting_M',
            'diagnostic_setting_W',
        ]

        rows = [headers]

        for item in yaml_data:
            row = [
                item['type'],
                item['entity'],
                item['device'],
                item['approval_date'],
                item['last_update'],
            ]

            if item['type'] == 'diagnostic':
                row.extend(
                    [
                        item['method'],
                        item['technology'] if 'technology' in item else None,
                        True if 'H' in item['settings'] else False,
                        True if 'M' in item['settings'] else False,
                        True if 'W' in item['settings'] else False,
                    ]
                )
            else:
                row.extend(
                    [
                        None,
                        None,
                        None,
                        None,
                        None,
                    ]
                )

            rows.append(row)

        writer = csv.writer(csv_output)
        writer.writerows(rows)

        click.echo(f'Wrote {len(rows)} to {csv_output}')
