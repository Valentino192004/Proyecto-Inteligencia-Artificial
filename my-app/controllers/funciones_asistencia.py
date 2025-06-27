import os
import cv2
import numpy as np
import base64
import json
from datetime import datetime, date, time, timedelta
from PIL import Image
import io
from werkzeug.utils import secure_filename
import re

# Importar conexión a BD
from conexion.conexionBD import connectionBD

def procesar_imagen_capturada(imagen_base64, id_empleado, tipo_marcado):
    """
    Procesa la imagen capturada desde la webcam para marcar asistencia
    Por ahora sin reconocimiento facial, solo guarda la imagen
    """
    try:
        # Guardar foto si está habilitado
        foto_path = None
        if imagen_base64 and obtener_configuracion('guardar_fotos_asistencia', '1') == '1':
            foto_path = guardar_foto_asistencia(imagen_base64, id_empleado, tipo_marcado)
        
        return {
            "success": True, 
            "message": "Imagen procesada correctamente",
            "foto_path": foto_path
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error al procesar imagen: {str(e)}"}

def detectar_movimiento_basico(imagen_base64):
    """
    Detecta si hay movimiento/presencia en la imagen usando OpenCV
    Funcionalidad básica antes de agregar reconocimiento facial
    """
    try:
        # Decodificar imagen base64
        header, encoded = imagen_base64.split(',', 1)
        imagen_data = base64.b64decode(encoded)
        imagen = Image.open(io.BytesIO(imagen_data))
        
        # Convertir PIL a numpy array
        imagen_np = np.array(imagen)
        
        # Convertir a escala de grises
        if len(imagen_np.shape) == 3:
            gray = cv2.cvtColor(imagen_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = imagen_np
        
        # Detectar contornos (movimiento básico)
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Si hay contornos significativos, hay movimiento
        movimiento_detectado = len(contours) > 10
        
        return {
            "success": True,
            "movimiento_detectado": movimiento_detectado,
            "contornos_detectados": len(contours)
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error en detección: {str(e)}"}

def marcar_asistencia_manual(id_empleado, tipo_marcado, imagen_base64=None, observaciones=None):
    """
    Marca la asistencia de un empleado (entrada o salida) - Versión manual por ahora
    """
    try:
        fecha_actual = date.today()
        hora_actual = datetime.now().time()
        
        # Procesar imagen si se proporciona
        foto_path = None
        if imagen_base64:
            resultado_imagen = procesar_imagen_capturada(imagen_base64, id_empleado, tipo_marcado)
            if resultado_imagen['success']:
                foto_path = resultado_imagen['foto_path']
        
        with connectionBD() as conexion:
            with conexion.cursor(dictionary=True) as cursor:
                # Verificar si ya existe registro para hoy
                cursor.execute(
                    "SELECT * FROM tbl_asistencia WHERE id_empleado = %s AND fecha = %s",
                    (id_empleado, fecha_actual)
                )
                registro_existente = cursor.fetchone()
                
                if tipo_marcado == 'entrada':
                    if registro_existente:
                        if registro_existente['hora_entrada']:
                            return {"success": False, "message": "Ya se registró la entrada para hoy"}
                        else:
                            # Actualizar entrada
                            cursor.execute("""
                                UPDATE tbl_asistencia 
                                SET hora_entrada = %s, foto_entrada = %s, observaciones = %s,
                                    estado = %s, metodo_registro = 'manual'
                                WHERE id_empleado = %s AND fecha = %s
                            """, (hora_actual, foto_path, observaciones, 
                                 calcular_estado_entrada(hora_actual), id_empleado, fecha_actual))
                    else:
                        # Crear nuevo registro
                        cursor.execute("""
                            INSERT INTO tbl_asistencia 
                            (id_empleado, fecha, hora_entrada, foto_entrada, observaciones, estado, metodo_registro)
                            VALUES (%s, %s, %s, %s, %s, %s, 'manual')
                        """, (id_empleado, fecha_actual, hora_actual, foto_path, observaciones,
                             calcular_estado_entrada(hora_actual)))
                
                elif tipo_marcado == 'salida':
                    if not registro_existente:
                        return {"success": False, "message": "Debe marcar entrada antes de la salida"}
                    
                    if registro_existente['hora_salida']:
                        return {"success": False, "message": "Ya se registró la salida para hoy"}
                    
                    # Actualizar salida
                    nuevo_estado = calcular_estado_salida(registro_existente['hora_entrada'], hora_actual)
                    cursor.execute("""
                        UPDATE tbl_asistencia 
                        SET hora_salida = %s, foto_salida = %s, estado = %s
                        WHERE id_empleado = %s AND fecha = %s
                    """, (hora_actual, foto_path, nuevo_estado, id_empleado, fecha_actual))
                
                conexion.commit()
                
                return {
                    "success": True, 
                    "message": f"Asistencia de {tipo_marcado} registrada correctamente",
                    "hora": hora_actual.strftime("%H:%M:%S"),
                    "fecha": fecha_actual.strftime("%Y-%m-%d")
                }
                
    except Exception as e:
        return {"success": False, "message": f"Error al marcar asistencia: {str(e)}"}

def guardar_foto_asistencia(imagen_base64, id_empleado, tipo_marcado):
    """
    Guarda la foto de asistencia en el sistema de archivos
    """
    try:
        # Crear directorio si no existe
        directorio = f"static/fotos_asistencia/{date.today().strftime('%Y-%m')}"
        os.makedirs(directorio, exist_ok=True)
        
        # Generar nombre de archivo único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"empleado_{id_empleado}_{tipo_marcado}_{timestamp}.jpg"
        ruta_completa = os.path.join(directorio, nombre_archivo)
        
        # Decodificar y guardar imagen
        header, encoded = imagen_base64.split(',', 1)
        imagen_data = base64.b64decode(encoded)
        
        with open(ruta_completa, 'wb') as f:
            f.write(imagen_data)
        
        return ruta_completa
        
    except Exception as e:
        print(f"Error al guardar foto: {str(e)}")
        return None

def calcular_estado_entrada(hora_entrada):
    """
    Calcula el estado basado en la hora de entrada
    """
    hora_oficial = obtener_configuracion('hora_entrada', '08:00:00')
    tolerancia_min = int(obtener_configuracion('tolerancia_entrada', '15'))
    
    # Convertir a objetos time para comparar
    hora_oficial_obj = datetime.strptime(hora_oficial, '%H:%M:%S').time()
    hora_limite = (datetime.combine(date.today(), hora_oficial_obj) + 
                   timedelta(minutes=tolerancia_min)).time()
    
    if hora_entrada <= hora_oficial_obj:
        return 'presente'
    elif hora_entrada <= hora_limite:
        return 'presente'  # Dentro de tolerancia
    else:
        return 'tardanza'

def calcular_estado_salida(hora_entrada, hora_salida):
    """
    Calcula el estado final basado en entrada y salida
    """
    if not hora_entrada:
        return 'ausente'
    
    hora_oficial_salida = obtener_configuracion('hora_salida', '17:00:00')
    hora_oficial_salida_obj = datetime.strptime(hora_oficial_salida, '%H:%M:%S').time()
    
    if hora_salida < hora_oficial_salida_obj:
        return 'salida_temprana'
    else:
        return 'presente'

def obtener_configuracion(parametro, valor_defecto):
    """
    Obtiene un valor de configuración de la base de datos
    """
    try:
        with connectionBD() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT valor FROM tbl_configuracion_asistencia WHERE parametro = %s",
                    (parametro,)
                )
                resultado = cursor.fetchone()
                return resultado[0] if resultado else valor_defecto
    except:
        return valor_defecto

def obtener_asistencia_empleado(id_empleado, fecha_inicio=None, fecha_fin=None):
    """
    Obtiene los registros de asistencia de un empleado
    """
    try:
        with connectionBD() as conexion:
            with conexion.cursor(dictionary=True) as cursor:
                sql = """
                    SELECT a.*, e.nombre_empleado, e.apellido_empleado, e.foto_empleado, e.profesion_empleado,
                           CONCAT(e.nombre_empleado, ' ', e.apellido_empleado) as nombre_completo
                    FROM tbl_asistencia a
                    INNER JOIN tbl_empleados e ON a.id_empleado = e.id_empleado
                    WHERE a.id_empleado = %s
                """
                params = [id_empleado]
                
                if fecha_inicio and fecha_fin:
                    sql += " AND a.fecha BETWEEN %s AND %s"
                    params.extend([fecha_inicio, fecha_fin])
                elif fecha_inicio:
                    sql += " AND a.fecha >= %s"
                    params.append(fecha_inicio)
                elif fecha_fin:
                    sql += " AND a.fecha <= %s"
                    params.append(fecha_fin)
                
                sql += " ORDER BY a.fecha DESC"
                
                cursor.execute(sql, params)
                return cursor.fetchall()
                
    except Exception as e:
        print(f"Error al obtener asistencia: {str(e)}")
        return []

def obtener_reporte_asistencia_general(fecha_inicio, fecha_fin):
    """
    Obtiene reporte general de asistencia
    """
    try:
        with connectionBD() as conexion:
            with conexion.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT a.*, e.nombre_empleado, e.apellido_empleado, e.foto_empleado, e.profesion_empleado,
                           CONCAT(e.nombre_empleado, ' ', e.apellido_empleado) as nombre_completo,
                           CASE 
                               WHEN a.hora_entrada IS NULL THEN 'Sin entrada'
                               WHEN a.hora_entrada <= %s THEN 'Puntual'
                               ELSE 'Tardanza'
                           END as status_entrada,
                           CASE 
                               WHEN a.hora_salida IS NULL THEN 'Sin salida'
                               WHEN a.hora_salida >= %s THEN 'Completa'
                               ELSE 'Salida temprana'
                           END as status_salida,
                           CASE 
                               WHEN a.hora_entrada IS NOT NULL AND a.hora_salida IS NOT NULL 
                               THEN TIMEDIFF(a.hora_salida, a.hora_entrada)
                               ELSE NULL
                           END as horas_trabajadas
                    FROM tbl_asistencia a
                    INNER JOIN tbl_empleados e ON a.id_empleado = e.id_empleado
                    WHERE a.fecha BETWEEN %s AND %s
                    ORDER BY a.fecha DESC, a.hora_entrada DESC
                """, (
                    obtener_configuracion('hora_entrada', '08:00:00'),
                    obtener_configuracion('hora_salida', '17:00:00'),
                    fecha_inicio, 
                    fecha_fin
                ))
                return cursor.fetchall()
                
    except Exception as e:
        print(f"Error al obtener reporte: {str(e)}")
        return []

def obtener_estadisticas_asistencia(id_empleado=None, mes=None, año=None):
    """
    Obtiene estadísticas de asistencia
    """
    try:
        with connectionBD() as conexion:
            with conexion.cursor(dictionary=True) as cursor:
                
                if mes and año:
                    fecha_inicio = f"{año}-{mes:02d}-01"
                    if mes == 12:
                        fecha_fin = f"{año + 1}-01-01"
                    else:
                        fecha_fin = f"{año}-{mes + 1:02d}-01"
                else:
                    # Mes actual
                    hoy = date.today()
                    fecha_inicio = hoy.replace(day=1)
                    siguiente_mes = (hoy.replace(day=28) + timedelta(days=4)).replace(day=1)
                    fecha_fin = siguiente_mes
                
                sql = """
                    SELECT 
                        COUNT(*) as total_dias,
                        SUM(CASE WHEN estado = 'presente' THEN 1 ELSE 0 END) as dias_presente,
                        SUM(CASE WHEN estado = 'tardanza' THEN 1 ELSE 0 END) as dias_tardanza,
                        SUM(CASE WHEN estado = 'ausente' THEN 1 ELSE 0 END) as dias_ausente,
                        SUM(CASE WHEN estado = 'salida_temprana' THEN 1 ELSE 0 END) as salidas_tempranas,
                        AVG(CASE WHEN hora_entrada IS NOT NULL AND hora_salida IS NOT NULL 
                            THEN TIME_TO_SEC(TIMEDIFF(hora_salida, hora_entrada))/3600 ELSE NULL END) as promedio_horas
                    FROM tbl_asistencia 
                    WHERE fecha >= %s AND fecha < %s
                """
                
                params = [fecha_inicio, fecha_fin]
                
                if id_empleado:
                    sql += " AND id_empleado = %s"
                    params.append(id_empleado)
                
                cursor.execute(sql, params)
                return cursor.fetchone()
                
    except Exception as e:
        print(f"Error al obtener estadísticas: {str(e)}")
        return {}

def obtener_asistencia_hoy():
    """
    Obtiene la asistencia del día actual
    """
    try:
        fecha_hoy = date.today()
        with connectionBD() as conexion:
            with conexion.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT a.*, e.nombre_empleado, e.apellido_empleado, e.foto_empleado, e.profesion_empleado,
                           CONCAT(e.nombre_empleado, ' ', e.apellido_empleado) as nombre_completo,
                           CASE 
                               WHEN a.hora_entrada IS NOT NULL AND a.hora_salida IS NOT NULL 
                               THEN TIMEDIFF(a.hora_salida, a.hora_entrada)
                               ELSE NULL
                           END as horas_trabajadas
                    FROM tbl_asistencia a
                    INNER JOIN tbl_empleados e ON a.id_empleado = e.id_empleado
                    WHERE a.fecha = %s
                    ORDER BY a.hora_entrada DESC
                """, (fecha_hoy,))
                return cursor.fetchall()
                
    except Exception as e:
        print(f"Error al obtener asistencia de hoy: {str(e)}")
        return []

def obtener_lista_empleados():
    """
    Obtiene lista de todos los empleados para selección manual
    """
    try:
        with connectionBD() as conexion:
            with conexion.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT id_empleado, nombre_empleado, apellido_empleado, foto_empleado, profesion_empleado,
                           CONCAT(nombre_empleado, ' ', apellido_empleado) as nombre_completo
                    FROM tbl_empleados
                    ORDER BY nombre_empleado, apellido_empleado
                """)
                return cursor.fetchall()
                
    except Exception as e:
        print(f"Error al obtener empleados: {str(e)}")
        return []