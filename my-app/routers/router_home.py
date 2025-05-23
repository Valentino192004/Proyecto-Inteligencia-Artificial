from app import app
from flask import render_template, request, flash, redirect, url_for, session,  jsonify
from mysql.connector.errors import Error
from werkzeug.security import generate_password_hash


# Importando cenexión a BD
from controllers.funciones_home import *

PATH_URL = "public/empleados"


@app.route('/registrar-empleado', methods=['GET'])
def viewFormEmpleado():
    if 'conectado' in session:
        return render_template(f'{PATH_URL}/form_empleado.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

# Ruta exclusiva API REST que devuelve JSON
@app.route('/api/lista-empleados', methods=['GET'])
def api_lista_empleados():
    empleados = sql_lista_empleadosBD()
    return jsonify(empleados)


@app.route('/form-registrar-empleado', methods=['POST'])
def formEmpleado():
    if 'conectado' in session:
        if 'foto_empleado' in request.files:
            foto_perfil = request.files['foto_empleado']
            resultado = procesar_form_empleado(request.form, foto_perfil)
            if resultado:
                return redirect(url_for('lista_empleados'))
            else:
                flash('El empleado NO fue registrado.', 'error')
                return render_template(f'{PATH_URL}/form_empleado.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

# Ruta exclusiva API REST que devuelve JSON
@app.route('/api/form-registrar-empleado', methods=['POST'])
def api_form_empleado():
    if 'conectado' not in session:
        return jsonify({"success": False, "message": "Primero debes iniciar sesión"}), 401

    if 'foto_empleado' not in request.files:
        return jsonify({"success": False, "message": "No se envió la foto del empleado"}), 400

    foto_perfil = request.files['foto_empleado']
    resultado = procesar_form_empleado(request.form, foto_perfil)

    # Verifica si hubo error técnico (retorno es string con error)
    if isinstance(resultado, str):
        return jsonify({"success": False, "message": resultado}), 500

    # Verifica si se insertó un registro
    if resultado == 1:
        return jsonify({"success": True, "message": "Empleado registrado correctamente"}), 201
    else:
        return jsonify({"success": False, "message": "No se pudo registrar el empleado"}), 400



@app.route('/lista-de-empleados', methods=['GET'])
def lista_empleados():
    if 'conectado' in session:
        return render_template(f'{PATH_URL}/lista_empleados.html', empleados=sql_lista_empleadosBD())
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route("/detalles-empleado/", methods=['GET'])
@app.route("/detalles-empleado/<int:idEmpleado>", methods=['GET'])
def detalleEmpleado(idEmpleado=None):
    if 'conectado' in session:
        # Verificamos si el parámetro idEmpleado es None o no está presente en la URL
        if idEmpleado is None:
            return redirect(url_for('inicio'))
        else:
            detalle_empleado = sql_detalles_empleadosBD(idEmpleado) or []
            return render_template(f'{PATH_URL}/detalles_empleado.html', detalle_empleado=detalle_empleado)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

# Ruta exclusiva API REST que devuelve JSON
@app.route("/api/detalles-empleado/<int:idEmpleado>", methods=['GET'])
def api_detalle_empleado(idEmpleado):
    if 'conectado' not in session:
        return jsonify({"success": False, "message": "Primero debes iniciar sesión"}), 401

    detalle_empleado = sql_detalles_empleadosBD(idEmpleado)

    if detalle_empleado:
        return jsonify({"success": True, "data": detalle_empleado}), 200
    else:
        return jsonify({"success": False, "message": "Empleado no encontrado"}), 404

# Buscadon de empleados
@app.route("/buscando-empleado", methods=['POST'])
def viewBuscarEmpleadoBD():
    resultadoBusqueda = buscarEmpleadoBD(request.json['busqueda'])
    if resultadoBusqueda:
        return render_template(f'{PATH_URL}/resultado_busqueda_empleado.html', dataBusqueda=resultadoBusqueda)
    else:
        return jsonify({'fin': 0})


@app.route("/editar-empleado/<int:id>", methods=['GET'])
def viewEditarEmpleado(id):
    if 'conectado' in session:
        respuestaEmpleado = buscarEmpleadoUnico(id)
        if respuestaEmpleado:
            return render_template(f'{PATH_URL}/form_empleado_update.html', respuestaEmpleado=respuestaEmpleado)
        else:
            flash('El empleado no existe.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# Recibir formulario para actulizar informacion de empleado
@app.route('/actualizar-empleado', methods=['POST'])
def actualizarEmpleado():
    resultData = procesar_actualizacion_form(request)
    if resultData:
        return redirect(url_for('lista_empleados'))

@app.route('/api/actualizar-empleado/<int:id_empleado>', methods=['PUT'])
def api_actualizar_empleado(id_empleado):
    if 'conectado' not in session:
        return jsonify({"success": False, "message": "Primero debes iniciar sesión"}), 401

    dataForm = request.form
    foto_empleado = request.files.get('foto_empleado')

    # Validación de campos obligatorios
    campos_requeridos = ['nombre_empleado', 'apellido_empleado', 'sexo_empleado',
                        'telefono_empleado', 'email_empleado', 'profesion_empleado', 'salario_empleado']

    for campo in campos_requeridos:
        if campo not in dataForm:
            return jsonify({"success": False, "message": f"Falta el campo: {campo}"}), 400

    # Procesar salario
    salario_sin_puntos = re.sub('[^0-9]+', '', dataForm['salario_empleado'])
    salario_entero = int(salario_sin_puntos) if salario_sin_puntos else 0

    # Convertir sexo si viene como texto
    sexo = dataForm['sexo_empleado']
    if sexo.lower() in ['masculino', 'femenino']:
        sexo = 1 if sexo.lower() == 'masculino' else 2
    else:
        sexo = int(sexo)

    try:
        with connectionBD() as conn:
            with conn.cursor(dictionary=True) as cursor:
                if foto_empleado:
                    nueva_foto = procesar_imagen_perfil(foto_empleado)
                    sql = """
                        UPDATE tbl_empleados SET 
                        nombre_empleado = %s,
                        apellido_empleado = %s,
                        sexo_empleado = %s,
                        telefono_empleado = %s,
                        email_empleado = %s,
                        profesion_empleado = %s,
                        salario_empleado = %s,
                        foto_empleado = %s
                        WHERE id_empleado = %s
                    """
                    valores = (
                        dataForm['nombre_empleado'],
                        dataForm['apellido_empleado'],
                        sexo,
                        dataForm['telefono_empleado'],
                        dataForm['email_empleado'],
                        dataForm['profesion_empleado'],
                        salario_entero,
                        nueva_foto,
                        id_empleado
                    )
                else:
                    sql = """
                        UPDATE tbl_empleados SET 
                        nombre_empleado = %s,
                        apellido_empleado = %s,
                        sexo_empleado = %s,
                        telefono_empleado = %s,
                        email_empleado = %s,
                        profesion_empleado = %s,
                        salario_empleado = %s
                        WHERE id_empleado = %s
                    """
                    valores = (
                        dataForm['nombre_empleado'],
                        dataForm['apellido_empleado'],
                        sexo,
                        dataForm['telefono_empleado'],
                        dataForm['email_empleado'],
                        dataForm['profesion_empleado'],
                        salario_entero,
                        id_empleado
                    )

                cursor.execute(sql, valores)
                conn.commit()

                if cursor.rowcount > 0:
                    return jsonify({"success": True, "message": "Empleado actualizado correctamente"}), 200
                else:
                    return jsonify({"success": False, "message": "Empleado no encontrado o sin cambios"}), 404

    except Exception as e:
        return jsonify({"success": False, "message": f"Error al actualizar: {str(e)}"}), 500



@app.route("/lista-de-usuarios", methods=['GET'])
def usuarios():
    if 'conectado' in session:
        resp_usuariosBD = lista_usuariosBD()
        return render_template('public/usuarios/lista_usuarios.html', resp_usuariosBD=resp_usuariosBD)
    else:
        return redirect(url_for('inicioCpanel'))

#API Lista usuarios (GET)
@app.route('/api/lista-usuarios', methods=['GET'])
def api_lista_usuarios():
    if 'conectado' not in session:
        return jsonify({"success": False, "message": "Primero debes iniciar sesión"}), 401

    try:
        with connectionBD() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT id, name_surname, email_user FROM users")
                usuarios = cursor.fetchall()

                return jsonify({
                    "success": True,
                    "data": usuarios,
                    "total": len(usuarios)
                }), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

#API Ver usuario por ID (GET)
@app.route('/api/detalles-usuario/<int:id_usuario>', methods=['GET'])
def api_detalles_usuario(id_usuario):
    if 'conectado' not in session:
        return jsonify({"success": False, "message": "Primero debes iniciar sesión"}), 401

    try:
        with connectionBD() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    "SELECT id, name_surname, email_user FROM users WHERE id = %s", (id_usuario,)
                )
                usuario = cursor.fetchone()

                if usuario:
                    return jsonify({
                        "success": True,
                        "data": usuario
                    }), 200
                else:
                    return jsonify({
                        "success": False,
                        "message": "Usuario no encontrado"
                    }), 404

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al consultar usuario: {str(e)}"
        }), 500


