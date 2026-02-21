(function () {
  'use strict';

  const API_BASE = 'https://guided-component-architect-g336.onrender.com';

  const el = {
    prompt: document.getElementById('prompt'),
    generateBtn: document.getElementById('generateBtn'),
    btnText: document.getElementById('btnText'),
    btnSpinner: document.getElementById('btnSpinner'),
    resultSection: document.getElementById('resultSection'),
    previewFrame: document.getElementById('previewFrame'),
    downloadTsx: document.getElementById('downloadTsx'),
    downloadZip: document.getElementById('downloadZip'),
    toast: document.getElementById('toast'),
    toastMessage: document.getElementById('toastMessage'),
  };

  function setLoading(loading) {
    el.generateBtn.disabled = loading;
    el.prompt.disabled = loading;
    el.btnText.textContent = loading ? 'Generating…' : 'Generate';
    el.btnSpinner.classList.toggle('hidden', !loading);
  }

  function showToast(message) {
    el.toastMessage.textContent = message;
    el.toast.classList.remove('hidden');
    el.toast.classList.add('show');
    setTimeout(function () {
      el.toast.classList.remove('show');
      setTimeout(function () {
        el.toast.classList.add('hidden');
      }, 300);
    }, 4000);
  }

  function showResult(data) {
    var previewUrl = API_BASE + data.preview_url;
    var tsxUrl = API_BASE + data.export_tsx_url;
    var zipUrl = API_BASE + data.export_zip_url;

    el.previewFrame.src = previewUrl;
    el.downloadTsx.href = tsxUrl;
    el.downloadTsx.download = 'component.tsx';
    el.downloadZip.href = zipUrl;
    el.downloadZip.download = 'component.zip';

    el.resultSection.classList.remove('hidden');
  }

  function onGenerate() {
    var promptText = (el.prompt.value || '').trim();
    if (!promptText) {
      showToast('Please describe your component.');
      return;
    }

    setLoading(true);

    fetch(API_BASE + '/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: promptText,
        session_id: 'demo',
      }),
    })
      .then(function (res) {
        if (!res.ok) {
          return res.json()
            .then(function (body) {
              var msg = (body && body.detail)
                ? (typeof body.detail === 'string' ? body.detail : (body.detail.message || 'Request failed'))
                : 'Request failed';
              throw new Error(msg);
            })
            .catch(function (e) {
              if (e instanceof SyntaxError) {
                throw new Error('Request failed. Is the API running at ' + API_BASE + '?');
              }
              throw e;
            });
        }
        return res.json();
      })
      .then(function (data) {
        showResult(data);
      })
      .catch(function (err) {
        showToast(err.message || 'Something went wrong. Try again.');
      })
      .finally(function () {
        setLoading(false);
      });
  }

  el.generateBtn.addEventListener('click', onGenerate);
  el.prompt.disabled = false;
})();
