// Navegación entre secciones
document.addEventListener('DOMContentLoaded', function() {
    // Cargar solo los datos de la sección activa inicial (Centros de Distribución)
    cargarCentrosDistribucion();

    // Configurar navegación
    const navLinks = document.querySelectorAll('.nav-link[data-target]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remover active de todos
            navLinks.forEach(nl => nl.classList.remove('active'));
            document.querySelectorAll('.content-section').forEach(section => {
                section.classList.remove('active');
            });
            
            // Activar actual
            this.classList.add('active');
            const target = this.getAttribute('data-target');
            document.getElementById(target).classList.add('active');
            
            // Cargar datos de la sección activa
            cargarSeccionActiva();
        });
    });
});

function cargarSeccionActiva() {
    const seccionActiva = document.querySelector('.content-section.active');
    if (!seccionActiva) return;
    
    const seccionId = seccionActiva.id;
    console.log('Cargando sección:', seccionId);
    
    switch(seccionId) {
        case 'centros-distribucion':
            cargarCentrosDistribucion();
            break;
        case 'distribuidores':
            cargarDistribuidores();
            break;
        case 'tiendas-oro':
            cargarTiendasOro();
            break;
        case 'tiendas-satelite':
            cargarTiendasSatelite();
            break;
    }
}
// ============================================================================
// FUNCIONES PARA CENTROS DE DISTRIBUCIÓN
// ============================================================================

