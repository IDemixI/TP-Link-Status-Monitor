#!/usr/local/bin/python

try:
    import readline
except ImportError:
    import pyreadline as readline

import os
import base64
import getpass
import re
import csv
import lxml
import SendKeys
import Tkinter

from sys import argv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

# Page links for each section that data is scraped from

#Main Page (Status)
routerURL = "http://192.168.1.1/" # - Sky Hub
# routerURL = "http://192.168.0.1/" - TP-Link Router

#DHCP Client List
routerDHCPList = "#__dhcpClient.htm" # - TP-Link Router

#Bandwidth Statistic Page
routerBandStat = "#__stat.htm" # - TP-Link Router

#Blank URL for parsing
routerURLx = ""

# Set a global variable for retries - increment count until it reaches limit
pageRetry = 0

#Set a global variable for maximum retries
pageRetryMax = 3

# Global Authentication Key for cookie generation on multiple retries
authKey = ""

# Settings boolean for CSV and HTML creation 
makeCSV = False
makeHTML = False

# Store the temporary CSV / HTML files
tmpCSV = ''
tmpHTML = ''



def main():

    mainMenu()


# Main Menu
      
def printMenu():
    print "\n"
    print 20 * "-" , " Network Statistics " , 20 * "-"
    print "1. Router Status"
    print "2. Connected Devices"
    print "3. Bandwidth Monitor"
    print "4. Settings"
    print "5. Exit"
    print "6. Dev stuff"
    print 62 * "-"
    print "\n"

	
def mainMenu():	

    global routerURL
    global routerDHCPList
    global routerBandStat
    global routerURLx
    
    loop = True      

    while loop:
        printMenu()
        choice = raw_input("Enter your choice [1-6]: ")
     
        if choice == '1':     
            print "\nGetting Router Status..."
            loop = False
        elif choice == '2':
            routerURLx = routerURL + routerDHCPList
            loop = False
            connectSite(choice, False) # As opened via menu - devList = False
        elif choice == '3':
            print "\nStarting Bandwidth Monitor..."
            routerURLx = routerURL + routerBandStat
            loop = False
            connectSite(choice, False) # As opened via menu - devList = False
        elif choice == '4':
            print "\nLoading Settings Menu..."
            settingsMenu()
            loop = False
        elif choice == '5':
            print "\nExiting Program..."
            loop = False
            exit(0)
        elif choice == '6':
            top = Tkinter.Tk()

            # changing the title of our master widget      
            top.title("GUI")
        
            # Code to add widgets will go here...
            top.mainloop()

        else:
            # Any integer inputs other than values 1-6 we print an error message
            print("\nInvalid option selected. Enter any option to try again..")


def printSettings():
    global makeCSV
    global makeHTML
    global tmpCSV
    global tmpHTML

    if makeCSV == True and tmpCSV == '':
        tmpCSV = 'Yes'
    elif tmpCSV == False and tmpCSV == '':
        tmpCSV = 'No'
    elif tmpCSV == 'Yes':
        tmpCSV = 'Yes'
    else:
        tmpCSV = 'No'

    if makeHTML == True and tmpHTML == '':
        tmpHTML = 'Yes'
    elif tmpHTML == False and tmpHTML == '':
        tmpHTML = 'No'
    elif tmpHTML == 'Yes':
        tmpHTML = 'Yes'
    else:
        tmpHTML = 'No'
	
    print "\n"
    print 25 * "-" , " Settings " , 25 * "-"
    print "1. Generate CSV File - [" + tmpCSV + "]"
    print "2. Generate HTML File - [" + tmpHTML + "]"
    print "3. Change Device Names for Output"
    print "4. Save and Exit"
    print "5. Exit without saving"
    print 62 * "-"
    print "\n"


def settingsMenu():	

    global makeCSV
    global makeHTML
    global tmpCSV
    global tmpHTML
    global routerURLx
	
    loop = True
    tmpCSV = ''
    tmpHTML = ''
	
    while loop:
        printSettings()
        choice = raw_input("Enter your choice [1-5]: ")
     
        if choice == '1':
		
            while choice == '1':
                print("\n")
                tmpCSV = raw_input("Generate CSV File (Y/N): ")

                if tmpCSV == 'Y' or tmpCSV == 'y':
                    tmpCSV = 'Yes'
                    choice = ''
                elif tmpCSV == 'N' or tmpCSV == 'n':
                    tmpCSV = 'No'
                    choice = ''
                else:
                    print("\nInvalid input.\n")

        elif choice == '2':
		
            while choice == '2':
                print("\n")
                tmpHTML = raw_input("Generate HTML File (Y/N): ")

                if tmpHTML == 'Y' or tmpHTML == 'y':
                    tmpHTML = 'Yes'
                    choice = ''
                elif tmpHTML == 'N' or tmpHTML == 'n':
                    tmpHTML = 'No'
                    choice = ''
                else:
                    print("\nInvalid input.\n")

        elif choice == '3':
		
            routerURLx = routerURL + routerDHCPList
            choicex = '2'
            devList = True
            connectSite(choicex, devList) # Really could just use 2 and True as the parameters...
			
        elif choice == '4':

            if tmpCSV == 'Yes':
                makeCSV = True
            elif tmpCSV == 'No':
                makeCSV = False

            if tmpHTML == 'Yes':
                makeHTML = True
            elif tmpHTML == 'No':
                makeHTML = False
				
            tmpCSV = ''
            tmpHTML = ''
            print "\nSettings Saved..."
            loop = False
            mainMenu()

        elif choice == '5':
		
            print "\nReturning to main menu..."
            loop = False
            mainMenu()
			
        else:
            # Any integer inputs other than values 1-5 we print an error message
            print("\nInvalid option selected. Enter any option to try again..")


