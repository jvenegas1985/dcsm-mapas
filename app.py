from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect
import folium
import json
import os
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = 'clave_secreta_mantenimiento_2025'

DATABASE_PATH = 'database'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# PIN hardcodeado
MAINTENANCE_PIN = "2025"

# Ruta para archivos estáticos
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/acceso-mantenimiento')
def acceso_mantenimiento():
    """Página de acceso con PIN"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Acceso Mantenimiento</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: #f8f9fa; }
            .login-box { max-width: 400px; margin: 100px auto; padding: 2rem; background: white; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h4 class="text-center mb-4">🔒 Acceso Mantenimiento</h4>
            <form method="POST" action="/verificar-pin">
                <div class="mb-3">
                    <label class="form-label">PIN de 4 dígitos:</label>
                    <input type="password" name="pin" class="form-control" maxlength="4" pattern="[0-9]{4}" required>
                </div>
                <button type="submit" class="btn btn-primary w-100">Acceder</button>
            </form>
            ''' + ('<div class="alert alert-danger mt-3">PIN incorrecto</div>' if request.args.get('error') else '') + '''
            <div class="text-center mt-3">
                <a href="/" class="text-muted">← Volver al inicio</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/verificar-pin', methods=['POST'])
def verificar_pin():
    """Verificar el PIN"""
    pin_ingresado = request.form.get('pin')
    
    if pin_ingresado == MAINTENANCE_PIN:
        session['mantenimiento_autorizado'] = True
        return redirect('/mantenimiento')
    else:
        return redirect('/acceso-mantenimiento?error=1')

@app.route('/mantenimiento')
def mantenimiento():
    """Página principal de mantenimiento (protegida)"""
    if not session.get('mantenimiento_autorizado'):
        return redirect('/acceso-mantenimiento')
    return render_template('mantenimiento.html')

@app.route('/logout-mantenimiento')
def logout_mantenimiento():
    """Cerrar sesión de mantenimiento"""
    session.pop('mantenimiento_autorizado', None)
    return redirect('/')

def cargar_datos_desde_json(archivo):
    """Carga datos desde JSON"""
    try:
        ruta_archivo = os.path.join(DATABASE_PATH, archivo)
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def guardar_datos_en_json(archivo, datos):
    """Guarda datos en JSON"""
    try:
        ruta_archivo = os.path.join(DATABASE_PATH, archivo)
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error guardando {archivo}: {e}")
        return False

def obtener_estadisticas_totales():
    """Estadísticas totales por tipo - SOLO ACTIVOS"""
    try:
        distribuidores = cargar_datos_desde_json('distribuidores_autorizados.json')
        tiendas_oro = cargar_datos_desde_json('tiendas_oro.json')
        tiendas_satelite = cargar_datos_desde_json('tiendas_satelite.json')
        centros_distribucion = cargar_datos_desde_json('centros_distribucion.json')
        
        # ✅ FILTRAR SOLO LOS ACTIVOS
        distribuidores_activos = [d for d in distribuidores if d.get('estado') == 'activo']
        tiendas_oro_activas = [t for t in tiendas_oro if t.get('estado') == 'activo']
        tiendas_satelite_activas = [t for t in tiendas_satelite if t.get('estado') == 'activo']
        centros_activos = [c for c in centros_distribucion if c.get('estado') == 'activo']
        
        # Estadísticas por estado (para información adicional)
        def contar_por_estado(datos):
            estados = {}
            for item in datos:
                estado = item.get('estado', 'activo')
                estados[estado] = estados.get(estado, 0) + 1
            return estados
        
        # Contar aperturas 2026 (solo de activos)
        def contar_2026(datos):
            return len([d for d in datos if d.get('fecha_apertura', '').startswith('2026')])
        
        stats = {
            # ✅ SOLO CONTAR ACTIVOS
            'distribuidores': len(distribuidores_activos),
            'tiendas_oro': len(tiendas_oro_activas),
            'tiendas_satelite': len(tiendas_satelite_activas),
            'centros_distribucion': len(centros_activos),
            'total_general': len(distribuidores_activos) + len(tiendas_oro_activas) + len(tiendas_satelite_activas) + len(centros_activos),
            
            # Información adicional (opcional)
            'por_estado': {
                'distribuidores': contar_por_estado(distribuidores),
                'tiendas_oro': contar_por_estado(tiendas_oro),
                'tiendas_satelite': contar_por_estado(tiendas_satelite),
                'centros_distribucion': contar_por_estado(centros_distribucion)
            },
            'aperturas_2026': {
                'distribuidores': contar_2026(distribuidores_activos),
                'tiendas_oro': contar_2026(tiendas_oro_activas),
                'tiendas_satelite': contar_2026(tiendas_satelite_activas),
                'centros_distribucion': contar_2026(centros_activos)
            },
            # Totales reales (para debug)
            '_totales_reales': {
                'distribuidores': len(distribuidores),
                'tiendas_oro': len(tiendas_oro),
                'tiendas_satelite': len(tiendas_satelite),
                'centros_distribucion': len(centros_distribucion)
            }
        }
        
        print(f"📊 Estadísticas calculadas - Activos: {stats['total_general']}")
        print(f"📊 Detalle - Distribuidores: {stats['distribuidores']}/{len(distribuidores)} activos")
        print(f"📊 Detalle - Tiendas Oro: {stats['tiendas_oro']}/{len(tiendas_oro)} activas")
        print(f"📊 Detalle - Tiendas Satélite: {stats['tiendas_satelite']}/{len(tiendas_satelite)} activas")
        print(f"📊 Detalle - Centros: {stats['centros_distribucion']}/{len(centros_distribucion)} activos")
        
        return stats
        
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        return {
            'distribuidores': 0,
            'tiendas_oro': 0,
            'tiendas_satelite': 0,
            'centros_distribucion': 0,
            'total_general': 0,
            'por_estado': {},
            'aperturas_2026': {},
            '_totales_reales': {}
        }
    


def crear_mapa_base():
    """Crea el mapa base"""
    return folium.Map(
        location=[9.7489, -83.7534],
        zoom_start=8,
        tiles='OpenStreetMap',
        control_scale=True
    )

def obtener_icono_personalizado(estado, tipo):
    """Devuelve icono personalizado según estado y tipo"""
    # Mapeo de iconos personalizados
    iconos_config = {
        'distribuidores': {
            'activo': 'logo-rojo-activo.png',
            'planeado': 'logo-rojo-activo-next.png',
            'proxima_apertura': 'logo-rojo-activo-next.png',
            'en_construccion': 'logo-rojo-activo-next.png'
        },
        'tiendas_oro': {
            'activo': 'logo-dorado-activo.png',
            'planeado': 'logo-dorado-activo-next.png',
            'proxima_apertura': 'logo-dorado-activo-next.png',
            'en_construccion': 'logo-dorado-activo-next.png'
        },
        'tiendas_satelite': {
            'activo': 'logo-azul-activo.png',
            'planeado': 'logo-azul-activo-next.png',
            'proxima_apertura': 'logo-azul-activo-next.png',
            'en_construccion': 'logo-azul-activo-next.png'
        },
        'centros_distribucion': {
            'activo': 'logo-verde-activo.png',
            'planeado': 'logo-verde-activo-next.png',
            'proxima_apertura': 'logo-verde-activo-next.png',
            'en_construccion': 'logo-verde-activo-next.png'
        }
    }
    
    # Determinar el estado clave
    estado_clave = 'activo'  # por defecto
    if estado in ['planeado', 'proxima_apertura', 'en_construccion']:
        estado_clave = 'planeado'
    elif estado in ['activo']:
        estado_clave = 'activo'
    
    # Obtener el nombre del archivo de icono
    nombre_icono = iconos_config.get(tipo, {}).get(estado_clave, 'logo-rojo-activo.png')
    
    # RUTA FÍSICA del archivo de icono (corregido)
    ruta_icono = os.path.join(BASE_DIR, 'static', 'images', nombre_icono)
    
    # Verificar que el archivo existe
    if not os.path.exists(ruta_icono):
        print(f"⚠️  Icono no encontrado: {ruta_icono}")
        # Usar un icono por defecto de Folium como fallback
        return folium.Icon(color='red', icon='info-sign')
    
    # 🔥 TAMAÑOS ESPECÍFICOS POR TIPO
    if tipo == 'tiendas_oro':
        # Iconos dorados MÁS PEQUEÑOS
        icon_size = (42, 42)
        icon_anchor = (21, 21)
    elif tipo == 'tiendas_satelite':
        # Iconos azules MÁS PEQUEÑOS  
        icon_size = (42, 42)
        icon_anchor = (21, 21)
    elif tipo == 'centros_distribucion':
        # Iconos verdes - tamaño mediano
        icon_size = (55, 55)
        icon_anchor = (27, 27)
    else:
        # Distribuidores - tamaño estándar pequeño
        icon_size = (65, 65)
        icon_anchor = (29, 29)
    
    icono_personalizado = folium.CustomIcon(
        icon_image=ruta_icono,
        icon_size=icon_size,
        icon_anchor=icon_anchor
    )
    
    return icono_personalizado

def crear_mapa_completo():
    """Crea el mapa completo y devuelve el HTML"""
    mapa = crear_mapa_base()
    
    # Agregar capas principales (SOLO ACTIVAS)
    agregar_capa_centros_distribucion(mapa)  # NUEVA CAPA PRINCIPAL
    agregar_capa_distribuidores(mapa)
    agregar_capa_tiendas_oro(mapa)
    agregar_capa_tiendas_satelite(mapa)
    
    # Agregar capas filtradas para Próxima Apertura 2026
    agregar_capa_distribuidores_2026(mapa)
    agregar_capa_tiendas_oro_2026(mapa)
    agregar_capa_tiendas_satelite_2026(mapa)
    #agregar_capa_centros_distribucion_2026(mapa)  # NUEVA CAPA FILTRADA
    
    # Control de capas personalizado - MÁS GRANDE Y VISIBLE
    folium.LayerControl(
        position='topleft',
        collapsed=False,
        autoZIndex=True,
        style={'font-size': '16px', 'padding': '10px'}
    ).add_to(mapa)
    
    # Agregar CSS personalizado para hacer los checkboxes más grandes
    css_style = """
    <style>
        .leaflet-control-layers label {
            font-size: 16px !important;
            padding: 8px 5px !important;
            margin: 5px 0 !important;
        }
        .leaflet-control-layers input[type="checkbox"] {
            transform: scale(1.5) !important;
            margin-right: 10px !important;
        }
        .leaflet-control-layers {
            background: white !important;
            border: 2px solid #ccc !important;
            border-radius: 8px !important;
            padding: 15px !important;
            max-height: 80vh !important;
            overflow-y: auto !important;
        }
        .leaflet-control-layers-base label:hover {
            background-color: #f8f9fa !important;
        }
    </style>
    """
    mapa.get_root().header.add_child(folium.Element(css_style))
    
    # Devuelve el HTML del mapa, NO lo guarda
    return mapa._repr_html_()

# ============================================================================
# NUEVA CAPA PRINCIPAL: CENTROS DE DISTRIBUCIÓN
# ============================================================================

def agregar_capa_centros_distribucion(mapa):
    """Capa 1: Centros de Distribución (SOLO ACTIVOS)"""
    centros = cargar_datos_desde_json('centros_distribucion.json')
    
    # FILTRAR SOLO CENTROS ACTIVOS
    centros_activos = [c for c in centros if c.get('estado') == 'activo']
    
    feature_group = folium.FeatureGroup(
        name=f'🏭 Centros De Distribución ({len(centros_activos)})',
        show=True
    )
    
    for centro in centros_activos:
        estado = centro.get('estado', 'activo')
        icono_personalizado = obtener_icono_personalizado(estado, 'centros_distribucion')
        
        emoji_tooltip = "🏭"
        color_estado = "darkgreen"
        
        html_popup = f"""
        <div style='min-width: 350px;'>
            <h4>{emoji_tooltip} {centro['nombre']}</h4>
            <b>Tipo:</b> Centro de Distribución<br>
            <b>Estado:</b> <span style="color: {color_estado}">{estado.replace('_', ' ').title()}</span><br>
            <b>ID:</b> {centro['id']}<br>
            <b>Ciudad:</b> {centro['ciudad']}<br>
            <b>Dirección:</b> {centro['direccion']}<br>
            <b>Teléfono:</b> {centro.get('telefono', 'N/A')}<br>
            <b>Capacidad Almacén:</b> {centro.get('capacidad_almacen', 'N/A')}<br>
            <b>Tipo Centro:</b> {centro.get('tipo_centro', 'N/A')}<br>
            <b>Zona Cobertura:</b> {centro.get('zona_cobertura', 'N/A')}<br>
            <b>Responsable:</b> {centro.get('responsable', 'N/A')}<br>
            <b>Fecha Apertura:</b> {centro.get('fecha_apertura', 'N/A')}<br>
            <hr>
            <small><i>Centro de Distribución - Carnes San Martín</i></small>
        </div>
        """
        
        folium.Marker(
            location=[centro['lat'], centro['lon']],
            popup=folium.Popup(html_popup, max_width=400),
            tooltip=f"{emoji_tooltip} {centro['nombre']}",
            icon=icono_personalizado
        ).add_to(feature_group)
    
    feature_group.add_to(mapa)


@app.route('/api/distribuidores', methods=['GET'])
def get_distribuidores():
    """Obtener todos los distribuidores"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    distribuidores = cargar_datos_desde_json('distribuidores_autorizados.json')
    return jsonify(distribuidores)

