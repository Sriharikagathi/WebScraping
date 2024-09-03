import http.server
import socketserver
import http.client
import json
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_h3 = False
        self.in_a = False
        self.stories = []
        self.current_title = ""
        self.current_link = ""

    def handle_starttag(self, tag, attrs):
        if tag == 'h3':
            self.in_h3 = True
        elif tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    self.current_link = attr[1]
                    self.in_a = True

    def handle_endtag(self, tag):
        if tag == 'h3' and self.in_h3:
            if self.current_link:
                self.stories.append({"title": self.current_title.strip(), "link": self.current_link})
            self.current_title = ""
            self.in_h3 = False
        elif tag == 'a':
            self.in_a = False

    def handle_data(self, data):
        if self.in_h3:
            self.current_title += data

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/getTimeStories":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = self.get_time_stories()
            self.wfile.write(response.encode())
        else:
            super().do_GET()

    def get_time_stories(self):
        conn = http.client.HTTPSConnection("time.com")
        conn.request("GET", "/")
        response = conn.getresponse()
        html_content = response.read().decode()
        conn.close()

        parser = MyHTMLParser()
        parser.feed(html_content)
        
        stories = parser.stories[:6]
        for story in stories:
            if not story['link'].startswith('http'):
                story['link'] = f"https://time.com{story['link']}"
        
        return json.dumps(stories, indent=2)

PORT = 8080
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print("Server running on port", PORT)
    httpd.serve_forever()