def connectSite(choice, devList):

    global makeCSV
    global makeHTML
    global authKey
	
    if choice == '1':
	    findEl = 'Dunno yet'
    elif choice == '2':
        findEl = 'hostTbl'
        print "\nRetrieving Device List..."
    elif choice == '3':
        findEl = 'stat_table'
		
		

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
        print ("Your Authentication Key is: " + authKey + "\n")
        browser = webdriver.PhantomJS()	
    else:
        if authKey == "":
            passwd = getpass.getpass("Enter Router Password: ")
            cookieIn = b"admin:" + passwd
            cookieOut = base64.b64encode(cookieIn.encode("utf8","ignore"))
            authKey = "Basic " + cookieOut
            print ("Your Authentication Key is: '" + authKey + "'\n")

        browser = webdriver.PhantomJS()

    browser.add_cookie({'name': 'Authorisation', 'value': authKey, 'domain': '192.168.1.1', 'path': '/'})

    browser.get(routerURLx)

    timeout_seconds = 6

    try:
        element_present = EC.presence_of_element_located((By.ID, findEl))
        WebDriverWait(browser, timeout_seconds).until(element_present)
    except TimeoutException:
        print "Page load timed out, going to menu.."
        mainMenu()

    soup = BeautifulSoup(browser.page_source, "lxml")
    
    browser.quit()
    #print(soup)
    parsePage(choice, soup, devList)



def parsePage(menuChoice, soupData, devList):

    data = []

    if menuChoice == '2':
        thead = soupData.find('table', {'class': 'XL bdr tc'})
        table = soupData.find('table', {'id': 'hostTbl'})
        table_header = thead.find('tr')
    elif menuChoice == '3':
        thead = soupData.find('table', {'class': 'XXL bdr tc'})
        table = soupData.find('table', {'id': 'stat_table'})
        table_header = thead.find_all('tr')
        table_header = str(table_header).strip('[]').decode('unicode_escape').encode('ascii','ignore')
        table_header = BeautifulSoup(table_header, "lxml")

    table_body = table.find('tbody')
	
    header = []

    i = 0

    if menuChoice == '2':
	
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
            #print(str(tag) + str(i))
            i += 1

        data.append(header) 

    if menuChoice == '3':
	
        for tag in table_header.find_all(re.compile("^th")):
            #if i == 0 or i == 6 or i == 8:
            if i == 6 or i == 8:
	            header.append(str(tag.text).ljust(20)[:20])
            elif i == 1:
	            header.append(str(tag.text).ljust(31)[:31])
            elif i == 2:
                header.append(str(tag.text).ljust(60)[:60])
            elif i == 3:
                header.append(str(tag.text).ljust(30)[:30])
            elif i == 4:
                header.insert(0,(str(tag.text[:10]).ljust(20)[:20]))
                data.append(header)
                header = []
                header.append(str(tag.text[10:]).ljust(20)[:20])
            elif i == 5 or i == 7 or i >= 9:
	            header.append(str(tag.text).ljust(10)[:10])
            else:
                print("No element found. Error detected.\n")
            i += 1

        data.append(header)

    if devList == False:
        print('-' * 80)
        dataF = [str(a).strip('[]') for a in data]
        print("\n" . join(dataF).translate(None, "',"))
        print('-' * 80)

    #test = str(header).strip('[]').translate(None, "',")
    #print(test)
    #print('-' * 80 + '\n')

    try:
        rows = table_body.find_all("tr")
    except AttributeError:
        print "Table not found. Reloading page..."
        connectSite(menuChoice, devList)

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
            #print(str(ele.text.strip())) # code 0-7 for Bandwidth Monitor!
            x += 1
        
        data.append(body)
	
    dataF = [str(a).strip('[]') for a in data[1:]]

    if devList == False:
        print("\n" . join(dataF).translate(None, "',") + "\n")
        callOutput(thead, table, data)
        mainMenu()
    else:
        loadDeviceList(data)
        
	
def loadDeviceList(data):

    i = 0

    print("\n" + "-" * 10 + " List of Devices " + "-" * 10 + "\n")

    for x in data:
        if i > 0:
            print ("[" + str(i) + "] - " + data[i][1])
        i += 1

    print("\n[" + str(i) + "] - Return to Settings\n")

    opt = raw_input("Select an item to change the name of: ")

    list_id = [ seq[0].strip() for seq in data[1:] ]
	
    if opt in list_id:
        data[int(opt)][1] =  raw_input("Enter a new device name for " + data[int(opt)][1].strip() + ": ")
        loadDeviceList(data)
    elif str(opt) == str(i):
        print('Going back to settings menu')
        #SendKeys.SendKeys(default_value, 0)
        settingsMenu()
    else:
        print("\n" + opt + " not found. Select from device list.")
        loadDeviceList(data)


def callOutput(head, table, csvOutput):

    if makeHTML == True:

        dir_path = os.path.dirname(os.path.realpath(__file__))
        f = open(dir_path + '\Output\devices.html','wb')

        htmlO = """<html>
        <head><style>td { text-align: center; } table { border: thin solid black; } </style></head>
        <body><br />"""

        htmlC = """</body>
        </html>"""

        f.write(htmlO + "\n")

        f.write(str(head).replace('<br />', '').replace('628px', '800px') + "\n")
        f.write(str(table).replace('<br />', '').replace('628px;', '800px; border-top: 0;').replace('<tr>', '\n<tr>') + "\n")
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
