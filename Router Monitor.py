#!/usr/local/bin/python

import os
import base64
import getpass
import re
import csv
import lxml
import json

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

#Blank URL for parsing
routerURLx = ""

makeCSV = False
makeHTML = False

# Set a global variable for retries - try and load page 2/3 times before quitting out and resetting count


def main():

    mainMenu()





# Main Menu
      
def print_menu():
    print "\n"
    print 20 * "-" , " Network Statistics " , 20 * "-"
    print "1. Router Status"
    print "2. Connected Devices"
    print "3. Bandwidth Monitor"
    print "4. Settings"
    print "5. Exit"
    print 62 * "-"
    print "\n"

	
	
def mainMenu():	

    global routerURL
    global routerDHCPList
    global routerBandStat
    global routerURLx
    
    loop = True      

    while loop:
        print_menu()
        choice = raw_input("Enter your choice [1-5]: ")
     
        if choice == '1':     
            print "\nGetting Router Status..."
            loop = False
        elif choice == '2':
            routerURLx = routerURL + routerDHCPList
            loop = False
            connectSite(choice)
        elif choice == '3':
            print "\nStarting Bandwidth Monitor..."
            routerURLx = routerURL + routerBandStat
            loop = False
        elif choice == '4':
            print "\nLoading Settings Menu..."
            loop = False
        elif choice == '5':
            print "\nExiting Program..."
            loop = False
            exit(0)
        else:
            # Any integer inputs other than values 1-5 we print an error message
            raw_input("Invalid option selected. Enter any option to try again..")


def connectSite(choice):

    global makeCSV
    global makeHTML
		
    if choice == '1':
	    findEl = 'Dunno yet'
    elif choice == '2':
        findEl = 'hostTbl'
        print "\nRetrieving Device List..."
    else:
        findEl = 'Dunno yet'
		

    # Enable proxy if any command line arguments are given
    if len(argv) > 1 and argv[1] == "ollie":
        print "Setting proxy & Cookie..."
        authKey = "Basic YWRtaW46ZmlnaHRpbmc="
        service_args = ['--proxy=127.0.0.1:8080', '--proxy-type=socks5']
        browser = webdriver.PhantomJS(service_args=service_args)
    elif len(argv) > 1 and argv[1] == "debug":
        authKey = "Basic YWRtaW46ZmlnaHRpbmc="
        print ("\nDebug Mode...\n")
        makeCSV = True
        makeHTML = True
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

    browser.get(routerURLx)

    browser.implicitly_wait(5)

    timeout_seconds = 6

    try:
        element_present = EC.presence_of_element_located((By.ID, findEl))
        WebDriverWait(browser, timeout_seconds).until(element_present)
    except TimeoutException:
        print "Page load timed out, going to menu.."
        mainMenu()

    soup = BeautifulSoup(browser.page_source, "lxml")
    
    browser.quit()
    parsePage(choice, soup)



def parsePage(menuChoice, soupData):

    data = []

    thead = soupData.find('table', {'class': 'XL bdr tc'})
    table = soupData.find('table', {'id': 'hostTbl'})


    table_header = thead.find('tr')
    table_body = table.find('tbody')

    header = []

    i = 0

    for tag in table_header.find_all(re.compile("^t")):
        if i == 0:
	        header.append(str(tag.text).ljust(3)[:3])
        elif i == 1:
	        header.append(str(tag.text).ljust(30)[:30])
        elif i == 2:
            header.append(str(tag.text).ljust(18)[:18])
        elif i == 3:
            header.append(str(tag.text).ljust(15)[:15])
        elif i == 4:
            header.append(str(tag.text).ljust(12)[:12])
        else:
            print("No element found. Error detected.\n")
        i += 1

    data.append(header) 


    #print('-' * 80)
    #test = str(header).strip('[]').translate(None, "',")
    #print(test)
    #print('-' * 80 + '\n')

    try:
        rows = table_body.find_all("tr")
    except AttributeError:
        print "Table not found. Reloading page..."
        connectSite(menuChoice)

    for row in rows:
        cols = row.find_all("td")

        x = 0
        body = []

        for ele in cols:
            if x == 0:
                body.append(str(ele.text.strip()).ljust(3)[:3])
            elif x == 1:
                body.append(str(ele.text.strip()).ljust(30)[:30])
            elif x == 2:
                body.append(str(ele.text.strip()).ljust(18)[:18])
            elif x == 3:
                body.append(str(ele.text.strip()).ljust(15)[:15])
            elif x == 4:
                body.append(str(ele.text.strip()).ljust(12)[:12])
            else:
                print("No element found. Error detected.\n")
            x += 1
        
        data.append(body)
	
    dataF = [str(a).strip('[]') for a in data]
    print("\n" . join(dataF).translate(None, "',") + "\n")

    callOutput(thead, table, data)
    mainMenu()
	
	
def callOutput(head, table, csvOutput):
	
    dir_path = os.path.dirname(os.path.realpath(__file__))

    f = open(dir_path + '\Output\devices.html','wb')

    htmlO = """<html>
    <head><style>td { text-align: center; } table { border: thin solid black; } </style></head>
    <body><br>"""

    htmlC = """</body>
    </html>"""

    f.write(htmlO + "\n")

    f.write(str(head).replace('<br/>', '').replace('628px', '800px') + "\n")
    f.write(str(table).replace('<br/>', '').replace('628px;', '800px; border-top: 0;').replace('<tr>', '\n<tr>') + "\n")
    f.write (htmlC)	

    f.close()

    print('Created: ' + dir_path + '\Output\devices.html')


    if makeCSV == True:
        with open(dir_path + '\Output\devices.csv', 'wb') as f:
            writer = csv.writer(f)
            writer.writerows(csvOutput)
            print('Created: ' + dir_path + '\Output\devices.csv')
        f.close()

main()
exit(0)