@app.route('/borrar-usuario/<string:id>', methods=['GET'])
def borrarUsuario(id):
    resp = eliminarUsuario(id)
    if resp:
        flash('El Usuario fue eliminado correctamente', 'success')
        return redirect(url_for('usuarios'))


@app.route('/borrar-empleado/<string:id_empleado>/<string:foto_empleado>', methods=['GET'])
def borrarEmpleado(id_empleado, foto_empleado):
    resp = eliminarEmpleado(id_empleado, foto_empleado)
    if resp:
        flash('El Empleado fue eliminado correctamente', 'success')
        return redirect(url_for('lista_empleados'))

@app.route('/api/eliminar-empleado/<int:id_empleado>', methods=['DELETE'])
def api_eliminar_empleado(id_empleado):
    if 'conectado' not in session:
        return jsonify({"success": False, "message": "Primero debes iniciar sesión"}), 401

    try:
        with connectionBD() as conexion:
            with conexion.cursor(dictionary=True) as cursor:
                # Obtener la foto del empleado antes de eliminar
                cursor.execute("SELECT foto_empleado FROM tbl_empleados WHERE id_empleado = %s", (id_empleado,))
                empleado = cursor.fetchone()

                if not empleado:
                    return jsonify({"success": False, "message": "Empleado no encontrado"}), 404

                # Eliminar el registro
                cursor.execute("DELETE FROM tbl_empleados WHERE id_empleado = %s", (id_empleado,))
                conexion.commit()

                # Eliminar la foto físicamente (opcional)
                if empleado['foto_empleado']:
                    ruta_foto = os.path.join(os.getcwd(), empleado['foto_empleado'])
                    if os.path.exists(ruta_foto):
                        os.remove(ruta_foto)

                return jsonify({"success": True, "message": "Empleado eliminado correctamente"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": f"Error al eliminar: {str(e)}"}), 500

#API Eliminar usuario (DELETE)
@app.route('/api/eliminar-usuario/<int:id_usuario>', methods=['DELETE'])
def api_eliminar_usuario(id_usuario):
    if 'conectado' not in session:
        return jsonify({"success": False, "message": "Primero debes iniciar sesión"}), 401

    try:
        with connectionBD() as conn:
            with conn.cursor() as cursor:
                # Verificar que el usuario exista antes de eliminar
                cursor.execute("SELECT id FROM users WHERE id = %s", (id_usuario,))
                user = cursor.fetchone()

                if not user:
                    return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

                # Ejecutar eliminación
                cursor.execute("DELETE FROM users WHERE id = %s", (id_usuario,))
                conn.commit()

                return jsonify({
                    "success": True,
                    "message": "Usuario eliminado correctamente"
                }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al eliminar usuario: {str(e)}"
        }), 500


#API Registrar usuario (POST)
@app.route('/api/registrar-usuario', methods=['POST'])
def api_registrar_usuario():
    data = request.form

    required_fields = ['name_surname', 'email_user', 'pass_user']
    for campo in required_fields:
        if campo not in data or not data[campo]:
            return jsonify({
                "success": False,
                "message": f"El campo '{campo}' es obligatorio"
            }), 400

    name_surname = data['name_surname']
    email_user = data['email_user']
    pass_user = data['pass_user']
    hashed_pass = generate_password_hash(pass_user)

    try:
        with connectionBD() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (name_surname, email_user, pass_user) VALUES (%s, %s, %s)",
                    (name_surname, email_user, hashed_pass)
                )
                conn.commit()

                return jsonify({
                    "success": True,
                    "message": "Usuario registrado correctamente"
                }), 201
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al registrar usuario: {str(e)}"
        }), 500