@app.route('/api/distribuidores', methods=['POST'])
def crear_distribuidor():
    """Crear nuevo distribuidor con ID único"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        datos = request.get_json()
        print(f"📝 Datos recibidos para nuevo distribuidor: {datos}")
        
        # Validar campos requeridos
        campos_requeridos = ['nombre', 'ciudad', 'direccion', 'lat', 'lon']
        for campo in campos_requeridos:
            if campo not in datos or not str(datos[campo]).strip():
                return jsonify({'success': False, 'error': f'Campo requerido: {campo}'}), 400
        
        distribuidores = cargar_datos_desde_json('distribuidores_autorizados.json')
        
        # ✅ CORREGIDO: Generar ID único verificando existencia
        nuevo_id = generar_id_unico('distribuidores', distribuidores)
        datos['id'] = nuevo_id
        
        # Establecer valores por defecto si no se proporcionan
        datos.setdefault('estado', 'activo')
        datos.setdefault('fecha_apertura', datetime.now().strftime('%Y-%m-%d'))
        
        distribuidores.append(datos)
        
        if guardar_datos_en_json('distribuidores_autorizados.json', distribuidores):
            print(f"✅ Nuevo distribuidor creado: {nuevo_id} - {datos['nombre']}")
            return jsonify({'success': True, 'id': nuevo_id, 'distribuidor': datos})
        else:
            return jsonify({'success': False, 'error': 'Error al guardar'}), 500
            
    except Exception as e:
        print(f"❌ Error creando distribuidor: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    


    
@app.route('/api/distribuidores/<distribuidor_id>', methods=['PUT'])
def actualizar_distribuidor(distribuidor_id):
    """Actualizar distribuidor existente con manejo correcto de campos"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        datos = request.get_json()
        print(f"📝 Datos recibidos para actualizar {distribuidor_id}: {datos}")  # Debug
        
        distribuidores = cargar_datos_desde_json('distribuidores_autorizados.json')
        
        for i, distribuidor in enumerate(distribuidores):
            if distribuidor['id'] == distribuidor_id:
                # ✅ CORRECTO: Actualizar solo los campos que vienen en la solicitud
                # Mantener los campos existentes que no se están actualizando
                for key, value in datos.items():
                    distribuidor[key] = value
                
                # Asegurar que el ID no cambie
                distribuidor['id'] = distribuidor_id
                
                print(f"✅ Distribuidor actualizado: {distribuidor}")  # Debug
                
                if guardar_datos_en_json('distribuidores_autorizados.json', distribuidores):
                    return jsonify({'success': True, 'distribuidor': distribuidor})
                else:
                    return jsonify({'success': False, 'error': 'Error al guardar'}), 500
        
        return jsonify({'success': False, 'error': 'Distribuidor no encontrado'}), 404
        
    except Exception as e:
        print(f"❌ Error actualizando distribuidor: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/distribuidores/<distribuidor_id>', methods=['DELETE'])
def eliminar_distribuidor(distribuidor_id):
    """Eliminar distribuidor"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    distribuidores = cargar_datos_desde_json('distribuidores_autorizados.json')
    
    for i, distribuidor in enumerate(distribuidores):
        if distribuidor['id'] == distribuidor_id:
            distribuidores.pop(i)
            if guardar_datos_en_json('distribuidores_autorizados.json', distribuidores):
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'error': 'Error al guardar'}), 500
    
    return jsonify({'success': False, 'error': 'Distribuidor no encontrado'}), 404  



# RUTAS PARA TIENDAS ORO
@app.route('/api/tiendas-oro', methods=['GET'])
def get_tiendas_oro():
    """Obtener todas las tiendas oro"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    tiendas = cargar_datos_desde_json('tiendas_oro.json')
    return jsonify(tiendas)

@app.route('/api/tiendas-oro', methods=['POST'])
def crear_tienda_oro():
    """Crear nueva tienda oro con ID único"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        datos = request.get_json()
        tiendas = cargar_datos_desde_json('tiendas_oro.json')
        
        # ✅ CORREGIDO: Generar ID único verificando existencia
        nuevo_id = generar_id_unico('tiendas_oro', tiendas)
        datos['id'] = nuevo_id
        
        tiendas.append(datos)
        
        if guardar_datos_en_json('tiendas_oro.json', tiendas):
            return jsonify({'success': True, 'id': nuevo_id})
        else:
            return jsonify({'success': False, 'error': 'Error al guardar'}), 500
            
    except Exception as e:
        print(f"❌ Error creando tienda oro: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    




@app.route('/api/tiendas-oro/<tienda_id>', methods=['PUT'])
def actualizar_tienda_oro(tienda_id):
    """Actualizar tienda oro existente"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    datos = request.get_json()
    tiendas = cargar_datos_desde_json('tiendas_oro.json')
    
    for i, tienda in enumerate(tiendas):
        if tienda['id'] == tienda_id:
            # Asegurarse de que el ID se mantenga
            datos['id'] = tienda_id
            tiendas[i] = datos
            if guardar_datos_en_json('tiendas_oro.json', tiendas):
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'error': 'Error al guardar'}), 500
    
    return jsonify({'success': False, 'error': 'Tienda no encontrada'}), 404

