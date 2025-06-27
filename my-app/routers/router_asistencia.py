from app import app
from flask import render_template, request, flash, redirect, url_for, session, jsonify
from datetime import datetime, date, timedelta
import os

# Importar funciones del controlador
from controllers.funciones_asistencia import *
from controllers.funciones_home import sql_detalles_empleadosBD  # Para obtener datos del empleado

PATH_URL = "templates/public/asistencia"

# ================================
# RUTAS PRINCIPALES
# ================================

@app.route('/asistencia', methods=['GET'])
def asistencia_home():
    """Página principal del módulo de asistencia"""
    if 'conectado' in session:
        # Obtener estadísticas del día
        asistencia_hoy = obtener_asistencia_hoy()
        
        return render_template(f'{PATH_URL}/asistencia_home.html', 
                             asistencia_hoy=asistencia_hoy)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/marcar-asistencia', methods=['GET'])
def marcar_asistencia_view():
    """Vista para marcar asistencia con cámara"""
    if 'conectado' in session:
        # Obtener lista de empleados para selección manual
        empleados = obtener_lista_empleados()
        return render_template(f'{PATH_URL}/marcar_asistencia.html', empleados=empleados)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/reportes-asistencia', methods=['GET'])
def reportes_asistencia():
    """Vista para reportes de asistencia"""
    if 'conectado' in session:
        return render_template(f'{PATH_URL}/reportes_asistencia.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/configuracion-asistencia', methods=['GET'])
