import api
import os
import pages
import server



api.install()
pages.install()
server.run(int(os.environ.get("PORT",0)))