@app.route('/api/tiendas-oro/<tienda_id>', methods=['DELETE'])
def eliminar_tienda_oro(tienda_id):
    """Eliminar tienda oro"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    tiendas = cargar_datos_desde_json('tiendas_oro.json')
    
    for i, tienda in enumerate(tiendas):
        if tienda['id'] == tienda_id:
            tiendas.pop(i)
            if guardar_datos_en_json('tiendas_oro.json', tiendas):
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'error': 'Error al guardar'}), 500
    
    return jsonify({'success': False, 'error': 'Tienda no encontrada'}), 404

# RUTAS PARA TIENDAS SATÉLITE
@app.route('/api/tiendas-satelite', methods=['GET'])
def get_tiendas_satelite():
    """Obtener todas las tiendas satélite"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    tiendas = cargar_datos_desde_json('tiendas_satelite.json')
    return jsonify(tiendas)

@app.route('/api/tiendas-satelite', methods=['POST'])
def crear_tienda_satelite():
    """Crear nueva tienda satélite con ID único"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        datos = request.get_json()
        tiendas = cargar_datos_desde_json('tiendas_satelite.json')
        
        # ✅ CORREGIDO: Generar ID único verificando existencia
        nuevo_id = generar_id_unico('tiendas_satelite', tiendas)
        datos['id'] = nuevo_id
        
        tiendas.append(datos)
        
        if guardar_datos_en_json('tiendas_satelite.json', tiendas):
            return jsonify({'success': True, 'id': nuevo_id})
        else:
            return jsonify({'success': False, 'error': 'Error al guardar'}), 500
            
    except Exception as e:
        print(f"❌ Error creando tienda satélite: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    



@app.route('/api/tiendas-satelite/<tienda_id>', methods=['PUT'])
def actualizar_tienda_satelite(tienda_id):
    """Actualizar tienda satélite existente"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    datos = request.get_json()
    tiendas = cargar_datos_desde_json('tiendas_satelite.json')
    
    for i, tienda in enumerate(tiendas):
        if tienda['id'] == tienda_id:
            # Asegurarse de que el ID se mantenga
            datos['id'] = tienda_id
            tiendas[i] = datos
            if guardar_datos_en_json('tiendas_satelite.json', tiendas):
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'error': 'Error al guardar'}), 500
    
    return jsonify({'success': False, 'error': 'Tienda no encontrada'}), 404

