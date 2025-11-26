// Navegación entre secciones
document.addEventListener('DOMContentLoaded', function() {
    // Navegación del sidebar
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.getAttribute('data-target')) {
                e.preventDefault();
                
                // Remover active de todos los links
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                // Agregar active al link clickeado
                this.classList.add('active');
                
                // Ocultar todas las secciones
                document.querySelectorAll('.content-section').forEach(section => {
                    section.classList.remove('active');
                });
                
                // Mostrar sección correspondiente
                const target = this.getAttribute('data-target');
                document.getElementById(target).classList.add('active');
                
                // Cargar datos si es necesario
                if (target === 'distribuidores') cargarDistribuidores();
                else if (target === 'tiendas-oro') cargarTiendasOro();
                else if (target === 'tiendas-satelite') cargarTiendasSatelite();
            }
        });
    });

    // Cargar datos iniciales
    cargarDistribuidores();
});

// ============================================================================
// FUNCIONES PARA DISTRIBUIDORES (ACTUALIZADAS)
// ============================================================================

function cargarDistribuidores() {
    fetch('/api/distribuidores')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('tbodyDistribuidores');
            tbody.innerHTML = '';
            
            data.forEach(distribuidor => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${distribuidor.id}</td>
                    <td>${distribuidor.nombre}</td>
                    <td>${distribuidor.ciudad}</td>
                    <td>${distribuidor.direccion}</td>
                    <td><span class="estado-${distribuidor.estado}">${formatearEstado(distribuidor.estado)}</span></td>
                    <td>${distribuidor.telefono || 'N/A'}</td>
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
        .catch(error => console.error('Error cargando distribuidores:', error));
}

function abrirModalDistribuidor(distribuidor = null) {
    const modal = new bootstrap.Modal(document.getElementById('modalDistribuidor'));
    
    if (distribuidor) {
        // Modo edición
        document.getElementById('modalDistribuidorTitle').textContent = 'Editar Distribuidor';
        document.getElementById('distribuidorId').value = distribuidor.id;
        document.getElementById('distribuidorNombre').value = distribuidor.nombre;
        document.getElementById('distribuidorCiudad').value = distribuidor.ciudad;
        document.getElementById('distribuidorDireccion').value = distribuidor.direccion;
        document.getElementById('distribuidorTelefono').value = distribuidor.telefono || '';
        document.getElementById('distribuidorEstado').value = distribuidor.estado;
        // COORDENADAS EN UNA LÍNEA
        document.getElementById('distribuidorCoordenadas').value = `${distribuidor.lat}, ${distribuidor.lon}`;
    } else {
        // Modo nuevo
        document.getElementById('modalDistribuidorTitle').textContent = 'Nuevo Distribuidor';
        document.getElementById('formDistribuidor').reset();
        document.getElementById('distribuidorId').value = '';
    }
    
    modal.show();
}

function editarDistribuidor(id) {
    fetch('/api/distribuidores')
        .then(response => response.json())
        .then(distribuidores => {
            const distribuidor = distribuidores.find(d => d.id === id);
            if (distribuidor) {
                abrirModalDistribuidor(distribuidor);
            }
        });
}

function guardarDistribuidor() {
    // Procesar coordenadas
    const coordenadasInput = document.getElementById('distribuidorCoordenadas').value;
    const coordenadas = coordenadasInput.split(',');
    
    if (coordenadas.length !== 2) {
        mostrarAlerta('Formato de coordenadas inválido. Use: latitud, longitud', 'danger');
        return;
    }

    const lat = parseFloat(coordenadas[0].trim());
    const lon = parseFloat(coordenadas[1].trim());

    if (isNaN(lat) || isNaN(lon)) {
        mostrarAlerta('Las coordenadas deben ser números válidos', 'danger');
        return;
    }

    const id = document.getElementById('distribuidorId').value;
    
    // Construir formData incluyendo el ID cuando esté en modo edición
    const formData = {
        nombre: document.getElementById('distribuidorNombre').value,
        ciudad: document.getElementById('distribuidorCiudad').value,
        direccion: document.getElementById('distribuidorDireccion').value,
        telefono: document.getElementById('distribuidorTelefono').value,
        estado: document.getElementById('distribuidorEstado').value,
        lat: lat,
        lon: lon
    };

    // INCLUIR EL ID EN LOS DATOS CUANDO SEA EDICIÓN
    if (id) {
        formData.id = id;
    }

    const url = id ? `/api/distribuidores/${id}` : '/api/distribuidores';
    const method = id ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('modalDistribuidor')).hide();
            cargarDistribuidores();
            mostrarAlerta('Distribuidor guardado exitosamente', 'success');
        } else {
            mostrarAlerta('Error al guardar: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarAlerta('Error al guardar', 'danger');
    });
}