def configuracion_asistencia():
    """Vista para configuración del sistema de asistencia"""
    if 'conectado' in session:
        return render_template(f'{PATH_URL}/configuracion_asistencia.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

# ================================
# APIs REST PARA ASISTENCIA
# ================================

@app.route('/api/marcar-asistencia', methods=['POST'])
def api_marcar_asistencia():
    """API para marcar asistencia (entrada/salida)"""
    if 'conectado' not in session:
        return jsonify({"success": False, "message": "Primero debes iniciar sesión"}), 401
    
    try:
        data = request.get_json()
        
        campos_requeridos = ['id_empleado', 'tipo_marcado']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({"success": False, "message": f"Falta el campo: {campo}"}), 400
        
        id_empleado = data['id_empleado']
        tipo_marcado = data['tipo_marcado']  # 'entrada' o 'salida'
        imagen = data.get('imagen')
        observaciones = data.get('observaciones')
        
        if tipo_marcado not in ['entrada', 'salida']:
            return jsonify({"success": False, "message": "Tipo de marcado inválido"}), 400
        
        resultado = marcar_asistencia_manual(id_empleado, tipo_marcado, imagen, observaciones)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al marcar asistencia: {str(e)}"}), 500

@app.route('/api/detectar-movimiento', methods=['POST'])
def api_detectar_movimiento():
    """API para detectar movimiento en imagen capturada"""
    if 'conectado' not in session:
        return jsonify({"success": False, "message": "Primero debes iniciar sesión"}), 401
    
    try:
        data = request.get_json()
        if not data or 'imagen' not in data:
            return jsonify({"success": False, "message": "No se envió la imagen"}), 400
        
        resultado = detectar_movimiento_basico(data['imagen'])
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 404
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Error en detección: {str(e)}"}), 500

# ================================
# APIs PARA REPORTES Y CONSULTAS
# ================================

@app.route('/api/asistencia-empleado/<int:id_empleado>', methods=['GET'])
def api_asistencia_empleado(id_empleado):
    """API para obtener asistencia de un empleado específico"""
    if 'conectado' not in session:
        return jsonify({"success": False, "message": "Primero debes iniciar sesión"}), 401
    
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        asistencia = obtener_asistencia_empleado(id_empleado, fecha_inicio, fecha_fin)
        
        return jsonify({
            "success": True,
            "data": asistencia,
            "total": len(asistencia)
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/reporte-asistencia-general', methods=['GET'])
def api_reporte_asistencia_general():
    """API para obtener reporte general de asistencia"""
    if 'conectado' not in session:
        return jsonify({"success": False, "message": "Primero debes iniciar sesión"}), 401
    
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({"success": False, "message": "Debe especificar fecha_inicio y fecha_fin"}), 400
        
        reporte = obtener_reporte_asistencia_general(fecha_inicio, fecha_fin)
        
        return jsonify({
            "success": True,
            "data": reporte,
            "total": len(reporte)
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/estadisticas-asistencia', methods=['GET'])
def api_estadisticas_asistencia():
    """API para obtener estadísticas de asistencia"""
    if 'conectado' not in session:
        return jsonify({"success": False, "message": "Primero debes iniciar sesión"}), 401
    
    try:
        id_empleado = request.args.get('id_empleado', type=int)
        mes = request.args.get('mes', type=int)
        año = request.args.get('año', type=int)
        
        estadisticas = obtener_estadisticas_asistencia(id_empleado, mes, año)
        
        return jsonify({
            "success": True,
            "data": estadisticas
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/asistencia-hoy', methods=['GET'])
def api_asistencia_hoy():
    """API para obtener asistencia del día actual"""
    if 'conectado' not in session:
        return jsonify({"success": False, "message": "Primero debes iniciar sesión"}), 401
    
    try:
        asistencia = obtener_asistencia_hoy()
        
        return jsonify({
            "success": True,
            "data": asistencia,
            "total": len(asistencia)
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/lista-empleados-asistencia', methods=['GET'])
def api_lista_empleados_asistencia():
    """API para obtener lista de empleados para asistencia"""
    if 'conectado' not in session:
        return jsonify({"success": False, "message": "Primero debes iniciar sesión"}), 401
    
    try:
        empleados = obtener_lista_empleados()
        
        return jsonify({
            "success": True,
            "data": empleados,
            "total": len(empleados)
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

# ================================
# RUTAS PARA VISTAS CON DATOS
# ================================

@app.route('/detalle-asistencia-empleado/<int:id_empleado>', methods=['GET'])
def detalle_asistencia_empleado(id_empleado):
    """Vista detallada de asistencia de un empleado"""
    if 'conectado' in session:
        # Obtener datos del empleado
        empleado = sql_detalles_empleadosBD(id_empleado)
        if not empleado:
            flash('Empleado no encontrado.', 'error')
            return redirect(url_for('asistencia_home'))
        
        # Obtener asistencia del mes actual
        hoy = date.today()
        inicio_mes = hoy.replace(day=1)
        asistencia = obtener_asistencia_empleado(id_empleado, inicio_mes, hoy)
        estadisticas = obtener_estadisticas_asistencia(id_empleado)
        
        return render_template(f'{PATH_URL}/detalle_asistencia_empleado.html',
                             empleado=empleado[0],  # sql_detalles_empleadosBD retorna lista
                             asistencia=asistencia,
                             estadisticas=estadisticas)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

# ================================
# APIs PARA CONFIGURACIÓN
# ================================

@app.route('/api/configuracion-asistencia', methods=['GET'])
def api_obtener_configuracion():
    """API para obtener configuración del sistema"""
    if 'conectado' not in session:
        return jsonify({"success": False, "message": "Primero debes iniciar sesión"}), 401
    
    try:
        with connectionBD() as conexion:
            with conexion.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM tbl_configuracion_asistencia ORDER BY parametro")
                configuraciones = cursor.fetchall()
                
                return jsonify({
                    "success": True,
                    "data": configuraciones
                }), 200
                
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/configuracion-asistencia', methods=['POST'])
def api_actualizar_configuracion():
    """API para actualizar configuración del sistema"""
    if 'conectado' not in session:
        return jsonify({"success": False, "message": "Primero debes iniciar sesión"}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No se enviaron datos"}), 400
        
        with connectionBD() as conexion:
            with conexion.cursor() as cursor:
                for parametro, valor in data.items():
                    cursor.execute("""
                        UPDATE tbl_configuracion_asistencia 
                        SET valor = %s 
                        WHERE parametro = %s
                    """, (valor, parametro))
                
                conexion.commit()
                
                return jsonify({
                    "success": True,
                    "message": "Configuración actualizada correctamente"
                }), 200
                
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

# ================================
# FUNCIONES DE UTILIDAD
# ================================

@app.route('/api/test-camara', methods=['POST'])
def api_test_camara():
    """API para probar que la cámara funciona correctamente"""
    if 'conectado' not in session:
        return jsonify({"success": False, "message": "Primero debes iniciar sesión"}), 401
    
    try:
        data = request.get_json()
        if not data or 'imagen' not in data:
            return jsonify({"success": False, "message": "No se envió la imagen"}), 400
        
        # Probar procesamiento básico
        resultado_movimiento = detectar_movimiento_basico(data['imagen'])
        
        return jsonify({
            "success": True,
            "message": "Cámara funcionando correctamente",
            "deteccion": resultado_movimiento
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al probar cámara: {str(e)}"}), 500

# ================================
# MANEJO DE ERRORES ESPECÍFICOS
# ================================

@app.errorhandler(413)
def archivo_muy_grande(error):
    """Maneja errores de archivos muy grandes"""
    return jsonify({"success": False, "message": "El archivo es muy grande"}), 413