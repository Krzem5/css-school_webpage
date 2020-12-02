import server
import pages
import api
import os



server.run(int(os.environ.get("PORT",0)))
