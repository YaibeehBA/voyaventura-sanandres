function confirmarEliminacion(mensajeId, event) {
    event.preventDefault();
    Swal.fire({
        title: '¿Estás seguro?',
        text: "¿Quieres eliminar este mensaje?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = '/admin/userauths/mensajeusuario/eliminar/' + mensajeId + '/';
        }
    });
}