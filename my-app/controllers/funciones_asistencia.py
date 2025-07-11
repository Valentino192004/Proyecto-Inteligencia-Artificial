"""
Controlador para el manejo de funciones de asistencia
Compatible con el sistema existente - Versión actualizada
"""

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
import random

# Importar conexión a BD
from conexion.conexionBD import connectionBD

# ================================
# FUNCIONES DE ASISTENCIA
# ================================

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

# ================================
# FUNCIONES DE PROCESAMIENTO DE IMÁGENES
# ================================

def procesar_imagen_capturada(imagen_base64, id_empleado, tipo_marcado):
    """
    Procesa la imagen capturada desde la webcam para marcar asistencia
    Por ahora sin reconocimiento facial, solo guarda la imagen
    """
    try:
        # Guardar foto si está habilitado
        foto_path = None
        if imagen_base64 and obtener_configuracion('requiere_foto', 'true') == 'true':
            foto_path = guardar_foto_asistencia(imagen_base64, id_empleado, tipo_marcado)
        
        return {
            "success": True, 
            "message": "Imagen procesada correctamente",
            "foto_path": foto_path
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error al procesar imagen: {str(e)}"}

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
        if 'data:image' in imagen_base64:
            header, encoded = imagen_base64.split(',', 1)
        else:
            encoded = imagen_base64
            
        imagen_data = base64.b64decode(encoded)
        
        with open(ruta_completa, 'wb') as f:
            f.write(imagen_data)
        
        return ruta_completa
        
    except Exception as e:
        print(f"Error al guardar foto: {str(e)}")
        return None

def obtener_asistencia_hoy():
    try:
        fecha_hoy = date.today()
        
        with connectionBD() as conexion:
            with conexion.cursor(dictionary=True) as cursor:
                querySQL = """
                    SELECT 
                        a.id_empleado, a.estado,
                        TIME_FORMAT(a.hora_entrada, '%H:%i:%s') as hora_entrada,
                        TIME_FORMAT(a.hora_salida, '%H:%i:%s') as hora_salida,
                        e.foto_empleado, e.profesion_empleado,
                        CONCAT(e.nombre_empleado, ' ', e.apellido_empleado) as nombre_completo,
                        CASE 
                            WHEN a.hora_entrada IS NOT NULL AND a.hora_salida IS NOT NULL
                            THEN TIME_FORMAT(TIMEDIFF(a.hora_salida, a.hora_entrada), '%H:%i:%s')
                            ELSE NULL
                        END as horas_trabajadas
                    FROM tbl_asistencia a
                    INNER JOIN tbl_empleados e ON a.id_empleado = e.id_empleado
                    WHERE a.fecha_asistencia = %(fecha)s
                    ORDER BY a.hora_entrada DESC
                """
                
                cursor.execute(querySQL, {'fecha': fecha_hoy})
                asistencias = cursor.fetchall()
                return asistencias
                
    except Exception as e:
        print(f"Error al obtener asistencia de hoy: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def marcar_asistencia_manual(id_empleado, tipo_marcado, imagen_base64=None, observaciones=None):
    """
    Marca la asistencia de un empleado (entrada o salida) - Compatible con sistema existente
    """
    try:
        fecha_actual = date.today()
        hora_actual = datetime.now().time()
        
        print(f"🕐 Marcando asistencia: {tipo_marcado} para empleado {id_empleado}")
        print(f"📅 Fecha actual: {fecha_actual} ({obtener_nombre_dia_español(fecha_actual)})")
        print(f"⏰ Hora actual: {hora_actual}")
        
        # Verificar horario laboral 
        permitir_fuera_horario = obtener_configuracion('permitir_marcado_fuera_horario', 'false') == 'true'
        validar_dias = obtener_configuracion('validar_dias_laborables', 'true') == 'true'
        
        # Validar días laborables
        if validar_dias and not es_dia_laborable(fecha_actual):
            dias_permitidos = obtener_nombres_dias_laborables()
            nombre_dia_actual = obtener_nombre_dia_español(fecha_actual)
            return {
                "success": False, 
                "message": f"Hoy es {nombre_dia_actual} y no es un día laborable. Los días laborables son: {dias_permitidos}."
            }
        
        # Validar horario laboral
        if not permitir_fuera_horario:
            if not validar_horario_trabajo(hora_actual):
                return {
                    "success": False,
                    "message": f"Fuera del horario laboral. Hora actual: {hora_actual.strftime('%H:%M')}. Horario permitido: 9:00 AM a 7:00 PM"
                }
        
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
                    "SELECT * FROM tbl_asistencia WHERE id_empleado = %s AND fecha_asistencia = %s",
                    (id_empleado, fecha_actual)
                )
                registro_existente = cursor.fetchone()
                
                if tipo_marcado == 'entrada':
                    if registro_existente:
                        if registro_existente['hora_entrada']:
                            return {"success": False, "message": "Ya se registró la entrada para hoy"}
                        else:
                            # Actualizar entrada
                            estado = calcular_estado_entrada(hora_actual)
                            print(f"📝 Actualizando entrada. Estado calculado: {estado}")
                            
                            cursor.execute("""
                                UPDATE tbl_asistencia 
                                SET hora_entrada = %s, imagen_entrada = %s, observaciones = %s,
                                    estado = %s
                                WHERE id_empleado = %s AND fecha_asistencia = %s
                            """, (hora_actual, foto_path, observaciones, 
                                 estado, id_empleado, fecha_actual))
                    else:
                        # Crear nuevo registro
                        estado = calcular_estado_entrada(hora_actual)
                        print(f"📝 Creando nuevo registro de entrada. Estado calculado: {estado}")
                        
                        cursor.execute("""
                            INSERT INTO tbl_asistencia 
                            (id_empleado, fecha_asistencia, hora_entrada, imagen_entrada, observaciones, estado, tipo_marcado)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (id_empleado, fecha_actual, hora_actual, foto_path, observaciones,
                             estado, tipo_marcado))
                
                elif tipo_marcado == 'salida':
                    if not registro_existente:
                        return {"success": False, "message": "Debe marcar entrada antes de la salida"}
                    
                    if registro_existente['hora_salida']:
                        return {"success": False, "message": "Ya se registró la salida para hoy"}
                    
                    # Actualizar salida
                    nuevo_estado = calcular_estado_salida(registro_existente['hora_entrada'], hora_actual)
                    print(f"📝 Actualizando salida. Estado calculado: {nuevo_estado}")
                    
                    cursor.execute("""
                        UPDATE tbl_asistencia 
                        SET hora_salida = %s, imagen_salida = %s, estado = %s
                        WHERE id_empleado = %s AND fecha_asistencia = %s
                    """, (hora_actual, foto_path, nuevo_estado, id_empleado, fecha_actual))
                
                conexion.commit()
                print(f"✅ Asistencia de {tipo_marcado} guardada exitosamente")
                
                return {
                    "success": True, 
                    "message": f"Asistencia de {tipo_marcado} registrada correctamente",
                    "hora": hora_actual.strftime("%H:%M:%S"),
                    "fecha": fecha_actual.strftime("%Y-%m-%d")
                }
                
    except Exception as e:
        print(f"❌ Error al marcar asistencia: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "message": f"Error al marcar asistencia: {str(e)}"}

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
                    sql += " AND a.fecha_asistencia BETWEEN %s AND %s"
                    params.extend([fecha_inicio, fecha_fin])
                elif fecha_inicio:
                    sql += " AND a.fecha_asistencia >= %s"
                    params.append(fecha_inicio)
                elif fecha_fin:
                    sql += " AND a.fecha_asistencia <= %s"
                    params.append(fecha_fin)
                
                sql += " ORDER BY a.fecha_asistencia DESC"
                
                cursor.execute(sql, params)
                return cursor.fetchall()
                
    except Exception as e:
        print(f"Error al obtener asistencia: {str(e)}")
        return []

def obtener_reporte_asistencia_general(fecha_inicio, fecha_fin, id_empleado=None):
    """
    Obtiene reporte general de asistencia con filtros de fecha y empleado.
    """
    try:
        # Convertir la fecha final a datetime y sumar un día para incluir todo el día.
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1)
        fecha_fin_ajustada = fecha_fin_dt.strftime('%Y-%m-%d')

        with connectionBD() as conexion:
            with conexion.cursor(dictionary=True) as cursor:
                # Se quita TIME_FORMAT de la consulta para formatear en Python.
                # Esto es más robusto y evita problemas de formato.
                query = """
                    SELECT 
                        a.id_asistencia,
                        a.id_empleado,
                        a.fecha_asistencia as fecha,
                        a.hora_entrada,
                        a.hora_salida,
                        a.estado,
                        a.observaciones,
                        e.foto_empleado,
                        e.profesion_empleado,
                        CONCAT(e.nombre_empleado, ' ', e.apellido_empleado) as nombre_completo,
                        TIMEDIFF(a.hora_salida, a.hora_entrada) as horas_trabajadas
                    FROM tbl_asistencia a
                    INNER JOIN tbl_empleados e ON a.id_empleado = e.id_empleado
                    WHERE a.fecha_asistencia >= %s AND a.fecha_asistencia < %s
                """
                params = [fecha_inicio, fecha_fin_ajustada]

                # Añadir filtro de empleado si se proporciona
                if id_empleado and id_empleado.isdigit():
                    query += " AND a.id_empleado = %s"
                    params.append(int(id_empleado))

                query += " ORDER BY a.fecha_asistencia DESC, a.hora_entrada DESC"
                cursor.execute(query, tuple(params))
                reporte = cursor.fetchall()

                # Formatear fechas y horas en Python para evitar errores de JSON y formato
                for row in reporte:
                    # Formatear fecha
                    if isinstance(row.get('fecha'), date):
                        row['fecha'] = row['fecha'].strftime('%Y-%m-%d')
                    
                    # Formatear horas (que la BD devuelve como objetos timedelta)
                    for key in ['hora_entrada', 'hora_salida', 'horas_trabajadas']:
                        if isinstance(row.get(key), timedelta):
                            total_seconds = row[key].total_seconds()
                            # abs() para manejar TIMEDIFF negativos si ocurrieran
                            hours, remainder = divmod(abs(total_seconds), 3600)
                            minutes, _ = divmod(remainder, 60)
                            row[key] = f"{int(hours):02}:{int(minutes):02}"
                
                return reporte
                
    except Exception as e:
        print(f"Error al obtener reporte general: {str(e)}")
        import traceback
        traceback.print_exc()
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
                        SUM(CASE WHEN estado = 'tarde' THEN 1 ELSE 0 END) as dias_tardanza,
                        SUM(CASE WHEN estado = 'ausente' THEN 1 ELSE 0 END) as dias_ausente,
                        SUM(CASE WHEN estado = 'temprano' THEN 1 ELSE 0 END) as salidas_tempranas,
                        AVG(CASE WHEN hora_entrada IS NOT NULL AND hora_salida IS NOT NULL 
                            THEN TIME_TO_SEC(TIMEDIFF(hora_salida, hora_entrada))/3600 ELSE NULL END) as promedio_horas
                    FROM tbl_asistencia 
                    WHERE fecha_asistencia >= %s AND fecha_asistencia < %s
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

# ================================
# FUNCIONES DE DETECCIÓN
# ================================

def detectar_movimiento_basico(imagen_base64):
    """Detecta movimiento básico en imagen (simulación)"""
    try:
        # Decodificar imagen base64
        if 'data:image' in imagen_base64:
            imagen_base64 = imagen_base64.split(',')[1]
        
        img_data = base64.b64decode(imagen_base64)
        img = Image.open(io.BytesIO(img_data))
        
        # Convertir a numpy array
        img_array = np.array(img)
        
        # Simulación básica de detección
        # En una implementación real, aquí irían algoritmos de CV
        altura, ancho = img_array.shape[:2]
        
        # Detectar si hay suficiente contraste (simulación)
        gris = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY) if len(img_array.shape) == 3 else img_array
        contraste = np.std(gris)
        
        if contraste > 30:  # Umbral básico
            return {
                "success": True,
                "movimiento_detectado": True,
                "confianza": min(contraste / 100, 1.0),
                "mensaje": "Movimiento detectado"
            }
        else:
            return {
                "success": False,
                "movimiento_detectado": False,
                "confianza": 0.0,
                "mensaje": "No se detectó movimiento suficiente"
            }
            
    except Exception as e:
        print(f"Error en detección de movimiento: {e}")
        return {
            "success": False,
            "movimiento_detectado": False,
            "confianza": 0.0,
            "mensaje": f"Error en detección: {str(e)}"
        }

# ================================
# FUNCIONES DE UTILIDAD Y VALIDACIÓN
# ================================

def obtener_nombre_dia_español(fecha):
    """Obtiene el nombre del día en español"""
    nombres_dias = {
        0: 'Lunes',
        1: 'Martes',
        2: 'Miércoles', 
        3: 'Jueves',
        4: 'Viernes',
        5: 'Sábado',
        6: 'Domingo'
    }
    
    dia_semana = fecha.weekday()  # 0=Lunes, 6=Domingo
    return nombres_dias.get(dia_semana, 'Día desconocido')

def obtener_nombres_dias_laborables():
    """Obtiene los nombres de los días laborables configurados"""
    try:
        dias_laborables = obtener_configuracion('dias_laborables', '1,2,3,4,5,6')
        dias_lista = [int(d.strip()) for d in dias_laborables.split(',')]
        
        # Mapeo de números a nombres de días
        nombres_dias = {
            1: 'Lunes',
            2: 'Martes', 
            3: 'Miércoles',
            4: 'Jueves',
            5: 'Viernes',
            6: 'Sábado',
            7: 'Domingo'
        }
        
        # Obtener nombres de los días configurados
        nombres = [nombres_dias[dia] for dia in dias_lista if dia in nombres_dias]
        
        # Formatear la lista
        if len(nombres) == 1:
            return nombres[0]
        elif len(nombres) == 2:
            return f"{nombres[0]} y {nombres[1]}"
        else:
            return f"{', '.join(nombres[:-1])} y {nombres[-1]}"
            
    except Exception as e:
        print(f"Error obteniendo nombres de días: {e}")
        return "Lunes a Sábado"

def obtener_horarios_sistema():
    """Obtiene todos los horarios configurados del sistema"""
    try:
        return {
            'hora_entrada_inicio': obtener_configuracion('hora_entrada_inicio', '09:00:00'),
            'hora_entrada_fin': obtener_configuracion('hora_entrada_fin', '19:00:00'),
            'hora_salida_inicio': obtener_configuracion('hora_salida_inicio', '09:00:00'),
            'hora_salida_fin': obtener_configuracion('hora_salida_fin', '19:00:00'),
            'tolerancia_minutos': int(obtener_configuracion('tolerancia_minutos', '15'))
        }
    except Exception as e:
        print(f"Error al obtener horarios: {e}")
        return {
            'hora_entrada_inicio': '09:00:00',
            'hora_entrada_fin': '19:00:00',
            'hora_salida_inicio': '09:00:00',
            'hora_salida_fin': '19:00:00',
            'tolerancia_minutos': 15
        }

# ================================
# FUNCIONES DE CONFIGURACIÓN Y VALIDACIÓN
# ================================

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
                valor = resultado[0] if resultado else valor_defecto
                
                # Normalizar valores de tiempo para incluir segundos
                if parametro.startswith('hora_') and valor and ':' in valor:
                    if len(valor.split(':')) == 2:
                        valor += ':00'
                
                return valor
    except Exception as e:
        print(f"Error obteniendo configuración para {parametro}: {e}")
        return valor_defecto

def calcular_estado_entrada(hora_entrada):
    """
    Calcula el estado basado en la hora de entrada
    """
    try:
        hora_oficial = obtener_configuracion('hora_entrada_inicio', '08:00:00')
        tolerancia_min = int(obtener_configuracion('tolerancia_minutos', '15'))
        
        # Normalizar formato de hora oficial (agregar segundos si no los tiene)
        if len(hora_oficial.split(':')) == 2:
            hora_oficial += ':00'
        
        # Convertir a objetos time para comparar
        hora_oficial_obj = datetime.strptime(hora_oficial, '%H:%M:%S').time()
        hora_limite = (datetime.combine(date.today(), hora_oficial_obj) + 
                       timedelta(minutes=tolerancia_min)).time()
        
        # Si hora_entrada es string, convertirla a time object
        if isinstance(hora_entrada, str):
            # Agregar segundos si no los tiene
            if len(hora_entrada.split(':')) == 2:
                hora_entrada += ':00'
            hora_entrada = datetime.strptime(hora_entrada, '%H:%M:%S').time()
        
        if hora_entrada <= hora_oficial_obj:
            return 'presente'
        elif hora_entrada <= hora_limite:
            return 'presente'  # Dentro de tolerancia
        else:
            return 'tarde'
            
    except Exception as e:
        print(f"Error calculando estado entrada: {e}")
        return 'presente'  # Por defecto

def calcular_estado_salida(hora_entrada, hora_salida):
    """
    Calcula el estado final basado en entrada y salida
    """
    try:
        if not hora_entrada:
            return 'ausente'
        
        hora_oficial_salida = obtener_configuracion('hora_salida_inicio', '17:00:00')
        
        # Normalizar formato de hora oficial
        if len(hora_oficial_salida.split(':')) == 2:
            hora_oficial_salida += ':00'
            
        hora_oficial_salida_obj = datetime.strptime(hora_oficial_salida, '%H:%M:%S').time()
        
        # Si hora_salida es string, convertirla a time object
        if isinstance(hora_salida, str):
            if len(hora_salida.split(':')) == 2:
                hora_salida += ':00'
            hora_salida = datetime.strptime(hora_salida, '%H:%M:%S').time()
        
        if hora_salida < hora_oficial_salida_obj:
            return 'temprano'
        else:
            return 'presente'
            
    except Exception as e:
        print(f"Error calculando estado salida: {e}")
        return 'presente'  # Por defecto

def obtener_configuracion_asistencia():
    """Obtiene toda la configuración del sistema"""
    try:
        with connectionBD() as conexion:
            with conexion.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT parametro, valor, descripcion, tipo_dato
                    FROM tbl_configuracion_asistencia
                    ORDER BY parametro
                """)
                configuraciones = cursor.fetchall()
                
                # Convertir a diccionario para fácil acceso
                config_dict = {}
                for config in configuraciones:
                    config_dict[config['parametro']] = config['valor']
                
                return config_dict
    except Exception as e:
        print(f"Error al obtener configuración: {e}")
        return {}

def actualizar_configuracion_asistencia(parametro, valor):
    """Actualiza un parámetro de configuración"""
    try:
        with connectionBD() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    UPDATE tbl_configuracion_asistencia 
                    SET valor = %s 
                    WHERE parametro = %s
                """, (valor, parametro))
                conexion.commit()
                return True
    except Exception as e:
        print(f"Error al actualizar configuración: {e}")
        return False

# ================================
# FUNCIONES DE VALIDACIÓN
# ================================

def validar_horario_trabajo(hora_actual, configuracion=None):
    """Valida si la hora actual está dentro del horario laboral: 9 AM a 7 PM"""
    try:
        if not configuracion:
            configuracion = obtener_configuracion_asistencia()
        
        # Obtener horarios configurados
        hora_inicio = configuracion.get('hora_entrada_inicio', '09:00:00')  # 9 AM
        hora_fin = configuracion.get('hora_entrada_fin', '19:00:00')        # 7 PM
        
        # Normalizar formatos (agregar segundos si faltan)
        if len(hora_inicio.split(':')) == 2:
            hora_inicio += ':00'
        if len(hora_fin.split(':')) == 2:
            hora_fin += ':00'
        
        # Convertir strings a objetos time
        inicio = datetime.strptime(hora_inicio, '%H:%M:%S').time()
        fin = datetime.strptime(hora_fin, '%H:%M:%S').time()
        
        # Si hora_actual es string, convertirla
        if isinstance(hora_actual, str):
            if len(hora_actual.split(':')) == 2:
                hora_actual += ':00'
            hora_actual = datetime.strptime(hora_actual, '%H:%M:%S').time()
        
        # Verificar si está en el rango de 9 AM a 7 PM
        en_horario_laboral = inicio <= hora_actual <= fin
        
        print(f"⏰ Validando horario laboral:")
        print(f"   - Hora actual: {hora_actual}")
        print(f"   - Horario laboral: {inicio} a {fin}")
        print(f"   - En horario válido: {en_horario_laboral}")
        
        return en_horario_laboral
        
    except Exception as e:
        print(f"Error al validar horario: {e}")
        return False  # Si hay error, no permitir

def es_dia_laborable(fecha_actual, configuracion=None):
    """Verifica si es un día laborable"""
    try:
        if not configuracion:
            configuracion = obtener_configuracion_asistencia()
        
        dias_laborables = configuracion.get('dias_laborables', '1,2,3,4,5')
        dias_lista = [int(d.strip()) for d in dias_laborables.split(',')]
        
        # Python: lunes=0, domingo=6; Base datos: lunes=1, domingo=7
        dia_semana = fecha_actual.weekday() + 1
        
        print(f"📅 Verificando día laborable:")
        print(f"   - Fecha: {fecha_actual} ({obtener_nombre_dia_español(fecha_actual)})")
        print(f"   - Día de semana (1=Lun, 7=Dom): {dia_semana}")
        print(f"   - Días laborables configurados: {dias_lista}")
        print(f"   - ¿Es laborable?: {dia_semana in dias_lista}")
        
        return dia_semana in dias_lista
    except Exception as e:
        print(f"Error al verificar día laborable: {e}")
        return True  # Por defecto permitir

# ================================
# FUNCIONES ADICIONALES DE UTILIDAD
# ================================

def verificar_sistema_activo():
    """Verifica si el sistema de asistencia está activo"""
    try:
        sistema_activo = obtener_configuracion('sistema_activo', 'true')
        return sistema_activo.lower() in ['true', '1', 'yes', 'si']
    except:
        return True

def obtener_horarios_sistema():
    """Obtiene todos los horarios configurados del sistema"""
    try:
        return {
            'hora_entrada_inicio': obtener_configuracion('hora_entrada_inicio', '09:00:00'),
            'hora_entrada_fin': obtener_configuracion('hora_entrada_fin', '19:00:00'),
            'hora_salida_inicio': obtener_configuracion('hora_salida_inicio', '09:00:00'),
            'hora_salida_fin': obtener_configuracion('hora_salida_fin', '19:00:00'),
            'tolerancia_minutos': int(obtener_configuracion('tolerancia_minutos', '15'))
        }
    except Exception as e:
        print(f"Error al obtener horarios: {e}")
        return {
            'hora_entrada_inicio': '09:00:00',
            'hora_entrada_fin': '19:00:00',
            'hora_salida_inicio': '09:00:00',
            'hora_salida_fin': '19:00:00',
            'tolerancia_minutos': 15
        }
    