@app.route('/api/tiendas-satelite/<tienda_id>', methods=['DELETE'])
def eliminar_tienda_satelite(tienda_id):
    """Eliminar tienda satélite"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    tiendas = cargar_datos_desde_json('tiendas_satelite.json')
    
    for i, tienda in enumerate(tiendas):
        if tienda['id'] == tienda_id:
            tiendas.pop(i)
            if guardar_datos_en_json('tiendas_satelite.json', tiendas):
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'error': 'Error al guardar'}), 500
    
    return jsonify({'success': False, 'error': 'Tienda no encontrada'}), 404


# ============================================================================
# CAPAS PRINCIPALES EXISTENTES (modificadas)
# ============================================================================

def agregar_capa_distribuidores(mapa):
    """Capa 2: Distribuidores Autorizados (SOLO ACTIVOS)"""
    distribuidores = cargar_datos_desde_json('distribuidores_autorizados.json')
    
    distribuidores_activos = [d for d in distribuidores if d.get('estado') == 'activo']
    
    feature_group = folium.FeatureGroup(
        name=f'📦 Distribuidores Autorizados Activos ({len(distribuidores_activos)})',
        show=True
    )
    
    for distribuidor in distribuidores_activos:
        estado = distribuidor.get('estado', 'activo')
        icono_personalizado = obtener_icono_personalizado(estado, 'distribuidores')
        
        emoji_tooltip = "📦"
        color_estado = "green"
        
        html_popup = f"""
        <div style='min-width: 320px;'>
            <h4>{emoji_tooltip} {distribuidor['nombre']}</h4>
            <b>Tipo:</b> Distribuidor Autorizado<br>
            <b>Estado:</b> <span style="color: {color_estado}">{estado.replace('_', ' ').title()}</span><br>
            <b>ID:</b> {distribuidor['id']}<br>
            <b>Ciudad:</b> {distribuidor['ciudad']}<br>
            <b>Dirección:</b> {distribuidor['direccion']}<br>
            <b>Teléfono:</b> {distribuidor.get('telefono', 'N/A')}<br>
            <b>Fecha Apertura:</b> {distribuidor.get('fecha_apertura', 'N/A')}<br>
            <hr>
            <small><i>Carnes San Martín</i></small>
        </div>
        """
        
        folium.Marker(
            location=[distribuidor['lat'], distribuidor['lon']],
            popup=folium.Popup(html_popup, max_width=350),
            tooltip=f"{emoji_tooltip} {distribuidor['nombre']}",
            icon=icono_personalizado
        ).add_to(feature_group)
    
    feature_group.add_to(mapa)

def agregar_capa_tiendas_oro(mapa):
    """Capa 3: Tiendas de Oro (SOLO ACTIVAS)"""
    tiendas = cargar_datos_desde_json('tiendas_oro.json')
    
    tiendas_activas = [t for t in tiendas if t.get('estado') == 'activo']
    
    feature_group = folium.FeatureGroup(
        name=f'🥇 Tiendas Oro Activas ({len(tiendas_activas)})',
        show=True
    )
    
    for tienda in tiendas_activas:
        estado = tienda.get('estado', 'activo')
        icono_personalizado = obtener_icono_personalizado(estado, 'tiendas_oro')
        
        emoji_tooltip = "🥇"
        color_estado = "blue"
        
        html_popup = f"""
        <div style='min-width: 300px;'>
            <h4>{emoji_tooltip} {tienda['nombre']}</h4>
            <b>Estado:</b> <span style="color: {color_estado}">{estado.replace('_', ' ').title()}</span><br>
            <b>ID:</b> {tienda['id']}<br>
            <b>Ciudad:</b> {tienda['ciudad']}<br>
            <b>Dirección:</b> {tienda['direccion']}<br>
            <b>Capacidad Congelador:</b> {tienda.get('capacidad_congelador', 'N/A')}<br>
            <b>Fecha Apertura:</b> {tienda.get('fecha_apertura', 'N/A')}<br>
            <hr>
            <small><i>Tienda Oro - Carnes San Martín</i></small>
        </div>
        """
        
        folium.Marker(
            location=[tienda['lat'], tienda['lon']],
            popup=folium.Popup(html_popup, max_width=350),
            tooltip=f"{emoji_tooltip} {tienda['nombre']}",
            icon=icono_personalizado
        ).add_to(feature_group)
    
    feature_group.add_to(mapa)

def agregar_capa_tiendas_satelite(mapa):
    """Capa 4: Tiendas Satélite (SOLO ACTIVAS)"""
    tiendas = cargar_datos_desde_json('tiendas_satelite.json')
    
    tiendas_activas = [t for t in tiendas if t.get('estado') == 'activo']
    
    feature_group = folium.FeatureGroup(
        name=f'🛒 Tiendas Satélite Activas ({len(tiendas_activas)})',
        show=True
    )
    
    for tienda in tiendas_activas:
        estado = tienda.get('estado', 'activo')
        icono_personalizado = obtener_icono_personalizado(estado, 'tiendas_satelite')
        
        emoji_tooltip = "🛒"
        color_estado = "green"
        
        html_popup = f"""
        <div style='min-width: 300px;'>
            <h4>{emoji_tooltip} {tienda['nombre']}</h4>
            <b>Estado:</b> <span style="color: {color_estado}">{estado.replace('_', ' ').title()}</span><br>
            <b>ID:</b> {tienda['id']}<br>
            <b>Ciudad:</b> {tienda['ciudad']}<br>
            <b>Dirección:</b> {tienda['direccion']}<br>
            <b>Tipo:</b> {tienda.get('tipo_satelite', 'N/A')}<br>
            <b>Fecha Apertura:</b> {tienda.get('fecha_apertura', 'N/A')}<br>
            <hr>
            <small><i>Tienda Satélite - Carnes San Martín</i></small>
        </div>
        """
        
        folium.Marker(
            location=[tienda['lat'], tienda['lon']],
            popup=folium.Popup(html_popup, max_width=350),
            tooltip=f"{emoji_tooltip} {tienda['nombre']}",
            icon=icono_personalizado
        ).add_to(feature_group)
    
    feature_group.add_to(mapa)

# ============================================================================
# CAPAS FILTRADAS 2026 (incluyendo nueva para Centros)
# ============================================================================

def agregar_capa_centros_distribucion_2026(mapa):
    """Capa 5: Centros de Distribución con Próxima Apertura en 2026"""
    centros = cargar_datos_desde_json('centros_distribucion.json')
    
    centros_filtrados = [
        c for c in centros 
        if c.get('estado') == 'proxima_apertura' 
        and c.get('fecha_apertura', '').startswith('2026')
    ]
    
    feature_group = folium.FeatureGroup(
        name=f'🎯 Centros Distribución 2026 ({len(centros_filtrados)})',
        show=False
    )
    
    for centro in centros_filtrados:
        icono_personalizado = obtener_icono_personalizado('proxima_apertura', 'centros_distribucion')
        
        html_popup = f"""
        <div style='min-width: 350px;'>
            <h4>🎯 {centro['nombre']}</h4>
            <b>Tipo:</b> Centro de Distribución<br>
            <b>Estado:</b> <span style="color: purple">Próxima Apertura 2026</span><br>
            <b>ID:</b> {centro['id']}<br>
            <b>Ciudad:</b> {centro['ciudad']}<br>
            <b>Dirección:</b> {centro['direccion']}<br>
            <b>Teléfono:</b> {centro.get('telefono', 'N/A')}<br>
            <b>Capacidad Almacén:</b> {centro.get('capacidad_almacen', 'N/A')}<br>
            <b>Tipo Centro:</b> {centro.get('tipo_centro', 'N/A')}<br>
            <b>Zona Cobertura:</b> {centro.get('zona_cobertura', 'N/A')}<br>
            <b>Fecha Apertura:</b> {centro.get('fecha_apertura', 'N/A')}<br>
            <hr>
            <small><i>📍 Apertura Programada 2026 - Centro Distribución</i></small>
        </div>
        """
        
        folium.Marker(
            location=[centro['lat'], centro['lon']],
            popup=folium.Popup(html_popup, max_width=400),
            tooltip=f"🎯 2026 - {centro['nombre']}",
            icon=icono_personalizado
        ).add_to(feature_group)
    
    feature_group.add_to(mapa)

def agregar_capa_distribuidores_2026(mapa):
    """Capa 6: Distribuidores con Próxima Apertura en 2026"""
    distribuidores = cargar_datos_desde_json('distribuidores_autorizados.json')
    
    distribuidores_filtrados = [
        d for d in distribuidores 
        if d.get('estado') == 'proxima_apertura' 
        and d.get('fecha_apertura', '').startswith('2026')
    ]
    
    feature_group = folium.FeatureGroup(
        name=f'🎯 Distribuidores Autorizados 2026 ({len(distribuidores_filtrados)})',
        show=False
    )
    
    for distribuidor in distribuidores_filtrados:
        icono_personalizado = obtener_icono_personalizado('proxima_apertura', 'distribuidores')
        
        html_popup = f"""
        <div style='min-width: 320px;'>
            <h4>🎯 {distribuidor['nombre']}</h4>
            <b>Tipo:</b> Distribuidor Autorizado<br>
            <b>Estado:</b> <span style="color: purple">Próxima Apertura 2026</span><br>
            <b>ID:</b> {distribuidor['id']}<br>
            <b>Ciudad:</b> {distribuidor['ciudad']}<br>
            <b>Dirección:</b> {distribuidor['direccion']}<br>
            <b>Teléfono:</b> {distribuidor.get('telefono', 'N/A')}<br>
            <b>Fecha Apertura:</b> {distribuidor.get('fecha_apertura', 'N/A')}<br>
            <hr>
            <small><i>📍 Apertura Programada 2026 - Carnes San Martín</i></small>
        </div>
        """
        
        folium.Marker(
            location=[distribuidor['lat'], distribuidor['lon']],
            popup=folium.Popup(html_popup, max_width=350),
            tooltip=f"🎯 2026 - {distribuidor['nombre']}",
            icon=icono_personalizado
        ).add_to(feature_group)
    
    feature_group.add_to(mapa)

def agregar_capa_tiendas_oro_2026(mapa):
    """Capa 7: Tiendas Oro con Próxima Apertura en 2026"""
    tiendas = cargar_datos_desde_json('tiendas_oro.json')
    
    tiendas_filtradas = [
        t for t in tiendas 
        if t.get('estado') == 'proxima_apertura' 
        and t.get('fecha_apertura', '').startswith('2026')
    ]
    
    feature_group = folium.FeatureGroup(
        name=f'🎯 Tiendas Oro 2026 ({len(tiendas_filtradas)})',
        show=False
    )
    
    for tienda in tiendas_filtradas:
        icono_personalizado = obtener_icono_personalizado('proxima_apertura', 'tiendas_oro')
        
        html_popup = f"""
        <div style='min-width: 300px;'>
            <h4>🎯 {tienda['nombre']}</h4>
            <b>Estado:</b> <span style="color: purple">Próxima Apertura 2026</span><br>
            <b>ID:</b> {tienda['id']}<br>
            <b>Ciudad:</b> {tienda['ciudad']}<br>
            <b>Dirección:</b> {tienda['direccion']}<br>
            <b>Capacidad Congelador:</b> {tienda.get('capacidad_congelador', 'N/A')}<br>
            <b>Fecha Apertura:</b> {tienda.get('fecha_apertura', 'N/A')}<br>
            <hr>
            <small><i>📍 Apertura Programada 2026 - Tienda Oro</i></small>
        </div>
        """
        
        folium.Marker(
            location=[tienda['lat'], tienda['lon']],
            popup=folium.Popup(html_popup, max_width=350),
            tooltip=f"🎯 2026 - {tienda['nombre']}",
            icon=icono_personalizado
        ).add_to(feature_group)
    
    feature_group.add_to(mapa)

def agregar_capa_tiendas_satelite_2026(mapa):
    """Capa 8: Tiendas Satélite con Próxima Apertura en 2026"""
    tiendas = cargar_datos_desde_json('tiendas_satelite.json')
    
    tiendas_filtradas = [
        t for t in tiendas 
        if t.get('estado') == 'proxima_apertura' 
        and t.get('fecha_apertura', '').startswith('2026')
    ]
    
    feature_group = folium.FeatureGroup(
        name=f'🎯 Tiendas Satélite 2026 ({len(tiendas_filtradas)})',
        show=False
    )
    
    for tienda in tiendas_filtradas:
        icono_personalizado = obtener_icono_personalizado('proxima_apertura', 'tiendas_satelite')
        
        html_popup = f"""
        <div style='min-width: 300px;'>
            <h4>🎯 {tienda['nombre']}</h4>
            <b>Estado:</b> <span style="color: purple">Próxima Apertura 2026</span><br>
            <b>ID:</b> {tienda['id']}<br>
            <b>Ciudad:</b> {tienda['ciudad']}<br>
            <b>Dirección:</b> {tienda['direccion']}<br>
            <b>Tipo:</b> {tienda.get('tipo_satelite', 'N/A')}<br>
            <b>Fecha Apertura:</b> {tienda.get('fecha_apertura', 'N/A')}<br>
            <hr>
            <small><i>📍 Apertura Programada 2026 - Tienda Satélite</i></small>
        </div>
        """
        
        folium.Marker(
            location=[tienda['lat'], tienda['lon']],
            popup=folium.Popup(html_popup, max_width=350),
            tooltip=f"🎯 2026 - {tienda['nombre']}",
            icon=icono_personalizado
        ).add_to(feature_group)
    
    feature_group.add_to(mapa)

# ============================================================================
# NUEVAS RUTAS API PARA CENTROS DE DISTRIBUCIÓN
# ============================================================================

@app.route('/api/centros-distribucion', methods=['GET'])
def get_centros_distribucion():
    """Obtener todos los centros de distribución"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    centros = cargar_datos_desde_json('centros_distribucion.json')
    return jsonify(centros)

