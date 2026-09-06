from html.parser import HTMLParser

class TagChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in ['img', 'br', 'hr', 'input', 'meta', 'link']:
            attr_dict = dict(attrs)
            element_id = attr_dict.get('id', '')
            cls = attr_dict.get('class', '')
            self.stack.append((tag, element_id, cls, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in ['img', 'br', 'hr', 'input', 'meta', 'link']:
            return
        if not self.stack:
            self.errors.append(f"Unexpected end tag </{tag}> at line {self.getpos()[0]}")
            return
        last_tag, eid, cls, line = self.stack[-1]
        if last_tag == tag:
            self.stack.pop()
        else:
            self.errors.append(f"Mismatched end tag </{tag}> at line {self.getpos()[0]}, expected </{last_tag}> (opened line {line} #{eid} .{cls})")

with open('app/index.html', 'r', encoding='utf-8') as f:
    checker = TagChecker()
    checker.feed(f.read())

print("Unclosed tags at EOF:")
for tag, eid, cls, line in checker.stack:
    if eid or 'tab-view' in cls or 'card' in cls or 'grid' in cls:
        print(f"  Line {line}: <{tag} id=\"{eid}\" class=\"{cls}\">")

print("\nErrors during parsing:")
for err in checker.errors[:10]:
    print(" ", err)
