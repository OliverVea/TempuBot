from defs import dir_path

def get_row(number, name, name_color, parse, parse_color, rank, dps):
    row = ""
    with open(dir_path + '/html_templates/row_template.html', 'r') as file:
        for line in file:
            row += line

    row = row.replace('$INSERT_NUMBER', number)
    row = row.replace('$INSERT_NAME_COLOR', name_color)
    row = row.replace('$INSERT_NAME', name)
    row = row.replace('$INSERT_PARSE_COLOR', parse_color)
    row = row.replace('$INSERT_PARSE', parse)
    row = row.replace('$INSERT_RANK', rank)
    row = row.replace('$INSERT_DPS', dps)

    if (int(number) % 2 == 1): row = row.replace('bgc-evenrow', 'bgc-oddrow')

    return row

def get_table(group_name : str, metric : str, rows : str, avg_parse : str, avg_parse_color : str, avg_rank : str, avg_dps : str):
    table = ""
    with open(dir_path + '/html_templates/table_template.html', 'r') as file:
        for line in file:
            table += line

    table = table.replace('$INSERT_GROUP', group_name)
    table = table.replace('$INSERT_METRIC', metric)
    table = table.replace('$INSERT_ROWS', rows)
    table = table.replace('$INSERT_AVG_PARSE_VALUE', avg_parse)
    table = table.replace('$INSERT_AVG_PARSE_COLOR', avg_parse_color)
    table = table.replace('$INSERT_AVG_RANK', avg_rank)
    table = table.replace('$INSERT_AVG_DPS', avg_dps)
    
    return table

def get_html(boss_name, table):
    html = ""
    with open(dir_path + '/html_templates/rankings_template.html', 'r') as file:
        for line in file:
            html += line

    html = html.replace('$INSERT_BOSS_NAME', boss_name)
    html = html.replace('$INSERT_TABLE', table)

    return html