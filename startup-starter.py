from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from startup_setup import Startup, Base, Founder

engine = create_engine('sqlite:///startup.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/startups"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                startups = session.query(Startup).all()
                output = ""
                output += "<html><body>"
                output += "<a href=\"/startups/new\">create startup!</a>"
                output +="<br>"
                for startup in startups:
                    output +="<br>"
                    output += "<a href=\"/startup/" + str(startup.id) + "/view\">" + startup.name + "</a>"
                    output +="<br>"
                    output += "<a href='/startups/%s/edit'> edit</a> "%startup.id
                    output += "<a href='/startups/%s/delete' > delete </a>"%startup.id
                    output +="<br><br>"
                output += "</body></html>"
                self.wfile.write(output)

                return


            if self.path.endswith("/startups/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<form method ='POST' enctype='multipart/form-data' action ='/startups/new'>"
                output += "<input type='text' name='name' placeholder='name'/>"
                output += "<button type='submit'> create startup! </button>"
                output += "</form></body></html>"
                self.wfile.write(output)

                return

            if self.path.endswith("/edit"):
                startup_id = self.path.split("/")[2]
                startup = session.query(Startup).filter_by(id=startup_id).one()

                if startup:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<form method ='POST' enctype='multipart/form-data' action ='/startups/%s/edit'>"%startup.id
                    output += "<input type='text' name='name' value='%s' placeholder='name'/>"%startup.name
                    output += "<button type='submit'> edit </button>"
                    output += "</form></body></html>"
                    self.wfile.write(output)

                    return

            if self.path.endswith("/delete"):
                startup_id = self.path.split("/")[2]
                startup = session.query(Startup).filter_by(id=startup_id).one()

                if startup:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body><form method ='POST' enctype='multipart/form-data' action ='/startups/%s/delete'>"%startup.id
                    output += "<label>%s</label>"%startup.name
                    output += "<button type='submit'> delete </button>"
                    output += "</form></body></html>"
                    self.wfile.write(output)

                    return

            if self.path.endswith("/view"):

                startup_id = self.path.split("/")[2]
                startup = session.query(Startup).filter_by(id=startup_id).one()
                founders = session.query(Founder).filter_by(startup_id=startup_id).all()

                if startup:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h3>Startup Name:</h3>"
                    output += startup.name
                    output += "<h3>Founders:</h3>"
                    output += "<ul>"
                    for founder in founders:
                        output +="<li>%s<br>%s<br><br></li>"%(founder.name, founder.bio)
                    output += "</ul>"
                    output += "<form method ='POST' enctype='multipart/form-data' action ='/founders/new'>"
                    output += "<input type='text' name='name' placeholder='name'/>"
                    output += "<input type='text' name='bio' placeholder='bio'/>"
                    output += "<input type='hidden' name='startup_id' value='" + startup_id + "'/>"
                    output += "<button type='submit'> Add Founder! </button>"
                    output += "</body></html>"
                    self.wfile.write(output)

                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith('/edit'):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    startup_name = fields.get('name')
                    startup_id = self.path.split("/")[2]
                    startup = session.query(Startup).filter_by(id=startup_id ).one()
                    startup.name = startup_name[0]
                    session.add(startup)
                    session.commit()
                    self.send_response(301)
                    self.send_header('content-type', "text/html")
                    self.send_header('Location', "/startups")
                    self.end_headers()

            if self.path.endswith('/delete'):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)

                    startup_id = self.path.split("/")[2]
                    startup = session.query(Startup).filter_by(id=startup_id ).one()

                    session.delete(startup)
                    session.commit()
                    self.send_response(301)
                    self.send_header('content-type', "text/html")
                    self.send_header('Location', "/startups")
                    self.end_headers()

            if self.path.endswith('/startups/new'):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    startup_name = fields.get('name')
                    startup = Startup(name=startup_name[0])
                    session.add(startup)
                    session.commit()
                    self.send_response(301)
                    self.send_header('content-type', "text/html")
                    self.send_header('Location', "/startups")
                    self.end_headers()

            if self.path.endswith('/founders/new'):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    founder_name = fields.get('name')
                    founder_bio = fields.get('bio')
                    startup_id = fields.get('startup_id')
                    founder = Founder(name=founder_name[0], bio=founder_bio[0], startup_id=startup_id[0])
                    session.add(founder)
                    session.commit()
                    self.send_response(301)
                    self.send_header('content-type', "text/html")
                    redirect_path = "/startup/" + startup_id[0] + "/view"
                    self.send_header('Location', redirect_path)
                    self.end_headers()


        except:
            pass


def main():
    try:
        port = 8000
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
