$(document).ready(function () {

    
    const form = $('#formAgregarSistema');
    const nombreSistemaInput = $('#nombre_sistema');
    const errorContainer = $('#modalErrorContainer');
    const charCountDisplay = $('#charCount');

    nombreSistemaInput.on('input', function() {
        const charCount = $(this).val().length;
        charCountDisplay.text(`Caracteres: ${charCount}/90`);
        
        if (charCount > 90) {
            charCountDisplay.removeClass('text-muted').addClass('text-danger');
        } else {
            charCountDisplay.removeClass('text-danger').addClass('text-muted');
        }
    });

    form.on('submit', function (event) {
        event.preventDefault();

        const nombreSistema = nombreSistemaInput.val().trim();
        let errors = [];

        if (nombreSistema === '') {
            errors.push('El nombre del sistema no puede estar vacío o contener solo espacios.');
        }
        if (nombreSistema.length > 90) {
            errors.push('El nombre del sistema no puede exceder los 90 caracteres.');
        }
        if (!/^[a-zA-Z0-9\s]+$/.test(nombreSistema)) {
            errors.push('El nombre del sistema solo puede contener letras, números y espacios.');
        }

        if (errors.length > 0) {
            errorContainer.removeClass('d-none').html(errors.join('<br>'));
        } else {
            errorContainer.addClass('d-none');
            this.submit();
        }
    });

    $('#agregarSistema').on('hidden.bs.modal', function () {
        errorContainer.addClass('d-none').empty();
        nombreSistemaInput.val('');
        charCountDisplay.text('Caracteres: 0/90').removeClass('text-danger').addClass('text-muted');
    });
});


function showDeleteConfirmation() {
    var selectedSystem = document.getElementById('sistema-eliminar').value;
    if (selectedSystem) {
        var deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
        deleteModal.show();
    } else {
        alert('Por favor, seleccione un sistema para eliminar.');
    }
}

function confirmDelete() {
    document.getElementById('deleteForm').submit();
}

document.addEventListener('DOMContentLoaded', function () {
    var deleteModal = document.getElementById('deleteModal');
    deleteModal.addEventListener('hidden.bs.modal', function () {
        var eliminarSistemaModal = bootstrap.Modal.getInstance(document.getElementById('ModelEliminarSistema'));
        eliminarSistemaModal.show();
    });
});