#API Actualizar usuario (PUT)
@app.route('/api/actualizar-usuario/<int:id_usuario>', methods=['PUT'])
def api_actualizar_usuario(id_usuario):
    if 'conectado' not in session:
        return jsonify({"success": False, "message": "Primero debes iniciar sesión"}), 401

    data = request.form

    campos_requeridos = ['name_surname', 'email_user']
    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({"success": False, "message": f"Falta el campo '{campo}'"}), 400

    name_surname = data['name_surname']
    email_user = data['email_user']
    nueva_clave = data.get('pass_user')  # opcional
    values = [name_surname, email_user]

    try:
        with connectionBD() as conn:
            with conn.cursor() as cursor:
                if nueva_clave:
                    hashed_pass = generate_password_hash(nueva_clave)
                    sql = """UPDATE users SET name_surname = %s, email_user = %s, pass_user = %s WHERE id = %s"""
                    values.append(hashed_pass)
                    values.append(id_usuario)
                else:
                    sql = """UPDATE users SET name_surname = %s, email_user = %s WHERE id = %s"""
                    values.append(id_usuario)

                cursor.execute(sql, tuple(values))
                conn.commit()

                if cursor.rowcount > 0:
                    return jsonify({"success": True, "message": "Usuario actualizado correctamente"}), 200
                else:
                    return jsonify({"success": False, "message": "Usuario no encontrado o sin cambios"}), 404

    except Exception as e:
        return jsonify({"success": False, "message": f"Error al actualizar usuario: {str(e)}"}), 500


@app.route("/descargar-informe-empleados/", methods=['GET'])
def reporteBD():
    if 'conectado' in session:
        return generarReporteExcel()
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
