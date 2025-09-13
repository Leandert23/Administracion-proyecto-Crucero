import sqlite3
from pprint import pprint

DB_PATH = 'db.sqlite3'
TABLES = [
    'restaurant_ingredientes',
    'restaurant_menu_dia_1',
    'restaurant_menu_dia_2',
    'restaurant_menu_dia_3',
    'restaurant_menu_dia_4',
    'restaurant_menu_dia_5',
    'restaurant_menu_dia_6',
    'restaurant_menu_dia_7',
    'restaurant_italiano',
    'restaurant_arabe',
    'restaurant_vinos',
    'restaurant_carta_especial',
    'restaurant_menu_fijo',
    'restaurant_buffet',
    'restaurant_platillos_ingredientes',
    'restaurant_products',
]

def table_info(cur, table):
    cur.execute(f"PRAGMA table_info('{table}')")
    cols = cur.fetchall()
    cur.execute(f"PRAGMA foreign_key_list('{table}')")
    fks = cur.fetchall()
    return cols, fks

if __name__ == '__main__':
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    for t in TABLES:
        print('='*80)
        print('TABLE:', t)
        try:
            cols, fks = table_info(cur, t)
            if not cols:
                print('No columns (table missing or empty pragma).')
            else:
                print('Columns:')
                for cid, name, ctype, notnull, dflt, pk in cols:
                    print(f" - {name} :: {ctype} NOTNULL={notnull} PK={pk} DEFAULT={dflt}")
                if fks:
                    print('Foreign Keys:')
                    for row in fks:
                        print(' ', row)
        except sqlite3.OperationalError as e:
            print('Error:', e)
    con.close()
