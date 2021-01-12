import api
import os
import pages
import server



server.run(int(os.environ.get("PORT",0)))
