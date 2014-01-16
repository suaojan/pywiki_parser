#!/usr/bin/python
from pyquery import PyQuery as pq
from lxml import etree
import codecs
import sys
import urllib2

sys.stdout = codecs.getwriter('utf-8')(sys.stdout) 

def denormalize(node, res):
    for child in node.getchildren():
        if child.get('title') is not None and len(child.get('title')) > 1:
            res.append(child.get('title'))
        if child.text is not None and len(child.text) > 1 :
            res.append(child.text)
        denormalize(child, res)
    return res

def parse_company(data):
    tree = pq(data)
    content = tree('table')('.infobox.vcard')('th')
    biz = {"industry":[], "service":[], "location":[]}

    for th in content:
        if th is not None:
            th_lower = ""
            if th.text is not None:
                th_lower = th.text.lower()
            else:
                for th_child in th.getchildren():
                    if th_child.text is not None:
                        th_lower = th_child.text.lower()
                        break
            if 'industry' in th_lower:
                for subl in th.itersiblings():
                    if subl.get('class') == "category" and subl.text is not None:
                        biz['industry'].append(subl.text)
                    biz['industry'] = denormalize(subl, biz['industry'])
            if 'service' in th_lower:
                for subl in th.itersiblings():
                    if subl.text is not None:
                        biz['service'].append(subl.text)
                    biz['service']  = denormalize(subl, biz['service'])

            if 'headquarter' in th_lower:
                for subl in th.itersiblings():
                    for child in subl.getchildren():
                        if child.get('title') is not None:
                            biz['location'].append(child.get('title'))
                        if child.text is not None:
                            biz['location'].append(child.text)
                        for grandchild in child.getchildren():
                            if grandchild.text is not None:
                                biz['location'].append(grandchild.text)
            if 'employees' in th_lower:
                for subl in th.itersiblings():
                    if biz.get('employees') is None:
                            biz['employees'] = ""
                    if subl.text is not None:
                        items = subl.text.split(" ")
#                        print items
                        last_item = False
                        last2 = False
                        xlist = ['over', 'appro', 'about', 'team', 'count', 'more', 'total', 'employ', 'global', 'staff', 'us']
                        for x in xlist:
                            if x in items[0].lower():
                                last_item = True
                                break
                        for x in xlist:
                            if x in items[-1].lower():
                                last2 = True
                                break
                        if last_item:
                            if not last2:
                                biz['employees'] = items[-1]
                            else:
                                biz['employees'] = items[-2]
                        else:
                            biz['employees'] = items[0]

    return biz

if __name__ == "__main__":
    
    #url = "http://en.wikipedia.org/wiki/Apple_Inc."
    url = "http://en.wikipedia.org/wiki/Craigslist"
    response = urllib2.urlopen(url).read()
    print parse_company(response)
           