@app.route('/api/centros-distribucion', methods=['POST'])
def crear_centro_distribucion():
    """Crear nuevo centro de distribución con ID único"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        datos = request.get_json()
        centros = cargar_datos_desde_json('centros_distribucion.json')
        
        # ✅ CORREGIDO: Generar ID único verificando existencia
        nuevo_id = generar_id_unico('centros_distribucion', centros)
        datos['id'] = nuevo_id
        
        centros.append(datos)
        
        if guardar_datos_en_json('centros_distribucion.json', centros):
            return jsonify({'success': True, 'id': nuevo_id})
        else:
            return jsonify({'success': False, 'error': 'Error al guardar'}), 500
            
    except Exception as e:
        print(f"❌ Error creando centro: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    


@app.route('/api/centros-distribucion/<centro_id>', methods=['PUT'])
def actualizar_centro_distribucion(centro_id):
    """Actualizar centro de distribución existente"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    datos = request.get_json()
    centros = cargar_datos_desde_json('centros_distribucion.json')
    
    for i, centro in enumerate(centros):
        if centro['id'] == centro_id:
            datos['id'] = centro_id
            centros[i] = datos
            if guardar_datos_en_json('centros_distribucion.json', centros):
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'error': 'Error al guardar'}), 500
    
    return jsonify({'success': False, 'error': 'Centro no encontrado'}), 404