function eliminarDistribuidor(id) {
    if (confirm('¿Estás seguro de que quieres eliminar este distribuidor?')) {
        fetch(`/api/distribuidores/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                cargarDistribuidores();
                mostrarAlerta('Distribuidor eliminado exitosamente', 'success');
            } else {
                mostrarAlerta('Error al eliminar: ' + data.error, 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarAlerta('Error al eliminar', 'danger');
        });
    }
}

// ============================================================================
// FUNCIONES PARA TIENDAS ORO (ACTUALIZADAS)
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
        });
}

function abrirModalTiendaOro(tienda = null) {
    const modal = new bootstrap.Modal(document.getElementById('modalTiendaOro'));
    
    if (tienda) {
        document.getElementById('modalTiendaOroTitle').textContent = 'Editar Tienda Oro';
        document.getElementById('tiendaOroId').value = tienda.id;
        document.getElementById('tiendaOroNombre').value = tienda.nombre;
        document.getElementById('tiendaOroCiudad').value = tienda.ciudad;
        document.getElementById('tiendaOroDireccion').value = tienda.direccion;
        document.getElementById('tiendaOroCapacidad').value = tienda.capacidad_congelador || '';
        document.getElementById('tiendaOroEstado').value = tienda.estado;
        // COORDENADAS EN UNA LÍNEA
        document.getElementById('tiendaOroCoordenadas').value = `${tienda.lat}, ${tienda.lon}`;
    } else {
        document.getElementById('modalTiendaOroTitle').textContent = 'Nueva Tienda Oro';
        document.getElementById('formTiendaOro').reset();
        document.getElementById('tiendaOroId').value = '';
    }
    
    modal.show();
}

function editarTiendaOro(id) {
    fetch('/api/tiendas-oro')
        .then(response => response.json())
        .then(tiendas => {
            const tienda = tiendas.find(t => t.id === id);
            if (tienda) abrirModalTiendaOro(tienda);
        });
}

function guardarTiendaOro() {
    // Procesar coordenadas
    const coordenadasInput = document.getElementById('tiendaOroCoordenadas').value;
    const coordenadas = coordenadasInput.split(',');
    
    if (coordenadas.length !== 2) {
        mostrarAlerta('Formato de coordenadas inválido. Use: latitud, longitud', 'danger');
        return;
    }

    const lat = parseFloat(coordenadas[0].trim());
    const lon = parseFloat(coordenadas[1].trim());

    if (isNaN(lat) || isNaN(lon)) {
        mostrarAlerta('Las coordenadas deben ser números válidos', 'danger');
        return;
    }

    const id = document.getElementById('tiendaOroId').value;
    
    const formData = {
        nombre: document.getElementById('tiendaOroNombre').value,
        ciudad: document.getElementById('tiendaOroCiudad').value,
        direccion: document.getElementById('tiendaOroDireccion').value,
        capacidad_congelador: document.getElementById('tiendaOroCapacidad').value,
        estado: document.getElementById('tiendaOroEstado').value,
        lat: lat,
        lon: lon
    };

    // INCLUIR EL ID EN LOS DATOS CUANDO SEA EDICIÓN
    if (id) {
        formData.id = id;
    }

    const url = id ? `/api/tiendas-oro/${id}` : '/api/tiendas-oro';
    const method = id ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('modalTiendaOro')).hide();
            cargarTiendasOro();
            mostrarAlerta('Tienda Oro guardada exitosamente', 'success');
        } else {
            mostrarAlerta('Error al guardar: ' + data.error, 'danger');
        }
    });
}

function eliminarTiendaOro(id) {
    if (confirm('¿Estás seguro de que quieres eliminar esta tienda oro?')) {
        fetch(`/api/tiendas-oro/${id}`, {method: 'DELETE'})
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                cargarTiendasOro();
                mostrarAlerta('Tienda Oro eliminada exitosamente', 'success');
            } else {
                mostrarAlerta('Error al eliminar: ' + data.error, 'danger');
            }
        });
    }
}

// ============================================================================
// FUNCIONES PARA TIENDAS SATÉLITE (ACTUALIZADAS)
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
        });
}

function abrirModalTiendaSatelite(tienda = null) {
    const modal = new bootstrap.Modal(document.getElementById('modalTiendaSatelite'));
    
    if (tienda) {
        document.getElementById('modalTiendaSateliteTitle').textContent = 'Editar Tienda Satélite';
        document.getElementById('tiendaSateliteId').value = tienda.id;
        document.getElementById('tiendaSateliteNombre').value = tienda.nombre;
        document.getElementById('tiendaSateliteCiudad').value = tienda.ciudad;
        document.getElementById('tiendaSateliteDireccion').value = tienda.direccion;
        document.getElementById('tiendaSateliteTipo').value = tienda.tipo_satelite || '';
        document.getElementById('tiendaSateliteEstado').value = tienda.estado;
        // COORDENADAS EN UNA LÍNEA
        document.getElementById('tiendaSateliteCoordenadas').value = `${tienda.lat}, ${tienda.lon}`;
    } else {
        document.getElementById('modalTiendaSateliteTitle').textContent = 'Nueva Tienda Satélite';
        document.getElementById('formTiendaSatelite').reset();
        document.getElementById('tiendaSateliteId').value = '';
    }
    
    modal.show();
}

function editarTiendaSatelite(id) {
    fetch('/api/tiendas-satelite')
        .then(response => response.json())
        .then(tiendas => {
            const tienda = tiendas.find(t => t.id === id);
            if (tienda) abrirModalTiendaSatelite(tienda);
        });
}

function guardarTiendaSatelite() {
    // Procesar coordenadas
    const coordenadasInput = document.getElementById('tiendaSateliteCoordenadas').value;
    const coordenadas = coordenadasInput.split(',');
    
    if (coordenadas.length !== 2) {
        mostrarAlerta('Formato de coordenadas inválido. Use: latitud, longitud', 'danger');
        return;
    }

    const lat = parseFloat(coordenadas[0].trim());
    const lon = parseFloat(coordenadas[1].trim());

    if (isNaN(lat) || isNaN(lon)) {
        mostrarAlerta('Las coordenadas deben ser números válidos', 'danger');
        return;
    }

    const id = document.getElementById('tiendaSateliteId').value;
    
    const formData = {
        nombre: document.getElementById('tiendaSateliteNombre').value,
        ciudad: document.getElementById('tiendaSateliteCiudad').value,
        direccion: document.getElementById('tiendaSateliteDireccion').value,
        tipo_satelite: document.getElementById('tiendaSateliteTipo').value,
        estado: document.getElementById('tiendaSateliteEstado').value,
        lat: lat,
        lon: lon
    };

    // INCLUIR EL ID EN LOS DATOS CUANDO SEA EDICIÓN
    if (id) {
        formData.id = id;
    }

    const url = id ? `/api/tiendas-satelite/${id}` : '/api/tiendas-satelite';
    const method = id ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('modalTiendaSatelite')).hide();
            cargarTiendasSatelite();
            mostrarAlerta('Tienda Satélite guardada exitosamente', 'success');
        } else {
            mostrarAlerta('Error al guardar: ' + data.error, 'danger');
        }
    });
}
function eliminarTiendaSatelite(id) {
    if (confirm('¿Estás seguro de que quieres eliminar esta tienda satélite?')) {
        fetch(`/api/tiendas-satelite/${id}`, {method: 'DELETE'})
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                cargarTiendasSatelite();
                mostrarAlerta('Tienda Satélite eliminada exitosamente', 'success');
            } else {
                mostrarAlerta('Error al eliminar: ' + data.error, 'danger');
            }
        });
    }
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

function mostrarAlerta(mensaje, tipo) {
    // Crear alerta temporal
    const alerta = document.createElement('div');
    alerta.className = `alert alert-${tipo} alert-dismissible fade show`;
    alerta.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    alerta.style.position = 'fixed';
    alerta.style.top = '20px';
    alerta.style.right = '20px';
    alerta.style.zIndex = '9999';
    alerta.style.minWidth = '300px';
    
    document.body.appendChild(alerta);
    
    // Auto-eliminar después de 5 segundos
    setTimeout(() => {
        if (alerta.parentNode) {
            alerta.parentNode.removeChild(alerta);
        }
    }, 5000);
}