function exportarDatos() {
    mostrarLoadingGestion('Exportando datos...');
    
    fetch('/api/exportar-datos')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Crear y descargar archivo JSON
                const blob = new Blob([JSON.stringify(data.datos, null, 2)], { 
                    type: 'application/json;charset=utf-8' 
                });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `backup_datos_carnes_san_martin_${new Date().toISOString().split('T')[0]}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
                mostrarResultadoGestion('success', 
                    `✅ <strong>Datos exportados correctamente</strong><br>
                     📊 <strong>Resumen:</strong><br>
                     • ${data.resumen.centros} centros de distribución<br>
                     • ${data.resumen.distribuidores} distribuidores autorizados<br>
                     • ${data.resumen.tiendas_oro} tiendas oro<br>
                     • ${data.resumen.tiendas_satelite} tiendas satélite<br>
                     • <strong>Total: ${data.resumen.total} ubicaciones</strong>`);
            } else {
                mostrarResultadoGestion('error', `❌ <strong>Error al exportar:</strong> ${data.error || 'Error desconocido'}`);
            }
        })
        .catch(error => {
            console.error('Error exportando datos:', error);
            mostrarResultadoGestion('error', `❌ <strong>Error de conexión:</strong> ${error.message}`);
        });
}

function importarDatos() {
    const fileInput = document.getElementById('importFile');
    const file = fileInput.files[0];
    
    if (!file) {
        mostrarResultadoGestion('error', '❌ <strong>Por favor selecciona un archivo JSON</strong>');
        return;
    }
    
    // Validar tipo de archivo
    if (!file.name.toLowerCase().endsWith('.json')) {
        mostrarResultadoGestion('error', '❌ <strong>El archivo debe ser un JSON</strong>');
        return;
    }
    
    const reader = new FileReader();
    
    reader.onload = function(e) {
        try {
            const datos = JSON.parse(e.target.result);
            
            // Validar estructura básica del JSON
            if (!datos || typeof datos !== 'object') {
                throw new Error('El archivo JSON no tiene una estructura válida');
            }
            
            // Confirmar antes de importar (ya que reemplaza todo)
            if (!confirm('⚠️ ¿Estás seguro de importar estos datos?\n\nEsto reemplazará TODOS los datos actuales. Esta acción no se puede deshacer.')) {
                return;
            }
            
            mostrarLoadingGestion('Importando datos...');
            
            fetch('/api/importar-datos', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(datos)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    let mensaje = `✅ <strong>Datos importados correctamente</strong><br>
                                  📥 <strong>Resumen de importación:</strong><br>`;
                    
                    for (const [categoria, cantidad] of Object.entries(data.resumen)) {
                        const nombre = categoria.replace('_', ' ');
                        mensaje += `• ${cantidad} ${nombre}<br>`;
                    }
                    
                    mensaje += `• <strong>Total: ${data.total} registros</strong><br><br>
                               <button class="btn btn-sm btn-success mt-2" onclick="location.reload()">
                                   <i class="fas fa-sync me-1"></i>Recargar página para ver cambios
                               </button>`;
                    
                    mostrarResultadoGestion('success', mensaje);
                    
                    // Limpiar el input de archivo
                    fileInput.value = '';
                    
                } else {
                    mostrarResultadoGestion('error', `❌ <strong>Error al importar:</strong> ${data.error || 'Error desconocido'}`);
                }
            })
            .catch(error => {
                console.error('Error importando datos:', error);
                mostrarResultadoGestion('error', `❌ <strong>Error de conexión:</strong> ${error.message}`);
            });
            
        } catch (error) {
            console.error('Error procesando archivo:', error);
            mostrarResultadoGestion('error', `❌ <strong>Error en el archivo JSON:</strong> ${error.message}`);
        }
    };
    
    reader.onerror = function() {
        mostrarResultadoGestion('error', '❌ <strong>Error al leer el archivo</strong>');
    };
    
    reader.readAsText(file);
}

function crearBackup() {
    if (!confirm('💾 ¿Crear una copia de seguridad de todos los datos?')) {
        return;
    }
    
    mostrarLoadingGestion('Creando copia de seguridad...');
    
    fetch('/api/backup-datos', { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            mostrarResultadoGestion('success', 
                `💾 <strong>Backup creado correctamente</strong><br>
                 📁 <strong>Archivo:</strong> ${data.backup_file}<br>
                 📊 <strong>Resumen:</strong><br>
                 • ${data.resumen.centros} centros de distribución<br>
                 • ${data.resumen.distribuidores} distribuidores autorizados<br>
                 • ${data.resumen.tiendas_oro} tiendas oro<br>
                 • ${data.resumen.tiendas_satelite} tiendas satélite`);
        } else {
            mostrarResultadoGestion('error', `❌ <strong>Error al crear backup:</strong> ${data.error || 'Error desconocido'}`);
        }
    })
    .catch(error => {
        console.error('Error creando backup:', error);
        mostrarResultadoGestion('error', `❌ <strong>Error de conexión:</strong> ${error.message}`);
    });
}

// Funciones auxiliares para la gestión de datos
function mostrarLoadingGestion(mensaje) {
    document.getElementById('resultadoGestion').innerHTML = 
        `<div class="alert alert-info d-flex align-items-center">
            <i class="fas fa-spinner fa-spin me-2"></i>
            <div>${mensaje}</div>
         </div>`;
}

function mostrarResultadoGestion(tipo, mensaje) {
    const clase = tipo === 'success' ? 'alert-success' : 'alert-danger';
    document.getElementById('resultadoGestion').innerHTML = 
        `<div class="alert ${clase}">
            <div class="d-flex align-items-center">
                <i class="fas fa-${tipo === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                <div>${mensaje}</div>
            </div>
         </div>`;
}

// ============================================================================
// FUNCIONES EXISTENTES DEL PANEL DE MANTENIMIENTO
// ============================================================================

// Navegación del sidebar
document.addEventListener('DOMContentLoaded', function() {
    // Cargar datos iniciales
    cargarCentrosDistribucion();
    cargarDistribuidores();
    cargarTiendasOro();
    cargarTiendasSatelite();
    
    // Navegación del sidebar
    document.querySelectorAll('.nav-link[data-target]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remover active de todos los links
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            // Agregar active al link clickeado
            this.classList.add('active');
            
            // Ocultar todas las secciones
            document.querySelectorAll('.content-section').forEach(section => {
                section.classList.remove('active');
            });
            
            // Mostrar la sección correspondiente
            const target = this.getAttribute('data-target');
            document.getElementById(target).classList.add('active');
        });
    });
});


function cargarCentrosDistribucion() {
    console.log('Cargando centros de distribución...');
    fetch('/api/centros-distribucion')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta de la API');
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos de centros recibidos:', data);
            const tbody = document.getElementById('tbodyCentrosDistribucion');
            if (!tbody) {
                console.error('No se encontró tbodyCentrosDistribucion');
                return;
            }
            
            tbody.innerHTML = '';
            
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="10" class="text-center">No hay centros de distribución registrados</td></tr>';
                return;
            }
            
            data.forEach(centro => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${centro.id}</td>
                    <td>${centro.nombre}</td>
                    <td>${centro.ciudad}</td>
                    <td>${centro.direccion}</td>
                    <td><span class="estado-${centro.estado}">${formatearEstado(centro.estado)}</span></td>
                    <td>${centro.telefono || 'N/A'}</td>
                    <td>${centro.capacidad_almacen || 'N/A'}</td>
                    <td>${centro.tipo_centro || 'N/A'}</td>
                    <td>${formatearFecha(centro.fecha_apertura)}</td>
                    <td class="table-actions">
                        <button class="btn btn-sm btn-warning me-1" onclick="editarCentroDistribucion('${centro.id}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="eliminarCentroDistribucion('${centro.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => {
            console.error('Error cargando centros de distribución:', error);
            const tbody = document.getElementById('tbodyCentrosDistribucion');
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="10" class="text-center text-danger">Error al cargar los datos</td></tr>';
            }
        });
}

function abrirModalCentroDistribucion(centro = null) {
    const modal = new bootstrap.Modal(document.getElementById('modalCentroDistribucion'));
    const form = document.getElementById('formCentroDistribucion');
    form.reset();
    
    if (centro) {
        document.getElementById('modalCentroDistribucionTitle').textContent = 'Editar Centro de Distribución';
        document.getElementById('centroDistribucionId').value = centro.id;
        document.getElementById('centroDistribucionNombre').value = centro.nombre;
        document.getElementById('centroDistribucionCiudad').value = centro.ciudad;
        document.getElementById('centroDistribucionDireccion').value = centro.direccion;
        document.getElementById('centroDistribucionTelefono').value = centro.telefono || '';
        document.getElementById('centroDistribucionCapacidad').value = centro.capacidad_almacen || '';
        document.getElementById('centroDistribucionTipo').value = centro.tipo_centro || 'Principal';
        document.getElementById('centroDistribucionEstado').value = centro.estado;
        document.getElementById('centroDistribucionFechaApertura').value = centro.fecha_apertura || '';
        document.getElementById('centroDistribucionZonaCobertura').value = centro.zona_cobertura || '';
        document.getElementById('centroDistribucionResponsable').value = centro.responsable || '';
        document.getElementById('centroDistribucionCoordenadas').value = `${centro.lat}, ${centro.lon}`;
    } else {
        document.getElementById('modalCentroDistribucionTitle').textContent = 'Nuevo Centro de Distribución';
        document.getElementById('centroDistribucionId').value = '';
        document.getElementById('centroDistribucionFechaApertura').value = new Date().toISOString().split('T')[0];
        document.getElementById('centroDistribucionCoordenadas').value = '';
    }
    
    modal.show();
}

function guardarCentroDistribucion() {
    const form = document.getElementById('formCentroDistribucion');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    // Procesar coordenadas
    const coordenadas = document.getElementById('centroDistribucionCoordenadas').value.split(',');
    if (coordenadas.length !== 2) {
        alert('Formato de coordenadas inválido. Use: latitud, longitud');
        return;
    }

    const lat = parseFloat(coordenadas[0].trim());
    const lon = parseFloat(coordenadas[1].trim());
    
    if (isNaN(lat) || isNaN(lon)) {
        alert('Coordenadas inválidas. Asegúrese de usar números.');
        return;
    }

    const centroData = {
        nombre: document.getElementById('centroDistribucionNombre').value,
        ciudad: document.getElementById('centroDistribucionCiudad').value,
        direccion: document.getElementById('centroDistribucionDireccion').value,
        telefono: document.getElementById('centroDistribucionTelefono').value,
        capacidad_almacen: document.getElementById('centroDistribucionCapacidad').value,
        tipo_centro: document.getElementById('centroDistribucionTipo').value,
        estado: document.getElementById('centroDistribucionEstado').value,
        fecha_apertura: document.getElementById('centroDistribucionFechaApertura').value,
        zona_cobertura: document.getElementById('centroDistribucionZonaCobertura').value,
        responsable: document.getElementById('centroDistribucionResponsable').value,
        lat: lat,
        lon: lon
    };

    const centroId = document.getElementById('centroDistribucionId').value;
    const url = centroId ? `/api/centros-distribucion/${centroId}` : '/api/centros-distribucion';
    const method = centroId ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(centroData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('modalCentroDistribucion')).hide();
            cargarCentrosDistribucion();
            mostrarAlerta('Centro de Distribución guardado exitosamente', 'success');
        } else {
            throw new Error(data.error || 'Error al guardar');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarAlerta('Error al guardar centro de distribución: ' + error.message, 'danger');
    });
}

function editarCentroDistribucion(id) {
    fetch(`/api/centros-distribucion`)
        .then(response => response.json())
        .then(centros => {
            const centro = centros.find(c => c.id === id);
            if (centro) {
                abrirModalCentroDistribucion(centro);
            }
        })
        .catch(error => console.error('Error:', error));
}

function eliminarCentroDistribucion(id) {
    if (confirm('¿Está seguro de que desea eliminar este centro de distribución?')) {
        fetch(`/api/centros-distribucion/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                cargarCentrosDistribucion();
                mostrarAlerta('Centro de Distribución eliminado exitosamente', 'success');
            } else {
                throw new Error(data.error || 'Error al eliminar');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('Error al eliminar centro de distribución: ' + error.message, 'danger');
        });
    }
}

