$(document).ready(function () {
    const passwordFields = [
        { field: $('#psw'), toggle: $('#togglePassword') },
        { field: $('#psw_confirm'), toggle: $('#togglePassword2') }
    ];

    function togglePasswordVisibility(field, toggle) {
        const type = field.attr('type') === 'password' ? 'text' : 'password';
        field.attr('type', type);
        toggle.find('i').toggleClass('bi-eye bi-eye-slash');
    }

    passwordFields.forEach(({ field, toggle }) => {
        toggle.on('click', () => togglePasswordVisibility(field, toggle));
    });

    $('#ModalAgregarUsuario form').on('submit', function (event) {
        event.preventDefault();

        const fields = [
            { id: 'userName', name: 'Nombre de usuario', validate: (val) => val.trim() !== '' },
            { id: 'email_user', name: 'Correo electrónico', validate: validateEmail },
            { id: 'psw', name: 'Contraseña', validate: (val) => val !== '' },
            { id: 'psw_confirm', name: 'Confirmar contraseña', validate: (val) => val !== '' },
            { id: 'computador', name: 'Computador', validate: (val) => val !== '' },
            { id: 'tipo_usuario', name: 'Tipo de usuario', validate: (val) => val !== '' }
        ];

        let errors = [];

        fields.forEach(field => {
            const value = $(`#${field.id}`).val();
            if (!field.validate(value)) {
                errors.push(`El campo "${field.name}" es inválido o está vacío.`);
            }
        });

        if ($('#psw').val() !== $('#psw_confirm').val()) {
            errors.push('Las contraseñas no coinciden.');
        }

        if (errors.length > 0) {
            showModalErrors(errors);
        } else {
            this.submit();
        }
    });

    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    }

    function showModalErrors(errors) {
        const errorContainer = $('#modalErrorContainer');
        errorContainer.empty().removeClass('d-none');

        const errorList = $('<ul class="mb-0"></ul>');
        errors.forEach(error => {
            errorList.append(`<li>${error}</li>`);
        });

        errorContainer.append(errorList);
    }

    $('#ModalAgregarUsuario').on('hidden.bs.modal', function () {
        $('#modalErrorContainer').addClass('d-none').empty();
    });
});