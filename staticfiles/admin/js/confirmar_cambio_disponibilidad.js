function confirmarCambioDisponibilidad(habitacionId, event) {
    event.preventDefault();
    Swal.fire({
        title: '¿Estás seguro?',
        text: "¿Quieres hacer esta habitación disponible?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, hacer disponible',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = '/admin/alojamiento/habitacion/cambiar_disponibilidad/' + habitacionId + '/';
        }
    });
}