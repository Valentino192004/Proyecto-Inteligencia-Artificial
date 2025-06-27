from app import app
from routers.router_login import *
from routers.router_home import *
from routers.router_page_not_found import *
from routers.router_asistencia import *


if __name__ == '__main__':
        app.run(debug=True, host='0.0.0.0', port=5000)