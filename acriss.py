import requests
import re
import string
from bs4 import BeautifulSoup
import re
from collections import defaultdict
import json
from pathlib import Path

class Acriss:
    
    def __init__(self, update_codes=False, dir_data=None):
        
        if dir_data:
            Path(dir_data).mkdir(parents=True, exist_ok=True)
        else:
            dir_data = './data'
        
        if update_codes:
            self.get_codes()
            json.dump(self.cc_codes, open(dir_data + '/' + 'cc_codes.json', 'w'))
        else:
            try:
                self.cc_codes = json.load(open(dir_data + '/' + 'cc_codes.json'))
            except:
                print(f'failed to load data file. consider updating codes')
                return
    
    def get_codes(self):
        
        self.URL = 'https://www.acriss.org/car-codes/'
            
        r = requests.get(self.URL)
            
        if r.status_code != requests.codes.ok:
            print(f'ERROR: there is a problem with your request, code {r.status_code}..')
            return self
            
        sp = BeautifulSoup(r.text, 'html.parser')
        
        self.cc_codes = defaultdict(lambda: defaultdict())
        
        for w in sp.find('h3', text="Vehicle Matrix- Car Classification Codes").next_elements:
            
            if w.name == 'table':
                
                for i, _ in enumerate(w.find_all('tr')):
            
                    if i == 0:
                        hdr = [l.string.lower().replace(' / ', '/').replace('.','') for l in  _.select('td>strong')]
                        continue
                    
                    ls = [td.string for td in _.find_all('td')]
                    
                    if len(ls) == len(hdr)*2:
                        
                        for c, (letter, meaning) in zip(hdr, [(ls[j].lower(), ls[j+1].lower().replace('â\x89¥', '>=')) for j in range(0, len(hdr)*2, 2)]):
                            if letter in string.ascii_lowercase:
                                self.cc_codes[c][letter] = meaning

                break
        
        for p in sp.find('strong', text='PASSENGER VAN CODING*').parents:
            
            if p.name == 'tr' and p.has_attr('bgcolor'):
                
                for s in p.next_siblings:
                    
                    pr = []
                    
                    try:
                        for e in s.select('tr>td'):
                            st = e.get_text().strip().lower()
                            if len(st) > 1:
                                pr.append(st)
                    except:
                        pass
                    
                    if len(pr) == 2:
                        self.cc_codes['van_codes'][pr[0]] = re.sub('\xa0', ' ', pr[1])
                break
        
        return self
    
    def decode(self, code):
        
        return {c: self.cc_codes[c][l] for c, l in zip(self.cc_codes, code.lower())}