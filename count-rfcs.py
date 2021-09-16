import urllib.request
import re
import sys
from bs4 import BeautifulSoup

# Here are the parameters to set. See the README for more information
name = 'M. Duke'
full_name = 'Martin Duke'
include_informational = False
include_experimental = False
include_acknowledgments = True
first_year = 2013
first_rfc = 4614
first_ad_year = 2020
# The filters below only apply to RFCs published before 'first_ad_year'
# Matching any of these is sufficient
#all values: streams = [ 'IAB', 'IETF', 'INDEPENDENT', 'IRTF' ]
streams = [ ]
#all values: areas = [ 'art', 'gen', 'int', 'ops', 'rtg', 'sec', 'tsv' ]
areas = [ 'tsv' ]
#all values: too many to list here; include 'NON' for non-WG
wgs = [ ]

# Result maps
author = {}
responsible_ad = {}
shepherd = {}
contributor = {}
balloted = {}
# not yet supported
art_reviewer = {}

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
    print(rfcnum, end=" ")
    # Break after documents I couldn't possibly have affected
    if int(rfcnum) < first_rfc:
        print("RFC number too early")
        break
    # Check other metadata before querying datatracker
    longline = row.td.find_next_sibling("td").get_text()
    if longline.find('Not Issued') >= 0:
        print ("Not issued")
        continue
    title = row.td.find_next_sibling("td").b.get_text()
    print('"' + title, end='": ')

    date = re.search(r"\[[ a-zA-Z0-9]+\]", longline)
    date = date[0].strip("[]")
    dmy = date.split(" ")
    year = int(dmy[len(dmy)-2])
    if (year < first_year):
        print("RFC year too early")
        break
    fields = re.finditer(r"[a-zA-Z0-9]+\: [a-zA-Z0-9]+", longline)
    doc = {}
    for fielditer in fields:
        field = fielditer.group()
        [key, value] = field.split(': ')
        doc[key] = value;

    # Do not apply stream, area, wg filters for ADs
    if (year < first_ad_year):
        if (doc["Stream"] != 'IETF') and not (doc["Stream"] in streams):
            print(doc["Stream"] + " stream not tracked")
            continue
        if (doc["WG"] == 'NON') and not ('NON' in wgs):
            print("No working group")
            continue
        if not ((doc["Area"] in areas) or (doc["WG"] in wgs)):
            print(doc["Area"] + " and " + doc["WG"] + " don't match")
            continue
    if (not include_informational) and (doc['Status'] == 'INFORMATIONAL'):
        print("Discarding INFORMATIONAL")
        continue
    if (not include_experimental) and (doc['Status'] == 'EXPERIMENTAL'):
        print("Discarding EXPERIMENTAL")
        continue

    if longline.find(name) >= 0:
        print("Authored")
        author[rfcnum] = title
        continue

    if (year > first_ad_year):
        # Extract the ballot
        ballot_review = False
        ballot_url='https://datatracker.ietf.org/doc/rfc'+rfcnum+'/ballot/'
        ballot_req = urllib.request.Request(ballot_url)
        try: ballot_resp = urllib.request.urlopen(ballot_req)
        except urllib.error.HTTPError as e:
            continue
        else:
            ballot_html = ballot_resp.read()
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
            print("Balloted")
            balloted[rfcnum] = title
        else:
            print("Name did not appear")
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
                print("Responsible AD")
                responsible_ad[rfc_num] = title
                found = true
                break
    if found:
        continue

    print("Acknowledged")
    contributor[rfcnum] = title



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
