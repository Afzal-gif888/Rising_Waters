document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('[data-validate-form]');
  if (!form) {
    return;
  }

  const fields = Array.from(form.querySelectorAll('input, select'));

  const validateField = (field) => {
    const value = field.value.trim();
    const isRequired = field.hasAttribute('required');
    const min = field.getAttribute('min');
    const max = field.getAttribute('max');
    const numeric = field.type === 'number';
    let valid = true;

    if (isRequired && !value) {
      valid = false;
    }

    if (numeric && value) {
      const parsedValue = Number(value);
      if (Number.isNaN(parsedValue)) {
        valid = false;
      } else {
        if (min !== null && parsedValue < Number(min)) {
          valid = false;
        }
        if (max !== null && parsedValue > Number(max)) {
          valid = false;
        }
      }
    }

    field.classList.toggle('is-invalid', !valid);
    field.classList.toggle('is-valid', valid && value !== '');
    return valid;
  };

  fields.forEach((field) => {
    field.addEventListener('input', () => validateField(field));
    field.addEventListener('change', () => validateField(field));
  });

  form.addEventListener('submit', (event) => {
    let isValid = true;
    fields.forEach((field) => {
      if (!validateField(field)) {
        isValid = false;
      }
    });

    if (!isValid) {
      event.preventDefault();
      form.classList.add('was-validated');
      return;
    }

    const button = form.querySelector('button[type="submit"]');
    const status = form.querySelector('[data-loading-status]');
    if (button) {
      button.disabled = true;
      button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Analyzing...';
    }
    if (status) {
      status.hidden = false;
    }
  });
});
