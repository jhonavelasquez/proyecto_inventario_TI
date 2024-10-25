$(document).ready(function () {
    $('#updateForm form').on('submit', function (event) {
        event.preventDefault();

        const fields = [
            { id: 'email_user', name: 'Correo electrónico', validate: validateEmail },
            { id: 'psw', name: 'Contraseña', validate: (val) => val.trim() !== '' },
            { id: 'psw_confirm', name: 'Confirmar contraseña', validate: (val) => val.trim() !== '' },
        ];

        let errors = [];

        fields.forEach(field => {
            const value = $(`#${field.id}`).val(); // Sin trim aquí para mantener los espacios
            if (!field.validate(value)) {
                errors.push(`El campo "${field.name}" es inválido o está vacío.`);
            }
        });

        const emailValue = $('#email_user').val(); // Sin trim aquí para verificar espacios
        if (emailValue.trim() === '') {
            errors.push('El campo "Correo electrónico" no puede estar vacío.');
        } else if (emailValue !== emailValue.trim()) {
            // Comprobar si hay espacios al inicio o al final
            errors.push('El campo "Correo electrónico" no puede tener espacios al inicio o al final.');
        }

        if ($('#psw').val().trim() !== $('#psw_confirm').val().trim()) {
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
});
