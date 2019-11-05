from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import json
import cgi

class Member(object):
    def __init__(self, name, parent = None):
        self.name = name
        #The set of things that are your parent
        self.original_parent = parent
        self.parents = set()
        if parent != None:
            self.add_parent(parent)
        #The set of things that you are parent to
        self.children = set()
        self.alternate_children = set()
    def add_alternate_child(self, child):
        self.alternate_children.add(child)
    def add_parent(self, parent):
        self.parents.add(parent)
        parent.children.add(self)
    def get_parent(self):
        if len(self.parents) == 1:
            return list(self.parents)[0]
        return None
    def is_bottom_level(self):
        return len(self.children) == 0
    def __eq__(self, other):
        if other == None:
            return False
        return self.name == other.name
    def __repr__(self):
        return self.name
    def __str__(self):
        return self.name
    def __hash__(self): 
        return hash(self.name)
    def toJSON(self):
        return {"name":self.name, "children": [child.toJSON() for child in self.children], "alternate_children": [child.toJSON() for child in self.alternate_children] }


def Account_Hierarchy_Template():
    ROOT = Member("ROOT")

    All_Accounts = Member("All Accounts", ROOT)
    Not_Account_Specific = Member("Not Account Specific", All_Accounts)
    Net_Income = Member("Net Income", All_Accounts)
    EBIT = Member("EBIT", Net_Income)
    Other_Income_Expense = Member("Other Income (Expense)", Net_Income)

    return ROOT

def Account_Hierarchy_Custom():
    ROOT = Member("ROOT")

    Money_Made = Member("Money Made", ROOT)
    Expenses = Member("Expenses", Money_Made)
    Tax = Member("Tax", Expenses)
    Fines = Member("Fines", Expenses)
    Wages = Member("Wages", Expenses)
    Sales = Member("Sales", Money_Made)
    Printers = Member("Printers", Sales)
    Phones = Member("Phones", Sales)
    Healing_Crystals = Member("Healing Crystals", Sales)

    return ROOT

def find_node(root, name):
    if root.name == name:
        return root
    for child in root.children:
      a = find_node(child, name)
      if a:
        return a
  
def serialize_model(model):
    for dim in model:
        dim_name = dim[0]
        print(dim_name)
        root = dim[1]
        return str(root.toJSON()).replace("'", '"')

def serialize_dimension(dim):
    return json.dumps(dim.toJSON())


class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header("Access-Control-Allow-Methods", "OPTIONS,POST,GET");
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_OPTIONS(self):
        print("Options")
        self._set_headers()
    def do_HEAD(self):
        self._set_headers()
        
    # GET sends back a Hello world message
    def do_GET(self):
        self._set_headers()
        self.wfile.write(json.dumps({"left":left.toJSON(), "right":right.toJSON()}))
        
    # POST echoes the message adding a JSON field
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        
        # refuse to receive non-json content
        #if ctype != 'application/json':
        #    self.send_response(400)
        #    self.end_headers()
        #    return
            
        # read the message and convert it into a python dictionary
        length = int(self.headers.getheader('content-length'))
        message = json.loads(self.rfile.read(length))
        
        # add a property to the object, just to mess with data
        parent = message["parent"]
        children = message["children"]
        #print(parent, children)
        parentNode = find_node(left, parent)
        #print(parentNode)
        for name in children:
          childNode = find_node(right, name)
          parentNode.add_alternate_child(childNode)
        
          
        # send the message back
        self._set_headers()
        self.wfile.write(json.dumps({"left":left.toJSON(), "right":right.toJSON()}))


left = Account_Hierarchy_Template()
right = Account_Hierarchy_Custom()
  

def run():
  print('starting server...')
 
  # Server settings
  # Choose port 8080, for port 80, which is normally used for a http server, you need root access
  server_address = ('127.0.0.1', 8082)
  httpd = HTTPServer(server_address, Server)
  print('running server...')
  httpd.serve_forever()
 
 
run()
