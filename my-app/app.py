from flask import Flask
from routers.router_ia import ia_bp

app = Flask(__name__)
application = app
app.secret_key = '97110c78ae51a45af397b6534caef90ebb9b1dcb3380f008f90b23a5d1616bf1bc29098105da20fe'

# Registramos el blueprint del módulo IA
app.register_blueprint(ia_bp)

# Aquí puedes seguir registrando otros routers si tienes más:
# from routers.router_login import login_bp
# app.register_blueprint(login_bp)

if __name__ == '__main__':
    app.run(debug=True)
