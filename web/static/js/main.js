document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadContainer = document.getElementById('upload-container');
    const loadingState = document.getElementById('loading-state');
    const resultsContainer = document.getElementById('results-container');
    const resultImage = document.getElementById('result-image');
    const downloadImage = document.getElementById('download-image');
    const downloadPdf = document.getElementById('download-pdf');
    const terminalLogs = document.getElementById('terminal-logs');
    const btnNovaAnalise = document.getElementById('nova-analise');

    // Abre diálogo do input file
    dropZone.addEventListener('click', () => fileInput.click());

    // Eventos de drag and drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('dragover');
        });
    });

    // Lida com o arquivo arrastado e solto
    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length) {
            handleUpload(files[0]);
        }
    });

    // Lida com o arquivo selecionado no menu do O.S.
    fileInput.addEventListener('change', function() {
        if (this.files.length) {
            handleUpload(this.files[0]);
        }
    });

    btnNovaAnalise.addEventListener('click', () => {
        resultsContainer.classList.add('hidden');
        uploadContainer.classList.remove('hidden');
        fileInput.value = ''; // Reset do input
    });

    function handleUpload(file) {
        // Validação inicial
        if (!file.type.match('image.*')) {
            alert('Por favor, selecione apenas arquivos de imagem.');
            return;
        }

        // Feedback de Loading animado e remoção do upload field
        uploadContainer.classList.add('hidden');
        loadingState.classList.remove('hidden');
        
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = function() {
            const base64Data = reader.result;

            // Envío AJAX
            fetch('http://127.0.0.1:8000/analisar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    image: base64Data,
                    filename: file.name
                })
            })
            .then(response => response.json().then(data => ({status: response.status, body: data})))
        .then(res => {
            loadingState.classList.add('hidden');
            
            if (res.status === 200 && res.body.success) {
                // Sucesso na extração visual e de dados via Python backend
                
                // Previne cache appending timestamp
                resultImage.src = res.body.image_url + "?t=" + new Date().getTime();
                downloadImage.href = res.body.image_url + "?t=" + new Date().getTime();
                
                if (res.body.pdf_url) {
                    downloadPdf.href = res.body.pdf_url + "?t=" + new Date().getTime();
                    downloadPdf.style.display = 'inline-block';
                } else {
                    downloadPdf.style.display = 'none';
                }

                terminalLogs.textContent = res.body.logs || "Comando executado silenciosamente sem retorno visível.";
                resultsContainer.classList.remove('hidden');
                document.querySelector('.results-grid').style.display = 'grid';
            } else {
                // Erro propagado do Analisador_Objetos
                alert('Erro na análise: ' + (res.body.error || 'Erro desconhecido. Verifique o log.'));
                uploadContainer.classList.remove('hidden');
                
                if (res.body.logs) {
                    terminalLogs.textContent = res.body.logs;
                    resultsContainer.classList.remove('hidden');
                    // Esconde a área de sucesso e mostra somentes os logs e novo btn
                    document.querySelector('.results-grid').style.display = 'none';
                }
            }
        })
        .catch(err => {
            loadingState.classList.add('hidden');
            uploadContainer.classList.remove('hidden');
            alert('Falha na comunicação com o servidor.');
            console.error(err);
        });
        };
    }
});
