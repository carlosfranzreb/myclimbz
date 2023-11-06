let mediaRecorder;
let audioChunks = [];
let audioPlayer = document.getElementById('audioPlayer');
let startButton = document.getElementById('startButton');
let stopButton = document.getElementById('stopButton');
let sendButton = document.getElementById('sendButton');

startButton.addEventListener('click', startRecording);
stopButton.addEventListener('click', stopRecording);
sendButton.addEventListener('click', sendToServer);

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            }

            mediaRecorder.onstop = () => {
                let audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                audioPlayer.src = URL.createObjectURL(audioBlob);
                audioPlayer.play();
                sendButton.disabled = false;
            }

            mediaRecorder.start();
            startButton.disabled = true;
            stopButton.disabled = false;
        })
        .catch(error => console.error('Error accessing microphone:', error));
}

function stopRecording() {
    mediaRecorder.stop();
    startButton.disabled = false;
    stopButton.disabled = true;
}

function sendToServer() {
    let audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    let formData = new FormData();
    formData.append('audioFile', audioBlob, 'recording.webm');
    formData.append('csrf_token', document.querySelector('input[name="csrf_token"]').value);

    fetch('/', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log(response);
        if (response.ok)
            if (document.getElementById('stopSession'))
                window.location.href = "/add_climb";
            else
                window.location.href = "/add_session";
        else
            alert('Server error:', response.statusText);
    })
    .catch(error => alert('Error sending audio to server:', error));
}
