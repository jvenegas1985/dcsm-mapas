from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect
import folium
import json
import os
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = 'clave_secreta_mantenimiento_2025'  # IMPORTANTE: Agregar secret key

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

# ESTA ES LA ÚNICA FUNCIÓN mantenimiento() - PROTEGIDA
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
    """Estadísticas totales por tipo"""
    distribuidores = cargar_datos_desde_json('distribuidores_autorizados.json')
    tiendas_oro = cargar_datos_desde_json('tiendas_oro.json')
    tiendas_satelite = cargar_datos_desde_json('tiendas_satelite.json')
    
    return {
        'distribuidores': len(distribuidores),
        'tiendas_oro': len(tiendas_oro),
        'tiendas_satelite': len(tiendas_satelite),
        'total_general': len(distribuidores) + len(tiendas_oro) + len(tiendas_satelite)
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
    
    # RUTA FÍSICA del archivo de icono
    ruta_icono = os.path.join(BASE_DIR, 'static', 'images', nombre_icono)
    
    # Verificar que el archivo existe
    if not os.path.exists(ruta_icono):
        print(f"⚠️  Icono no encontrado: {ruta_icono}")
        # Usar un icono por defecto de Folium
        return folium.Icon(color='red', icon='info-sign')
    
    # Crear el icono personalizado con la ruta física
    icono_personalizado = folium.CustomIcon(
        icon_image=ruta_icono,  # Ruta física del archivo
        icon_size=(60, 60),
        icon_anchor=(30, 30)
    )
    
    return icono_personalizado

def crear_mapa_completo():
    """Crea el mapa completo y devuelve el HTML"""
    mapa = crear_mapa_base()
    
    # Agregar capas
    agregar_capa_distribuidores(mapa)
    agregar_capa_tiendas_oro(mapa)
    agregar_capa_tiendas_satelite(mapa)
    
    # Control de capas en el lado IZQUIERDO y siempre visible
    folium.LayerControl(
        position='topleft',  # Cambiado de 'topright' a 'topleft'
        collapsed=False,
        autoZIndex=True
    ).add_to(mapa)
    
    # Devuelve el HTML del mapa, NO lo guarda
    return mapa._repr_html_()

def agregar_capa_distribuidores(mapa):
    """Capa 1: Distribuidores Autorizados"""
    distribuidores = cargar_datos_desde_json('distribuidores_autorizados.json')
    
    feature_group = folium.FeatureGroup(
        name=f' Distribuidores Autorizados ({len(distribuidores)})',
        show=True
    )
    
    for distribuidor in distribuidores:
        estado = distribuidor.get('estado', 'activo')
        icono_personalizado = obtener_icono_personalizado(estado, 'distribuidores')
        
        if estado in ['planeado', 'proxima_apertura', 'en_construccion']:
            emoji_tooltip = "📅"
            color_estado = "orange"
        else:
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
    """Capa 2: Tiendas de Oro"""
    tiendas = cargar_datos_desde_json('tiendas_oro.json')
    
    feature_group = folium.FeatureGroup(
        name=f'Tiendas Oro ({len(tiendas)})',
        show=True
    )
    
    for tienda in tiendas:
        estado = tienda.get('estado', 'activo')
        icono_personalizado = obtener_icono_personalizado(estado, 'tiendas_oro')
        
        if estado in ['planeado', 'proxima_apertura', 'en_construccion']:
            emoji_tooltip = "📅"
            color_estado = "orange"
        else:
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
    """Capa 3: Tiendas Satélite"""
    tiendas = cargar_datos_desde_json('tiendas_satelite.json')
    
    feature_group = folium.FeatureGroup(
        name=f'Tiendas Satélite ({len(tiendas)})',
        show=True
    )
    
    for tienda in tiendas:
        estado = tienda.get('estado', 'activo')
        icono_personalizado = obtener_icono_personalizado(estado, 'tiendas_satelite')
        
        if estado in ['planeado', 'proxima_apertura', 'en_construccion']:
            emoji_tooltip = "📅"
            color_estado = "orange"
        else:
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
# RUTAS DE MANTENIMIENTO (CRUD) - PROTEGIDAS
# ============================================================================

# RUTAS PARA DISTRIBUIDORES AUTORIZADOS
@app.route('/api/distribuidores', methods=['GET'])
def get_distribuidores():
    """Obtener todos los distribuidores"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    distribuidores = cargar_datos_desde_json('distribuidores_autorizados.json')
    return jsonify(distribuidores)

@app.route('/api/distribuidores', methods=['POST'])
def crear_distribuidor():
    """Crear nuevo distribuidor"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    datos = request.get_json()
    distribuidores = cargar_datos_desde_json('distribuidores_autorizados.json')
    
    # Generar ID único
    nuevo_id = f"D{len(distribuidores) + 1:03d}"
    datos['id'] = nuevo_id
    
    distribuidores.append(datos)
    
    if guardar_datos_en_json('distribuidores_autorizados.json', distribuidores):
        return jsonify({'success': True, 'id': nuevo_id})
    else:
        return jsonify({'success': False, 'error': 'Error al guardar'}), 500

@app.route('/api/distribuidores/<distribuidor_id>', methods=['PUT'])
def actualizar_distribuidor(distribuidor_id):
    """Actualizar distribuidor existente"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    datos = request.get_json()
    distribuidores = cargar_datos_desde_json('distribuidores_autorizados.json')
    
    for i, distribuidor in enumerate(distribuidores):
        if distribuidor['id'] == distribuidor_id:
            # Asegurarse de que el ID se mantenga
            datos['id'] = distribuidor_id
            distribuidores[i] = datos
            if guardar_datos_en_json('distribuidores_autorizados.json', distribuidores):
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'error': 'Error al guardar'}), 500
    
    return jsonify({'success': False, 'error': 'Distribuidor no encontrado'}), 404

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
    """Crear nueva tienda oro"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    datos = request.get_json()
    tiendas = cargar_datos_desde_json('tiendas_oro.json')
    
    # Generar ID único
    nuevo_id = f"TO{len(tiendas) + 1:03d}"
    datos['id'] = nuevo_id
    
    tiendas.append(datos)
    
    if guardar_datos_en_json('tiendas_oro.json', tiendas):
        return jsonify({'success': True, 'id': nuevo_id})
    else:
        return jsonify({'success': False, 'error': 'Error al guardar'}), 500

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
    """Crear nueva tienda satélite"""
    if not session.get('mantenimiento_autorizado'):
        return jsonify({'error': 'No autorizado'}), 401
    datos = request.get_json()
    tiendas = cargar_datos_desde_json('tiendas_satelite.json')
    
    # Generar ID único
    nuevo_id = f"TS{len(tiendas) + 1:03d}"
    datos['id'] = nuevo_id
    
    tiendas.append(datos)
    
    if guardar_datos_en_json('tiendas_satelite.json', tiendas):
        return jsonify({'success': True, 'id': nuevo_id})
    else:
        return jsonify({'success': False, 'error': 'Error al guardar'}), 500

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
        'logo-azul-activo.png', 'logo-azul-activo-next.png'
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