import http.client
import re
import json
import sys
from bs4 import BeautifulSoup

# Here are the parameters to set. See the README for more information
name = 'Martin Duke'
include_informational = False
include_experimental = True
include_acknowledgments = True
first_year = 2013
first_rfc = 4614
last_rfc = 20000
first_ad_year = 2020
# The filters below only apply to RFCs published before 'first_ad_year'
# Matching any of these is sufficient
#all values: streams = [ 'IAB', 'IETF', 'INDEPENDENT', 'IRTF' ]
streams = [ ]
#all values: areas = [ 'art', 'gen', 'int', 'ops', 'rtg', 'sec', 'tsv' ]
areas = [ 'tsv' ]
#all values: too many to list here; include 'NON' for non-WG; 'IESG' is also
# accepted
wgs = [ ]

# Result maps
author = {}
responsible_ad = {}
shepherd = {}
contributor = {}
balloted = {}
# not yet supported
art_reviewer = {}

rfced = http.client.HTTPSConnection('www.rfc-editor.org')
rfced.request('GET', '/rfc-index2.html')
try: rfced_resp = rfced.getresponse()
except ConnectionError as e:
    print(type(e).__qualname__)
    sys.exit()
else:
    rfc_list = rfced_resp.read()

# Set up datatracker connection
dt = http.client.HTTPSConnection('datatracker.ietf.org')

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
    if int(rfcnum) > last_rfc:
        continue
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
            print("Discarding No working group")
            continue
        if (doc["WG"] == 'IESG') and not ('IESG' in wgs):
            print("Discarding IESG working group")
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

    # Get the datatracker metadata
    dt.request('GET', '/doc/rfc'+rfcnum+'/doc.json')
    try: dt_resp = dt.getresponse()
    except ConnectionError as e:
        print("Could not retrieve .json: " + type(e).__qualname__)
        continue
    else:
        dt_json = dt_resp.read()
    # Check for author, shepherd, AD
    found = False
    dt_data = json.loads(dt_json)
    for auth_entry in dt_data['authors']:
        if auth_entry['name'] == name:
            author[rfcnum]= title
            found = True
            break
    if found:
        continue
    if dt_data['shepherd'] != None:
        shep = dt_data['shepherd'].split(" <")[0]
        if (shep == name):
            print("Shepherd")
            shepherd[rfcnum] = title
            continue
    if dt_data['ad'] != None:
        ad = dt_data['ad'].split(" <")[0]
        if (ad == name):
            print("Responsible AD")
            responsible_ad[rfcnum] = title
            continue

    # Check the text of the RFC for acknowledgments
    if include_acknowledgments:
        rfced.request('GET', '/rfc/rfc'+rfcnum+'.txt')
        try: rfced_resp = rfced.getresponse()
        except ConnectionError as e:
            print("Could not retrieve .txt: " + type(e).__qualname__)
            continue;
        else:
            rfc_txt = rfced_resp.read().decode('utf-8')
        if rfc_txt.find(name) >= 0:
            print("Contributor")
            contributor[rfcnum] = title
            continue

    if (year < first_ad_year):
        print("Name did not appear")
        continue

    # Check if balloted
    dt.request('GET', '/doc/rfc'+rfcnum+'/ballot/')
    try: dt_resp = dt.getresponse()
    except ConnectionError as e:
        print("Could not retrieve ballot: " + type(e).__qualname__)
        continue
    else:
        ballot_html = dt_resp.read()
    ballot_soup = BeautifulSoup(ballot_html, 'html.parser')
    for ad in ballot_soup.select('div[class="balloter-name"]'):
        if ad.a == None: # did not review
            continue
        ad_name = ad.get_text().strip()
        if (ad_name == name) or (ad_name == '(' + name + ')'):
            print("Balloted")
            found = True
            balloted[rfcnum] = title
            break

    if not found:
        print("Name did not appear")

rfced.close()
dt.close()
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
