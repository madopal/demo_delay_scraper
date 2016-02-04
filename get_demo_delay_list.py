#!/usr/bin/env python 

import os, sys
import requests
from bs4 import BeautifulSoup
from argparse import ArgumentParser
import datetime
import pprint
import simplejson
import re

DEFAULT_URL = "http://www.cityofchicago.org/city/en/depts/dcd/supp_info/demolition-delay-hold-list--2015-.html"

URL_LIST = {
    '2014-8888' : "http://www.cityofchicago.org/city/en/depts/dcd/supp_info/demolition-delay-hold-list--2014-.html",
    '2003-2013': "http://www.cityofchicago.org/city/en/depts/dcd/supp_info/demolition_delayholdlist2003.html",
}

def parse_cmd_args():

    parser = ArgumentParser()
    parser.add_argument(
        "--url", 
        help="URL to scrape (default %s, where year is --year)" % URL_LIST['2014-8888'].replace('2014', str(datetime.datetime.now().year)), 
        default=URL_LIST['2014-8888']
    )
    parser.add_argument(
        "--years", 
        help="Years to get data for [2003-present, default %d]" % datetime.datetime.now().year,
        nargs="*",
        default=datetime.datetime.now().year,
        type=int
    )
    parser.add_argument("--save", help="Save results to file", dest="save", action="store_true")
    parser.add_argument("--pretty", help="Prettify the result printing", dest="pretty", action="store_true")
    parser.set_defaults(prettify=False, save=False)
    args = parser.parse_args()

    return args

def figure_out_url(year):
    url = None
    for key, value in URL_LIST.iteritems():
        range = key.split('-')
        if int(range[0]) <= year <= int(range[1]):
            url = value.replace(range[0], str(year))
    
    return url

def get_demo_hold(year):

    hold_list = []

    url = figure_out_url(year)

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
                                out_data = int(re.findall(r'\d+', part.split(':')[1].strip())[0])
                            else:
                                out_data = part.split(':')[1].strip()
                            hold_entry[part.split(':')[0].strip().lower().replace(" ", "_")] = out_data
                        elif '#' in part:
                            if '&' in part:
                                nums = part.split('&')
                                hold_entry['permit_numbers'] = []
                                for num in nums:
                                    try:
                                        hold_entry['permit_numbers'].append(int(num.strip().lstrip('#')))
                                    except:
                                        hold_entry['permit_numbers'].append(num.strip().lstrip('#'))
                            else:
                                try:
                                    hold_entry['permit_numbers'] = [int(part.lstrip('#').strip())]
                                except:
                                    hold_entry['permit_numbers'] = [part.lstrip('#').strip()]
                if len(hold_entry):
                    hold_list.append(hold_entry)
    else:
        print "Unable to retrieve %s" % url
        print r.status_code, r.reason

    return hold_list

if __name__ == '__main__':
    args = parse_cmd_args()
    hold_list = {}
    for year in args.years:
        hold_list[year] = get_demo_hold(year)

    if not args.save:
        if args.pretty:
            pp = pprint.PrettyPrinter(depth=3)
            pp.pprint(hold_list)
        else:
            print hold_list
    else:
        out_filename = "demo_delay-%s.json" % datetime.datetime.now().isoformat()
        with open(out_filename, "w") as out_file:
            simplejson.dump(hold_list, out_file)
            out_file.write('\n')
