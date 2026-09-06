from html.parser import HTMLParser

class ViewHierarchyParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.geography_parent = None
        self.geography_inside_delivery = False
        self.canvas_found = False
        self.tbody_found = False

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        eid = attr_dict.get('id', '')
        cls = attr_dict.get('class', '')
        
        # Check if entering geography
        if eid == 'view-geography':
            # Store immediate parent
            if self.stack:
                self.geography_parent = self.stack[-1]
            # Check if inside view-delivery
            for p_tag, p_id, p_cls in self.stack:
                if p_id == 'view-delivery':
                    self.geography_inside_delivery = True
                    
        # Check elements inside view-geography
        if len(self.stack) > 0:
            for p_tag, p_id, p_cls in self.stack:
                if p_id == 'view-geography':
                    if eid == 'chartGeoScope':
                        self.canvas_found = True
                    if eid == 'tbodyGeoHotspots':
                        self.tbody_found = True
                        
        if tag not in ['img', 'br', 'hr', 'input', 'meta', 'link']:
            self.stack.append((tag, eid, cls))

    def handle_endtag(self, tag):
        if tag not in ['img', 'br', 'hr', 'input', 'meta', 'link']:
            if self.stack:
                self.stack.pop()

with open('app/index.html', 'r', encoding='utf-8') as f:
    parser = ViewHierarchyParser()
    parser.feed(f.read())

print("=== GEOGRAPHY TAB DOM VERIFICATION ===")
print("Is #view-geography nested inside #view-delivery?:", parser.geography_inside_delivery)
print("Immediate parent tag of #view-geography:", parser.geography_parent)
print("Canvas #chartGeoScope present inside #view-geography?:", parser.canvas_found)
print("Table body #tbodyGeoHotspots present inside #view-geography?:", parser.tbody_found)
