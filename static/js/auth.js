/*
  Tiny JS glue to mimic the React state from the original.
  Nothing server-side, nothing fancy. Humans love fancy and then wonder why it breaks.
*/

// Password visibility toggles
function initPasswordToggles() {
  document.querySelectorAll('[data-toggle-password]')
    .forEach((btn) => {
      btn.addEventListener('click', () => {
        const id = btn.getAttribute('data-toggle-password');
        const input = document.getElementById(id);
        if (!input) return;
        input.type = input.type === 'password' ? 'text' : 'password';
        btn.setAttribute('aria-pressed', input.type === 'text' ? 'true' : 'false');
      });
    });
}

// Remember me (fake checkbox)
function initRememberMe() {
  const remember = document.querySelector('[data-remember]');
  if (!remember) return;

  const setChecked = (v) => {
    remember.setAttribute('data-checked', v ? 'true' : 'false');
    remember.setAttribute('aria-pressed', v ? 'true' : 'false');
    const hidden = document.querySelector('input[name="remember"]');
    if (hidden) hidden.value = v ? '1' : '0';
  };

  const initial = remember.getAttribute('data-checked') !== 'false';
  setChecked(initial);

  remember.addEventListener('click', () => {
    const cur = remember.getAttribute('data-checked') === 'true';
    setChecked(!cur);
  });
}

// 4-digit verification code input
function initCodeInputs() {
  const wrap = document.querySelector('[data-code-wrap]');
  if (!wrap) return;

  const inputs = Array.from(wrap.querySelectorAll('input[data-code]'));
  const submit = document.querySelector('button[type="submit"][data-code-submit]');
  const optional = wrap.hasAttribute('data-code-optional');

  const updateSubmit = () => {
    if (optional) {
      if (submit) submit.disabled = false;
      return;
    }
    const ok = inputs.every((i) => i.value.trim() !== '');
    if (submit) submit.disabled = !ok;
  };

  const focusIndex = (idx) => {
    const el = inputs[idx];
    if (el) el.focus();
  };

  inputs.forEach((input, idx) => {
    input.addEventListener('input', (e) => {
      // Keep only digits
      input.value = input.value.replace(/\D/g, '').slice(0, 1);
      if (input.value && idx < inputs.length - 1) focusIndex(idx + 1);
      updateSubmit();
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Backspace' && !input.value && idx > 0) {
        focusIndex(idx - 1);
      }
      if (e.key === 'ArrowLeft' && idx > 0) {
        e.preventDefault();
        focusIndex(idx - 1);
      }
      if (e.key === 'ArrowRight' && idx < inputs.length - 1) {
        e.preventDefault();
        focusIndex(idx + 1);
      }
    });

    input.addEventListener('paste', (e) => {
      const text = (e.clipboardData || window.clipboardData).getData('text');
      const digits = (text || '').replace(/\D/g, '').slice(0, inputs.length);
      if (!digits) return;
      e.preventDefault();
      digits.split('').forEach((d, i) => {
        if (inputs[i]) inputs[i].value = d;
      });
      updateSubmit();
      focusIndex(Math.min(digits.length, inputs.length - 1));
    });
  });

  updateSubmit();

  // Resend
  const resend = document.querySelector('[data-resend]');
  if (resend) {
    resend.addEventListener('click', () => {
      inputs.forEach((i) => (i.value = ''));
      updateSubmit();
      focusIndex(0);
    });
  }
}

// Prevent dummy forms from actually submitting anywhere.
function initNoopForms() {
  document.querySelectorAll('form[data-noop]')
    .forEach((form) => form.addEventListener('submit', (e) => e.preventDefault()));
}

function initForgotMethodToggle() {
  const btn = document.querySelector('[data-toggle-forgot-method]');
  if (!btn) return;
  const phoneWrap = document.querySelector('[data-forgot-phone]');
  const emailWrap = document.querySelector('[data-forgot-email]');
  const phoneInput = phoneWrap ? phoneWrap.querySelector('input') : null;
  const emailInput = emailWrap ? emailWrap.querySelector('input') : null;

  let useEmail = true; // backend требует email; включаем email по умолчанию
  const apply = () => {
    if (phoneWrap) phoneWrap.style.display = useEmail ? 'none' : 'flex';
    if (emailWrap) emailWrap.style.display = useEmail ? 'flex' : 'none';
    if (phoneInput) {
      phoneInput.required = !useEmail;
      phoneInput.name = useEmail ? '' : 'email';
    }
    if (emailInput) {
      emailInput.required = useEmail;
      emailInput.name = useEmail ? 'email' : '';
    }
  };

  btn.addEventListener('click', () => {
    useEmail = !useEmail;
    apply();
  });

  apply();
}

function initRedirectForms() {
  document.querySelectorAll("form[data-redirect]").forEach((form) => {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const btn = form.querySelector("button[type=submit]");
      if (btn && btn.disabled) return;
      const target = form.getAttribute("data-redirect");
      if (target) window.location.href = target;
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initPasswordToggles();
  initRememberMe();
  initCodeInputs();
  initForgotMethodToggle();
  initRedirectForms();
  initNoopForms();
});