@app.route('/api/centros-distribucion/<centro_id>', methods=['DELETE'])
def eliminar_centro_distribucion(centro_id):
    """Eliminar centro de distribución"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    centros = cargar_datos_desde_json('centros_distribucion.json')
    
    for i, centro in enumerate(centros):
        if centro['id'] == centro_id:
            centros.pop(i)
            if guardar_datos_en_json('centros_distribucion.json', centros):
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'error': 'Error al guardar'}), 500
    
    return jsonify({'success': False, 'error': 'Centro no encontrado'}), 404

# [Mantener todas las otras rutas API existentes...]




def generar_id_unico(tipo, datos_existentes):
    """Genera un ID único verificando que no exista"""
    prefix = {
        'distribuidores': 'D',
        'tiendas_oro': 'TO', 
        'tiendas_satelite': 'TS',
        'centros_distribucion': 'CD'
    }.get(tipo, 'ID')
    
    # Obtener todos los IDs existentes
    ids_existentes = {item['id'] for item in datos_existentes}
    
    # Buscar el próximo ID disponible
    contador = 1
    while True:
        nuevo_id = f"{prefix}{contador:03d}"
        if nuevo_id not in ids_existentes:
            return nuevo_id
        contador += 1
        
        # Prevención de bucle infinito
        if contador > 1000:
            raise ValueError("No se pudo generar un ID único después de 1000 intentos")



# ============================================================================
# RUTAS PRINCIPALES
# ============================================================================

@app.route('/')
def index():
    """Página principal"""
    stats = obtener_estadisticas_totales()
    return render_template('index.html', stats=stats)











@app.route('/mapa')
def mostrar_mapa():
    """Renderiza el mapa directamente sin guardar archivos"""
    mapa_html = crear_mapa_completo()
    return render_template('mapa.html', mapa_html=mapa_html)

# Ruta para verificar archivos de iconos
@app.route('/verificar-iconos')
def verificar_iconos():
    """Página para verificar que todos los iconos existen"""
    iconos = [
        'logo-rojo-activo.png', 'logo-rojo-activo-next.png',
        'logo-dorado-activo.png', 'logo-dorado-activo-next.png', 
        'logo-azul-activo.png', 'logo-azul-activo-next.png',
        'logo-verde-activo.png', 'logo-verde-activo-next.png'
    ]
    
    resultados = []
    for icono in iconos:
        ruta = os.path.join(BASE_DIR, 'static', 'images', icono)
        existe = os.path.exists(ruta)
        resultados.append({
            'icono': icono,
            'ruta': ruta,
            'existe': existe
        })
    
    html = "<h1>Verificación de Iconos</h1>"
    for resultado in resultados:
        status = "✅ EXISTE" if resultado['existe'] else "❌ NO EXISTE"
        html += f"<p>{status} - {resultado['icono']}</p>"
        if resultado['existe']:
            html += f'<img src="/static/images/{resultado["icono"]}" style="width: 50px; margin: 5px;">'
    
    return html

if __name__ == '__main__':
    # Crear directorios si no existen
    os.makedirs(DATABASE_PATH, exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    
    print("📍 Verificando estructura de archivos...")
    print(f"📁 Directorio base: {BASE_DIR}")
    print(f"📁 Static images: {os.path.join(BASE_DIR, 'static', 'images')}")
    
    app.run(debug=True, host='0.0.0.0', port=8000)