// ============================================================================
// FUNCIONES PARA DISTRIBUIDORES
// ============================================================================

function cargarDistribuidores() {
    console.log('📦 Cargando distribuidores...');
    fetch('/api/distribuidores')
        .then(response => {
            console.log('📡 Respuesta de API distribuidores:', response.status, response.statusText);
            
            if (!response.ok) {
                if (response.status === 401) {
                    throw new Error('No autorizado - Sesión expirada');
                } else if (response.status === 404) {
                    throw new Error('API no encontrada');
                } else {
                    throw new Error(`Error HTTP: ${response.status} ${response.statusText}`);
                }
            }
            return response.json();
        })
        .then(data => {
            console.log('✅ Datos de distribuidores recibidos:', data);
            const tbody = document.getElementById('tbodyDistribuidores');
            if (!tbody) {
                console.error('❌ No se encontró tbodyDistribuidores');
                return;
            }
            
            tbody.innerHTML = '';
            
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" class="text-center">No hay distribuidores registrados</td></tr>';
                return;
            }
            
            data.forEach(distribuidor => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${distribuidor.id}</td>
                    <td>${distribuidor.nombre}</td>
                    <td>${distribuidor.ciudad}</td>
                    <td>${distribuidor.direccion}</td>
                    <td><span class="estado-${distribuidor.estado}">${formatearEstado(distribuidor.estado)}</span></td>
                    <td>${distribuidor.telefono || 'N/A'}</td>
                    <td>${formatearFecha(distribuidor.fecha_apertura)}</td>
                    <td class="table-actions">
                        <button class="btn btn-sm btn-warning me-1" onclick="editarDistribuidor('${distribuidor.id}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="eliminarDistribuidor('${distribuidor.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => {
            console.error('💥 Error cargando distribuidores:', error);
            const tbody = document.getElementById('tbodyDistribuidores');
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="8" class="text-center text-danger">
                            <strong>Error al cargar los datos</strong><br>
                            <small>${error.message}</small>
                        </td>
                    </tr>
                `;
            }
        });
}

function abrirModalDistribuidor(distribuidor = null) {
    const modal = new bootstrap.Modal(document.getElementById('modalDistribuidor'));
    const form = document.getElementById('formDistribuidor');
    form.reset();
    
    if (distribuidor) {
        document.getElementById('modalDistribuidorTitle').textContent = 'Editar Distribuidor';
        document.getElementById('distribuidorId').value = distribuidor.id;
        document.getElementById('distribuidorNombre').value = distribuidor.nombre;
        document.getElementById('distribuidorCiudad').value = distribuidor.ciudad;
        document.getElementById('distribuidorDireccion').value = distribuidor.direccion;
        document.getElementById('distribuidorTelefono').value = distribuidor.telefono || '';
        document.getElementById('distribuidorEstado').value = distribuidor.estado;
        document.getElementById('distribuidorFechaApertura').value = distribuidor.fecha_apertura || '';
        document.getElementById('distribuidorCoordenadas').value = `${distribuidor.lat}, ${distribuidor.lon}`;
    } else {
        document.getElementById('modalDistribuidorTitle').textContent = 'Nuevo Distribuidor';
        document.getElementById('distribuidorId').value = '';
        document.getElementById('distribuidorFechaApertura').value = new Date().toISOString().split('T')[0];
        document.getElementById('distribuidorCoordenadas').value = '';
    }
    
    modal.show();
}

function guardarDistribuidor() {
    const form = document.getElementById('formDistribuidor');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    // Procesar coordenadas
    const coordenadas = document.getElementById('distribuidorCoordenadas').value.split(',');
    if (coordenadas.length !== 2) {
        alert('Formato de coordenadas inválido. Use: latitud, longitud');
        return;
    }

    const lat = parseFloat(coordenadas[0].trim());
    const lon = parseFloat(coordenadas[1].trim());
    
    if (isNaN(lat) || isNaN(lon)) {
        alert('Coordenadas inválidas. Asegúrese de usar números.');
        return;
    }

    const distribuidorData = {
        nombre: document.getElementById('distribuidorNombre').value,
        ciudad: document.getElementById('distribuidorCiudad').value,
        direccion: document.getElementById('distribuidorDireccion').value,
        telefono: document.getElementById('distribuidorTelefono').value,
        estado: document.getElementById('distribuidorEstado').value,
        fecha_apertura: document.getElementById('distribuidorFechaApertura').value,
        lat: lat,
        lon: lon
    };

    const distribuidorId = document.getElementById('distribuidorId').value;
    const url = distribuidorId ? `/api/distribuidores/${distribuidorId}` : '/api/distribuidores';
    const method = distribuidorId ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(distribuidorData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('modalDistribuidor')).hide();
            cargarDistribuidores();
            mostrarAlerta('Distribuidor guardado exitosamente', 'success');
        } else {
            throw new Error(data.error || 'Error al guardar');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarAlerta('Error al guardar distribuidor: ' + error.message, 'danger');
    });
}

// ============================================================================
// FUNCIONES PARA TIENDAS ORO
// ============================================================================

function cargarTiendasOro() {
    fetch('/api/tiendas-oro')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('tbodyTiendasOro');
            tbody.innerHTML = '';
            
            data.forEach(tienda => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${tienda.id}</td>
                    <td>${tienda.nombre}</td>
                    <td>${tienda.ciudad}</td>
                    <td>${tienda.direccion}</td>
                    <td><span class="estado-${tienda.estado}">${formatearEstado(tienda.estado)}</span></td>
                    <td>${tienda.capacidad_congelador || 'N/A'}</td>
                    <td>${formatearFecha(tienda.fecha_apertura)}</td>
                    <td class="table-actions">
                        <button class="btn btn-sm btn-warning me-1" onclick="editarTiendaOro('${tienda.id}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="eliminarTiendaOro('${tienda.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => console.error('Error cargando tiendas oro:', error));
}

function abrirModalTiendaOro(tienda = null) {
    const modal = new bootstrap.Modal(document.getElementById('modalTiendaOro'));
    const form = document.getElementById('formTiendaOro');
    form.reset();
    
    if (tienda) {
        document.getElementById('modalTiendaOroTitle').textContent = 'Editar Tienda Oro';
        document.getElementById('tiendaOroId').value = tienda.id;
        document.getElementById('tiendaOroNombre').value = tienda.nombre;
        document.getElementById('tiendaOroCiudad').value = tienda.ciudad;
        document.getElementById('tiendaOroDireccion').value = tienda.direccion;
        document.getElementById('tiendaOroCapacidad').value = tienda.capacidad_congelador || '';
        document.getElementById('tiendaOroEstado').value = tienda.estado;
        document.getElementById('tiendaOroFechaApertura').value = tienda.fecha_apertura || '';
        document.getElementById('tiendaOroCoordenadas').value = `${tienda.lat}, ${tienda.lon}`;
    } else {
        document.getElementById('modalTiendaOroTitle').textContent = 'Nueva Tienda Oro';
        document.getElementById('tiendaOroId').value = '';
        document.getElementById('tiendaOroFechaApertura').value = new Date().toISOString().split('T')[0];
        document.getElementById('tiendaOroCoordenadas').value = '';
    }
    
    modal.show();
}

function guardarTiendaOro() {
    const form = document.getElementById('formTiendaOro');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    // Procesar coordenadas
    const coordenadas = document.getElementById('tiendaOroCoordenadas').value.split(',');
    if (coordenadas.length !== 2) {
        alert('Formato de coordenadas inválido. Use: latitud, longitud');
        return;
    }

    const lat = parseFloat(coordenadas[0].trim());
    const lon = parseFloat(coordenadas[1].trim());
    
    if (isNaN(lat) || isNaN(lon)) {
        alert('Coordenadas inválidas. Asegúrese de usar números.');
        return;
    }

    const tiendaData = {
        nombre: document.getElementById('tiendaOroNombre').value,
        ciudad: document.getElementById('tiendaOroCiudad').value,
        direccion: document.getElementById('tiendaOroDireccion').value,
        capacidad_congelador: document.getElementById('tiendaOroCapacidad').value,
        estado: document.getElementById('tiendaOroEstado').value,
        fecha_apertura: document.getElementById('tiendaOroFechaApertura').value,
        lat: lat,
        lon: lon
    };

    const tiendaId = document.getElementById('tiendaOroId').value;
    const url = tiendaId ? `/api/tiendas-oro/${tiendaId}` : '/api/tiendas-oro';
    const method = tiendaId ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(tiendaData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('modalTiendaOro')).hide();
            cargarTiendasOro();
            mostrarAlerta('Tienda Oro guardada exitosamente', 'success');
        } else {
            throw new Error(data.error || 'Error al guardar');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarAlerta('Error al guardar tienda oro: ' + error.message, 'danger');
    });
}

// ============================================================================
// FUNCIONES PARA TIENDAS SATÉLITE
// ============================================================================

function cargarTiendasSatelite() {
    fetch('/api/tiendas-satelite')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('tbodyTiendasSatelite');
            tbody.innerHTML = '';
            
            data.forEach(tienda => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${tienda.id}</td>
                    <td>${tienda.nombre}</td>
                    <td>${tienda.ciudad}</td>
                    <td>${tienda.direccion}</td>
                    <td><span class="estado-${tienda.estado}">${formatearEstado(tienda.estado)}</span></td>
                    <td>${tienda.tipo_satelite || 'N/A'}</td>
                    <td>${formatearFecha(tienda.fecha_apertura)}</td>
                    <td class="table-actions">
                        <button class="btn btn-sm btn-warning me-1" onclick="editarTiendaSatelite('${tienda.id}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="eliminarTiendaSatelite('${tienda.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => console.error('Error cargando tiendas satélite:', error));
}

function abrirModalTiendaSatelite(tienda = null) {
    const modal = new bootstrap.Modal(document.getElementById('modalTiendaSatelite'));
    const form = document.getElementById('formTiendaSatelite');
    form.reset();
    
    if (tienda) {
        document.getElementById('modalTiendaSateliteTitle').textContent = 'Editar Tienda Satélite';
        document.getElementById('tiendaSateliteId').value = tienda.id;
        document.getElementById('tiendaSateliteNombre').value = tienda.nombre;
        document.getElementById('tiendaSateliteCiudad').value = tienda.ciudad;
        document.getElementById('tiendaSateliteDireccion').value = tienda.direccion;
        document.getElementById('tiendaSateliteTipo').value = tienda.tipo_satelite || '';
        document.getElementById('tiendaSateliteEstado').value = tienda.estado;
        document.getElementById('tiendaSateliteFechaApertura').value = tienda.fecha_apertura || '';
        document.getElementById('tiendaSateliteCoordenadas').value = `${tienda.lat}, ${tienda.lon}`;
    } else {
        document.getElementById('modalTiendaSateliteTitle').textContent = 'Nueva Tienda Satélite';
        document.getElementById('tiendaSateliteId').value = '';
        document.getElementById('tiendaSateliteFechaApertura').value = new Date().toISOString().split('T')[0];
        document.getElementById('tiendaSateliteCoordenadas').value = '';
    }
    
    modal.show();
}

function guardarTiendaSatelite() {
    const form = document.getElementById('formTiendaSatelite');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    // Procesar coordenadas
    const coordenadas = document.getElementById('tiendaSateliteCoordenadas').value.split(',');
    if (coordenadas.length !== 2) {
        alert('Formato de coordenadas inválido. Use: latitud, longitud');
        return;
    }

    const lat = parseFloat(coordenadas[0].trim());
    const lon = parseFloat(coordenadas[1].trim());
    
    if (isNaN(lat) || isNaN(lon)) {
        alert('Coordenadas inválidas. Asegúrese de usar números.');
        return;
    }

    const tiendaData = {
        nombre: document.getElementById('tiendaSateliteNombre').value,
        ciudad: document.getElementById('tiendaSateliteCiudad').value,
        direccion: document.getElementById('tiendaSateliteDireccion').value,
        tipo_satelite: document.getElementById('tiendaSateliteTipo').value,
        estado: document.getElementById('tiendaSateliteEstado').value,
        fecha_apertura: document.getElementById('tiendaSateliteFechaApertura').value,
        lat: lat,
        lon: lon
    };

    const tiendaId = document.getElementById('tiendaSateliteId').value;
    const url = tiendaId ? `/api/tiendas-satelite/${tiendaId}` : '/api/tiendas-satelite';
    const method = tiendaId ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(tiendaData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('modalTiendaSatelite')).hide();
            cargarTiendasSatelite();
            mostrarAlerta('Tienda Satélite guardada exitosamente', 'success');
        } else {
            throw new Error(data.error || 'Error al guardar');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarAlerta('Error al guardar tienda satélite: ' + error.message, 'danger');
    });
}

// ============================================================================
// FUNCIONES UTILITARIAS
// ============================================================================

function formatearEstado(estado) {
    const estados = {
        'activo': 'Activo',
        'planeado': 'Planeado',
        'proxima_apertura': 'Próxima Apertura',
        'en_construccion': 'En Construcción'
    };
    return estados[estado] || estado;
}

function formatearFecha(fecha) {
    if (!fecha) return 'N/A';
    const date = new Date(fecha);
    return date.toLocaleDateString('es-ES');
}

function mostrarAlerta(mensaje, tipo) {
    const alerta = document.createElement('div');
    alerta.className = `alert alert-${tipo} alert-dismissible fade show position-fixed`;
    alerta.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alerta.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alerta);
    
    setTimeout(() => {
        if (alerta.parentNode) {
            alerta.parentNode.removeChild(alerta);
        }
    }, 5000);
}

// ============================================================================
// FUNCIONES DE EDICIÓN Y ELIMINACIÓN
// ============================================================================

function editarCentroDistribucion(id) {
    fetch(`/api/centros-distribucion`)
        .then(response => response.json())
        .then(centros => {
            const centro = centros.find(c => c.id === id);
            if (centro) {
                abrirModalCentroDistribucion(centro);
            }
        })
        .catch(error => console.error('Error:', error));
}

function eliminarCentroDistribucion(id) {
    if (confirm('¿Está seguro de que desea eliminar este centro de distribución?')) {
        fetch(`/api/centros-distribucion/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                cargarCentrosDistribucion();
                mostrarAlerta('Centro de Distribución eliminado exitosamente', 'success');
            } else {
                throw new Error(data.error || 'Error al eliminar');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('Error al eliminar centro de distribución: ' + error.message, 'danger');
        });
    }
}

