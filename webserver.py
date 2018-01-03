from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem


# Connect to DB and create session
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class WebserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurants = session.query(Restaurant).all()

                output = ""
                output += "<html><body>"
                output += "<a href='/restaurants/new'>Make a New Restaurant Here</a><br><br>"
                for rt in restaurants:
                    output += "%s<br>" % rt.name
                    output += "<a href='/restaurants/%s/edit'>Edit</a>" % rt.id
                    output += " "
                    output += "<a href='/restaurants/%s/delete'>Delete</a><br><br>" % rt.id
                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
                output += "<input name='r_name' type='text' placeholder='New Restaurant Name'>"
                output += "<input type='submit' value='Create'>"
                output += "</form></body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/edit"):
                r_id = self.path.split('/')[2]
                target_restaurant = session.query(Restaurant).filter_by(id=r_id).one()

                if target_restaurant:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    output = ""
                    output += "<html><body>"
                    output += "<h1>Edit Restaurant</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" % r_id
                    output += "<input name='r_name' type='text' placeholder=\"%s\">" % target_restaurant.name
                    output += "<input type='submit' value='Rename' >"
                    output += "</form></body></html>"
                    self.wfile.write(output)
                return

            if self.path.endswith("/delete"):
                r_id = self.path.split('/')[2]
                target_restaurant = session.query(Restaurant).filter_by(id=r_id).one()

                if target_restaurant:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    output = ""
                    output += "<html><body>"
                    output += "<h1>Edit Restaurant</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>" % r_id
                    output += "<h1>Are you sure to delete Restaurant %s?</h1>" % target_restaurant.name
                    output += "<input type='submit' value='Delete'>"
                    output += "</form></body></html>"
                    print(output)
                    self.wfile.write(output)
                return

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    r_name_content = fields.get('r_name')
                    newRestaurant = Restaurant(name=r_name_content[0])
                    session.add(newRestaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
                return

            if self.path.endswith("/edit"):
                r_id = self.path.split('/')[2]
                target_restaurant = session.query(Restaurant).filter_by(id=r_id).one()

                if target_restaurant:
                    ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

                    if ctype == 'multipart/form-data':
                        fields = cgi.parse_multipart(self.rfile, pdict)
                        r_name_content = fields.get('r_name')
                        target_restaurant.name = r_name_content[0]
                        session.add(target_restaurant)
                        session.commit()

                        self.send_response(301)
                        self.send_header('Location', '/restaurants')
                        self.end_headers()
                return

            if self.path.endswith("/delete"):
                r_id = self.path.split('/')[2]
                target_restaurant = session.query(Restaurant).filter_by(id=r_id).one()
                print("to delete r_id: {}".format(r_id))
                if target_restaurant:
                    session.delete(target_restaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
                return

        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebserverHandler)
        print "Web server runing on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()


if __name__ == '__main__':
    main()
