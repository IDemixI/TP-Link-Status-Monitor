#!/usr/local/bin/python

import os
import base64
import getpass
import re
import csv
import lxml

from sys import argv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

# Page links for each section that data is scraped from

#Main Page (Status)
routerURL = "http://192.168.1.1/"

#DHCP Client List
routerDHCPList = "#__dhcpClient.htm"

#Bandwidth Stats Page
routerBandStat = "#__stat.htm"


makeCSV = False

# Main Menu
      
def print_menu():
    print "\n"
    print 20 * "-" , " Network Statistics " , 20 * "-"
    print "1. Router Status"
    print "2. Connected Devices"
    print "3. Bandwidth Monitor"
    print "4. Settings"
    print "5. Exit"
    print 60 * "-"
    print "\n"
  
loop = True      
  
while loop:
    print_menu()
    choice = raw_input("Enter your choice [1-5]: ")
     
    if choice == '1':     
        print "\nGetting Router Status..."
        loop = False
    elif choice == '2':
        print "\nRetrieving Device List..."
        routerURL = routerURL + routerDHCPList
        loop = False		
    elif choice == '3':
        print "\nStarting Bandwidth Monitor..."
        routerURL = routerURL + routerBandStat
        loop = False
    elif choice == '4':
        print "\nLoading Settings Menu..."
        makeCSV = True
        loop = False
    elif choice == '5':
        print "\nExiting Program..."
        loop = False
        exit(0)
    else:
        # Any integer inputs other than values 1-5 we print an error message
        raw_input("Invalid option selected. Enter any key to try again..")


# Enable proxy if any command line arguments are given
if len(argv) > 1 and argv[1] == "ollie":
    print "Setting proxy & Cookie..."
    authKey = "Basic YWRtaW46ZmlnaHRpbmc="
    service_args = ['--proxy=127.0.0.1:8080', '--proxy-type=socks5']
    browser = webdriver.PhantomJS(service_args=service_args)
elif len(argv) > 1 and argv[1] == "debug":
    authKey = "Basic YWRtaW46ZmlnaHRpbmc="
    print ("\nDebug Mode...\n")
    print ("Your Auth Key is: " + authKey + "\n")
    browser = webdriver.PhantomJS()	
else:
    passwd = getpass.getpass("Enter Router Password: ")

    cookieIn = b"admin:" + passwd
    cookieOut = base64.b64encode(cookieIn.encode("utf8","ignore"))

    authKey = "Basic " + cookieOut

    print ("Your Auth Key is: " + authKey + "\n")
    browser = webdriver.PhantomJS()

browser.add_cookie({'name': 'Authorization', 'value': authKey, 'domain': '192.168.1.1', 'path': '/'})

browser.get(routerURL)

browser.implicitly_wait(5)

timeout_seconds = 10

try:
    element_present = EC.presence_of_element_located((By.ID, 'updateBtn'))
    WebDriverWait(browser, timeout_seconds).until(element_present)
except TimeoutException:
    print "Page load timed out, exiting"
    exit(1)

soup = BeautifulSoup(browser.page_source, "lxml")
browser.close()
browser.quit()


data = []

header = soup.find('table', {'class': 'XL bdr tc'})
table = soup.find('table', {'id': 'hostTbl'})


table_header = header.find('tr')
table_body = table.find('tbody')

header = []

i = 0

for tag in table_header.find_all(re.compile("^t")):
    if i == 0:
	    header.append(tag.text.ljust(3)[:3])
    elif i == 4:
        header.append(tag.text.ljust(15)[:15])
    else:
	    header.append(tag.text.ljust(25)[:25])
    i += 1

print "\n"

data.append(header) 

rows = table_body.find_all("tr")

for row in rows:
    cols = row.find_all("td")
    cols = [ele.text.strip().ljust(25)[:25] for ele in cols]
    data.append([ele for ele in cols if ele]) # Get rid of empty values
	
	
datao = [str(a) for a in data]
print("\n" . join(datao))

if makeCSV == True:
    with open("Clients.csv", "wb") as f:
        writer = csv.writer(f)
        writer.writerows(data)

exit(0)