function editarDistribuidor(id) {
    fetch(`/api/distribuidores`)
        .then(response => response.json())
        .then(distribuidores => {
            const distribuidor = distribuidores.find(d => d.id === id);
            if (distribuidor) {
                abrirModalDistribuidor(distribuidor);
            }
        })
        .catch(error => console.error('Error:', error));
}

function eliminarDistribuidor(id) {
    if (confirm('¿Está seguro de que desea eliminar este distribuidor?')) {
        fetch(`/api/distribuidores/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                cargarDistribuidores();
                mostrarAlerta('Distribuidor eliminado exitosamente', 'success');
            } else {
                throw new Error(data.error || 'Error al eliminar');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('Error al eliminar distribuidor: ' + error.message, 'danger');
        });
    }
}

function editarTiendaOro(id) {
    fetch(`/api/tiendas-oro`)
        .then(response => response.json())
        .then(tiendas => {
            const tienda = tiendas.find(t => t.id === id);
            if (tienda) {
                abrirModalTiendaOro(tienda);
            }
        })
        .catch(error => console.error('Error:', error));
}

function eliminarTiendaOro(id) {
    if (confirm('¿Está seguro de que desea eliminar esta tienda oro?')) {
        fetch(`/api/tiendas-oro/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                cargarTiendasOro();
                mostrarAlerta('Tienda Oro eliminada exitosamente', 'success');
            } else {
                throw new Error(data.error || 'Error al eliminar');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('Error al eliminar tienda oro: ' + error.message, 'danger');
        });
    }
}

function editarTiendaSatelite(id) {
    fetch(`/api/tiendas-satelite`)
        .then(response => response.json())
        .then(tiendas => {
            const tienda = tiendas.find(t => t.id === id);
            if (tienda) {
                abrirModalTiendaSatelite(tienda);
            }
        })
        .catch(error => console.error('Error:', error));
}

function eliminarTiendaSatelite(id) {
    if (confirm('¿Está seguro de que desea eliminar esta tienda satélite?')) {
        fetch(`/api/tiendas-satelite/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                cargarTiendasSatelite();
                mostrarAlerta('Tienda Satélite eliminada exitosamente', 'success');
            } else {
                throw new Error(data.error || 'Error al eliminar');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('Error al eliminar tienda satélite: ' + error.message, 'danger');
        });
    }
}