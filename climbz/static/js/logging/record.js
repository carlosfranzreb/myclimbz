let mediaRecorder;
let audioChunks = [];
let recording = false;
let recordButton = document.getElementById("record_button");
recordButton.addEventListener("click", record_audio);

let icon_microphone = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"class="bi bi-mic-fill" viewBox="0 0 16 16"><path d="M5 3a3 3 0 0 1 6 0v5a3 3 0 0 1-6 0z" /><path    d="M3.5 6.5A.5.5 0 0 1 4 7v1a4 4 0 0 0 8 0V7a.5.5 0 0 1 1 0v1a5 5 0 0 1-4.5 4.975V15h3a.5.5 0 0 1 0 1h-7a.5.5 0 0 1 0-1h3v-2.025A5 5 0 0 1 3 8V7a.5.5 0 0 1 .5-.5" /></svg>'
let icon_recording = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-record-circle" viewBox="0 0 16 16"><path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/><path d="M11 8a3 3 0 1 1-6 0 3 3 0 0 1 6 0"/></svg>'
let icon_spinner = '<div class="spinner-border spinner-border-sm" role="status"><span class="sr-only"></span></div>'


function record_audio() {
    if (!recording) {
        startRecording();
        recordButton.innerHTML = "Record " + icon_recording;
        recording = true;
    }
    else {
        stopRecording();
        recordButton.innerHTML = "Record " + icon_spinner;
        sendToServer();
        recording = false;
    }
}


function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            }

            mediaRecorder.onstop = () => {
                let audioBlob = new Blob(audioChunks, { type: "audio/wav" });
                audioPlayer.src = URL.createObjectURL(audioBlob);
                audioPlayer.play();
                sendButton.disabled = false;
            }

            mediaRecorder.start();
        })
        .catch(error => console.error("Error accessing microphone:", error));
}

function stopRecording() {
    mediaRecorder.stop();
}

function sendToServer() {
    let audioBlob = new Blob(audioChunks, { type: "audio/webm" });
    let formData = new FormData();
    formData.append("audioFile", audioBlob, "recording.webm");
    formData.append("data_type", "audio");
    formData.append("csrf_token", document.querySelector('input[name="csrf_token"]').value);

    fetch("/", {
        method: "POST",
        body: formData
    })
        .then(response => {
            recordButton.innerHTML = "Record " + icon_microphone;
            if (response.ok)
                if (document.getElementById("stopSession"))
                    window.location.href = "/add_climb";
                else
                    window.location.href = "/add_session";
            else
                alert("Server error:", response.statusText);
        })
        .catch(error => alert("Error sending audio to server:", error));
}
