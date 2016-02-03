#!/usr/bin/env python 

import os, sys
import requests
from bs4 import BeautifulSoup
from argparse import ArgumentParser
import datetime
import pprint
import simplejson

DEFAULT_URL = "http://www.cityofchicago.org/city/en/depts/dcd/supp_info/demolition-delay-hold-list--2015-.html"

def parse_cmd_args():

    parser = ArgumentParser()
    parser.add_argument("--url", help="URL to scrape (default %s, where year is year" % DEFAULT_URL, default=DEFAULT_URL)
    parser.add_argument(
        "--year", 
        help="Year to get data for [2014-present, default %d" % datetime.datetime.now().year,
        default=datetime.datetime.now().year,
        type=int
    )
    parser.add_argument("--save", help="Save results to file", dest="save", action="store_true")
    parser.add_argument("--pretty", help="Prettify the result printing", dest="pretty", action="store_true")
    parser.set_defaults(prettify=False, save=False)
    args = parser.parse_args()

    return args

hold_list = []

args = parse_cmd_args()

if args.year != 2015:
    url = args.url.replace("2015", str(args.year))
else:
    url = args.url

print "Attempting %s" % url
r = requests.get(url)
if r.status_code == 200:
    data = BeautifulSoup(r.text, "lxml")
    results = data.find_all('p')
    for entry in results:
        if 'status' in entry.get_text().lower():
            hold_entry = {}
            for part in entry:
                if isinstance(part, basestring):
                    if ':' in part:
                        if part.split(':')[0].strip().lower().replace(" ", "_") == u"ward":
                            out_data = int(part.split(':')[1].strip())
                        else:
                            out_data = part.split(':')[1].strip()
                        hold_entry[part.split(':')[0].strip().lower().replace(" ", "_")] = out_data
                    elif '#' in part:
                        hold_entry['permit_number'] = int(part.lstrip('#').strip())
            if len(hold_entry):
                hold_list.append(hold_entry)
else:
    print "Unable to retrieve %s" % url
    print r.status_code, r.reason

if not args.save:
    if args.pretty:
        pp = pprint.PrettyPrinter(depth=2)
        pp.pprint(hold_list)
    else:
        print hold_list
else:
    out_filename = "demo_delay_%s.json" % datetime.datetime.now().isoformat()
    with open(out_filename, "w") as out_file:
        for entry in hold_list:
            simplejson.dump(entry, out_file)
            out_file.write('\n')
