import urllib.request
import re
import sys
from bs4 import BeautifulSoup

first_rfc = 4614
include_informational = True
include_experimental = True
name = 'M. Duke'
full_name = 'Martin Duke'

# Result lists
author = []
responsible_ad = []
shepherd = []
contributor = []
balloted = []
# not yet supported
art_reviewer = []

rfced_url = 'https://www.rfc-editor.org/rfc-index2.html'
rfced_req = urllib.request.Request(rfced_url)
try: rfced_resp = urllib.request.urlopen(rfced_req)
except urllib.error.HTTPError as e:
    print(e.reason)
    sys.exit()
else:
    rfc_list = rfced_resp.read()

rfc_soup = BeautifulSoup(rfc_list, 'html.parser')
# Find third table in document
table = rfc_soup.table
table = table.find_next_sibling("table")
table = table.find_next_sibling("table")
for row in table.contents:
    if row.name != 'tr':
        continue
    if (row.td.noscript == None):
        continue
    rfcnum = row.td.noscript.get_text()
    # Break after documents I couldn't possibly have affected
    if int(rfcnum) < first_rfc:
        break
    longline = row.td.find_next_sibling("td").get_text()
    if longline.find('Not Issued') >= 0:
        continue
    if (not include_informational) or (not include_experimental):
        status_block = re.findall(r'\(Status: .*?\)', longline)
        status = status_block[0][9:(len(status_block[0])-1)]
        if (not include_informational) and (status == 'INFORMATIONAL'):
            continue
        if (not include_experimental) and (status == 'EXPERIMENTAL'):
            continue
    if longline.find(name) >= 0:
        authored.append(rfcnum.encode('ascii'))
        continue
    # Extract the ballot
    ballot_review = False
    ballot_url='https://datatracker.ietf.org/doc/rfc'+rfcnum+'/ballot/'
    ballot_req = urllib.request.Request(ballot_url)
    try: ballot_resp = urllib.request.urlopen(ballot_req)
    except urllib.error.HTTPError as e:
        continue
    else:
        ballot_html = ballot_resp.read()
    print("\n" + rfcnum, end=" ")
    ballot_soup = BeautifulSoup(ballot_html, 'html.parser')
    for ad in ballot_soup.select('div[class="balloter-name"]'):
        if ad.a == None: # did not review
            continue
        ad_name = ad.get_text().strip()
        if (ad_name == full_name) or (ad_name == '(' + full_name + ')'):
            ballot_review = True

    # Get the datatracker page
    dt_url='https://datatracker.ietf.org/doc/rfc'+rfcnum+'/'
    dt_req = urllib.request.Request(dt_url)
    try: dt_resp = urllib.request.urlopen(dt_req)
    except urllib.error.HTTPError as e:
        continue
    else:
        dt_html = dt_resp.read()
    uc_name = full_name.encode('utf-8')
    if (dt_html.find(uc_name) < 0):
        if ballot_review:
            print("Balloted", end="")
            balloted.append(rfcnum.encode('ascii'))
        continue
    found = False
    dtsoup = BeautifulSoup(dt_html, 'html.parser')
    dtsoup_tables = dtsoup.findChildren('table')
    dtsoup_body = dtsoup_tables[0].findChildren('tbody')
    # Extract Shepherd
    dttable = dtsoup_body[2]
    entries = dttable.findChildren('tr')
    for entry in entries:
        cols = entry.findChildren('th')
        if len(cols) < 2:
            continue
        key = cols[1].text.strip()
        if (key == "Document shepherd"):
            values = entry.findChildren('td')
            value = values[1].text.strip()
            #print("shepherd: " + value)
            if (value == full_name):
                print("Shepherd",end="")
                shepherd.append(rfcnum.encode('ascii'))
                found = true
                break
    if found:
        continue

    # Extract Responsible AD
    dttable = dtsoup_body[3]
    entries = dttable.findChildren('tr')
    for entry in entries:
        cols = entry.findChildren('th')
        if len(cols) < 2:
            continue
        key = cols[1].text.strip()
        values = entry.findChildren('td')
        value = values[1].text.strip()
        if (key == "Responsible AD"):
            values = entry.findChildren('td')
            value = values[1].text.strip()
            #print("AD: " + value)
            if value == full_name:
                print("Responsible AD",end="")
                responsible_ad.append(rfcnum.encode('ascii'))
                found = true
                break
    if found:
        continue

    print("Acknowledged", end="")
    contributor.append(rfcnum.encode('ascii'))



print("Authored: " + str(len(author)))
print(author)
print("Shepherded:" + str(len(shepherd)))
print(shepherd)
print("Responsible AD: " + str(len(responsible_ad)))
print(responsible_ad)
print("Balloted: " + str(len(balloted)))
print(balloted)
print("Acknowledged: " + str(len(contributor)))
print(contributor)
