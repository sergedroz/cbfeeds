import sys
import os
import time

# third part lib imports
import requests

from distutils.version import StrictVersion

if StrictVersion(requests.__version__) < StrictVersion("1.2.3"):
    # only in 1.2.3+ did response objects support iteration 
    raise ImportError("requires requests >= 1.2.3")

# our imports
sys.path.insert(0, "../../")
from cbfeeds import CbReport
from cbfeeds import CbFeed
from cbfeeds import CbFeedInfo


def get_zeus():
    reports = []
    r = requests.get("https://zeustracker.abuse.ch/blocklist.php?download=domainblocklist")
    lines = r.text.split("\n")
    domains = []
    for line in lines:
        if len(line) < 3: continue
        if line[0] == "#": continue

        domains.append(line.strip())

    fields = {'iocs': {
        "dns": domains,
    },
        'timestamp': int(time.mktime(time.gmtime())),
        'link': "https://zeustracker.abuse.ch/blocklist.php?download=domainblocklist",
        'id': 'abusech-zeus',
        'title': 'abuse.ch Zeus hit on Standard domain blocklist',
        'score': 100,
    }
    if domains:
        reports.append(CbReport(**fields))
        return reports
    else:
        return []

def get_feodo():
    reports = []
    r = requests.get("https://feodotracker.abuse.ch/blocklist/?download=domainblocklist")
    lines = r.text.split("\n")
    domains = []
    for line in lines:
        if len(line) < 3: continue
        if line[0] == "#": continue

        domains.append(line.strip())
    
    fields = {'iocs': {
        "dns": domains,
    },
        'timestamp': int(time.mktime(time.gmtime())),
        'link': "https://feodotracker.abuse.ch/blocklist/?download=domainblocklist",
        'id': 'abusech-feodo',
        'title': 'abuse.ch feodo Domain hit on domain blocklist',
        'score': 100,
    }
    if domains:
        reports.append(CbReport(**fields))
        return reports
    else:
        return []

def get_ransomware():
    reports = []
    r = requests.get("https://ransomwaretracker.abuse.ch/downloads/RW_DOMBL.txt")
    lines = r.text.split("\n")
    domains = []
    for line in lines:
        if len(line) < 3: continue
        if line[0] == "#": continue

        domains.append(line.strip())

    fields = {'iocs': {
        "dns": domains,
    },
        'timestamp': int(time.mktime(time.gmtime())),
        'link': "https://ransomwaretracker.abuse.ch/downloads/RW_DOMBL.txt",
        'id': 'abusech-ransomware',
        'title': 'abuse.ch Ransomware on domain blocklist',
        'score': 100,
    }
    if domains:
        reports.append(CbReport(**fields))
        return reports
    else:
        return []

def create():
    reports = []
    tmp = get_zeus()
    if tmp:
        reports.extend(tmp)
    tmp = get_feodo()
    if tmp:
        reports.extend(tmp)
    tmp = get_ransomware()
    if tmp:
        reports.extend(tmp)

    feedinfo = {'name': 'abusech',
                'display_name': "abuse.ch Malware Domains",
                'provider_url': "http://www.abuse.ch",
                'summary': "abuse.ch tracks C&C servers for Zeus and Palevo malware. " +
                           "This feed combines the two domain names blocklists.",
                'tech_data': "There are no requirements to share any data to receive this feed.",
                'icon': "abuse.ch.jpg",
                'icon_small': "abuse.ch.small.jpg",
                'category': "Open Source"
                }

    # the lazy way to the icon 
    old_cwd = os.getcwd()
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    feedinfo = CbFeedInfo(**feedinfo)
    feed = CbFeed(feedinfo, reports)
    feed_bytes = feed.dump()

    os.chdir(old_cwd)

    return feed_bytes


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: generate_abuse.ch_feed.py [outfile]")
        sys.exit()

    feed_created = create()
    open(sys.argv[1], "w").write(feed_created)
