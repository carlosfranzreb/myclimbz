// Variables related to video display
const videoFileInput = document.getElementById("videoFile");
const videoContainer = document.getElementById("video-forms-container");
const videoPlayer = document.getElementById("videoPlayer");
const form = videoFileInput.form;
let ffmpeg = null;
let ffmpegLoaded = false;

// Event listener for when a video file is uploaded
videoFileInput.addEventListener("change", function (event) {
	const file = event.target.files[0];

	// Revoke previous object URL if it exists
	if (videoPlayer.previousObjectURL) {
		URL.revokeObjectURL(videoPlayer.previousObjectURL);
		videoPlayer.previousObjectURL = null;
	}

	// If there is no file, return
	if (!file) return;

	// Check that the file type is correct, otherwise alert user and return
	if (!file.type.startsWith("video/")) {
		alert("Please select a valid video file.");
		videoFileInput.value = "";
		videoContainer.classList.append("d-none");
		return;
	}

	// Create the video
	const videoURL = URL.createObjectURL(file);
	videoPlayer.previousObjectURL = videoURL; // Store current URL for future revocation

	videoPlayer.src = videoURL;
	videoPlayer.load();
	videoContainer.classList.remove("d-none");
});

// Seek the video's timestamp (in seconds) that matches the caller's value
// If the input value is a start, its corresponding end is updated if empty
function navigateVideo(event) {
	const timeInSeconds = parseFloat(event.target.value);
	if (isNaN(timeInSeconds)) return;

	videoPlayer.currentTime = timeInSeconds;
	if (event.target.id.includes("start")) {
		const endID = event.target.id.replace("start", "end");
		const endInput = document.getElementById(endID);
		if (!endInput.value.trim()) endInput.value = timeInSeconds + 1;
	}
}

// Add video clips before the form is submitted
async function addVideos() {
	// Return if there is no video
	if (videoFileInput.files.length == 0) return alert("There is no video");

	// Check that each section's end is larger than each section's start,
	// and that all values are between 0 and the video's duration
	const sections = document.querySelectorAll("#sections-container>div");
	for (const div of sections) {
		const startInput = div.querySelector("input[id*='start']");
		const endInput = div.querySelector("input[id*='end']");
		const startValue = parseFloat(startInput.value);
		const endValue = parseFloat(endInput.value);

		if (isNaN(startValue) || isNaN(endValue))
			return alert("Please enter valid numbers for all sections.");

		if (
			startValue < 0 ||
			endValue < 0 ||
			startValue > videoPlayer.duration ||
			endValue > videoPlayer.duration
		)
			return alert(
				`Sections must be between 0 and the video duration (${videoPlayer.duration} seconds).`
			);

		if (endValue <= startValue)
			return alert("Each section's end must be greater than its start.");
	}

	// Check that the number of attempts is at least the number of sections
	const nAttempts = parseInt(document.getElementById("n_attempts").value, 10);
	if (isNaN(nAttempts) || nAttempts < sections.length)
		return alert("There cannot be more sections than attempts.");

	// Disable the screen and inform the user about the upload
	const uploadingOverlay = document.createElement("div");
	uploadingOverlay.style.position = "fixed";
	uploadingOverlay.style.top = 0;
	uploadingOverlay.style.left = 0;
	uploadingOverlay.style.width = "100%";
	uploadingOverlay.style.height = "100%";
	uploadingOverlay.style.backgroundColor = "rgba(0, 0, 0, 0.7)";
	uploadingOverlay.style.zIndex = "9999";
	uploadingOverlay.style.display = "flex";
	uploadingOverlay.style.flexDirection = "column";
	uploadingOverlay.style.alignItems = "center";
	uploadingOverlay.style.justifyContent = "center";
	
	const overlayTitle = document.createElement("h1");
	overlayTitle.style.color = "#fff";
	overlayTitle.innerText = "Clipping videos";
	uploadingOverlay.appendChild(overlayTitle);

	const overlayStatus = document.createElement("p");
	overlayStatus.style.color = "#fff";
	overlayStatus.style.fontSize = "1.2em";
	overlayStatus.style.marginTop = "10px";
	uploadingOverlay.appendChild(overlayStatus);

	document.body.appendChild(uploadingOverlay);

	// Ensure FFmpeg is loaded
	while (!ffmpegLoaded)
		await new Promise((resolve) => setTimeout(resolve, 50));

	// Write the original file into FFmpeg’s filesystem
	await ffmpeg.writeFile("input.mp4", await fetchFile(videoPlayer.src));

	// Add the video to the form fields
	const sectionDivs = document.querySelectorAll("#sections-container>div");
	let completedClips = 0;
	overlayStatus.innerText = `0/${sectionDivs.length}`;

	const sectionPromises = Array.from(sectionDivs).map(async (div) => {
		let start = div.querySelector("input[id*='start']");
		let sectionId = start.id.split("-")[1];
		let startValue = start.value;
		let endValue = div.querySelector("input[id*='end']").value;
		let fileInput = div.querySelector("input[type=file]");
		let duration = String(parseInt(endValue) - parseInt(startValue));

		// Run the clip command
		const outName = `section_${sectionId}.mp4`;
		await ffmpeg.exec([
			"-ss",
			startValue,
			"-i",
			"input.mp4",
			"-t",
			duration,
			"-c",
			"copy",
			outName,
		]);

		// Read the clipped file back out
		const data = await ffmpeg.readFile(outName);
		const clipBlob = new Blob([data.buffer], { type: "video/mp4" });
		const clipFile = new File([clipBlob], outName, {
			type: "video/mp4",
		});

		// Stick it into the file input
		const dt = new DataTransfer();
		dt.items.add(clipFile);
		fileInput.files = dt.files;

		completedClips++;
		overlayStatus.innerText = `${completedClips}/${sectionDivs.length}`;
	});

	// validate and submit the form
	await Promise.all(sectionPromises);
	let form = document.querySelector("#sections-0-file").form;
	if (!form.checkValidity()) {
		form.reportValidity();
		document.body.removeChild(uploadingOverlay);
		return;
	}

	overlayTitle.innerText = "Uploading videos...";
	overlayStatus.innerText = "Starting upload...";

	// Use Background Fetch API if available
	if ('BackgroundFetchManager' in self) {
		try {
			// Request notification permission
			if ('Notification' in window && Notification.permission !== 'granted') {
				await Notification.requestPermission();
			}

			// Calculate total upload size
			let totalUploadSize = 0;
			for (const div of sectionDivs) {
				const fileInput = div.querySelector("input[type=file]");
				if (fileInput.files[0]) {
					totalUploadSize += fileInput.files[0].size;
				}
			}

			const formData = new FormData(form);
			const fetchRequest = new Request(form.action || window.location.href, {
				method: 'POST',
				body: formData,
			});

			const bgFetch = await navigator.serviceWorker.ready.then(swReg => 
				swReg.backgroundFetch.fetch(`upload-${Date.now()}`, fetchRequest, {
					title: `Uploading ${sectionDivs.length} videos`,
					icons: [{
						src: '/static/logo.png', // Replace with actual logo path if available
						sizes: '192x192',
						type: 'image/png',
					}],
					uploadTotal: totalUploadSize,
					downloadTotal: 0, // We don't expect a large response
				})
			);

			// Immediate redirect for better UX
			window.location.href = "/"; 
			return; 
		} catch (err) {
			console.error("Background Fetch failed to start, falling back to AJAX:", err);
			// Fall through to AJAX
		}
	}

	// Fallback: Use AJAX to submit the form and track progress
	const formData = new FormData(form);
	const xhr = new XMLHttpRequest();

	xhr.open("POST", form.action || window.location.href, true);

	xhr.upload.onprogress = function (e) {
		if (e.lengthComputable) {
			const percentComplete = (e.loaded / e.total) * 100;
			overlayStatus.innerText = `${Math.round(percentComplete)}%`;
		}
	};

	xhr.onload = function () {
		if (xhr.status >= 200 && xhr.status < 300) {
			// If the server redirects, the xhr.responseURL will be the new URL
			if (xhr.responseURL && xhr.responseURL !== window.location.href) {
				window.location.href = xhr.responseURL;
			} else {
				// Fallback: replace document content
				document.open();
				document.write(xhr.responseText);
				document.close();
			}
		} else {
			alert("Upload failed. Please try again.");
			document.body.removeChild(uploadingOverlay);
		}
	};

	xhr.onerror = function () {
		alert("An error occurred during the upload.");
		document.body.removeChild(uploadingOverlay);
	};

	xhr.send(formData);
}

const toBlobURL = async (url, mimeType, patcher) => {
	var resp = await fetch(url);
	if (patcher) {
		var body = await resp.text();
		body = patcher(body);
	} else var body = await resp.blob();
	var blob = new Blob([body], { type: mimeType });
	return URL.createObjectURL(blob);
};

const fetchFile = async (url) => {
	var resp = await fetch(url);
	var buffer = await resp.arrayBuffer();
	return new Uint8Array(buffer);
};

// Load FFMPEG
// From <https://github.com/ffmpegwasm/ffmpeg.wasm/issues/548#issuecomment-1707248897>
// TODO: check if all the modules are really needed
async function loadFfmpeg() {
	const baseURLFFMPEG = "https://unpkg.com/@ffmpeg/ffmpeg@0.12.6/dist/umd";
	const ffmpegBlobURL = await toBlobURL(
		`${baseURLFFMPEG}/ffmpeg.js`,
		"text/javascript",
		(js) => {
			return js.replace("new URL(e.p+e.u(814),e.b)", "r.worker814URL");
		}
	);
	const baseURLCore = "https://unpkg.com/@ffmpeg/core@0.12.3/dist/umd";
	const config = {
		worker814URL: await toBlobURL(
			`${baseURLFFMPEG}/814.ffmpeg.js`,
			"text/javascript"
		),
		coreURL: await toBlobURL(
			`${baseURLCore}/ffmpeg-core.js`,
			"text/javascript"
		),
		wasmURL: await toBlobURL(
			`${baseURLCore}/ffmpeg-core.wasm`,
			"application/wasm"
		),
	};
	await import(ffmpegBlobURL);
	ffmpeg = new FFmpegWASM.FFmpeg();
	ffmpeg.on("log", (log) => console.log(log));
	await ffmpeg.load(config);
	ffmpegLoaded = true;
}

document.addEventListener("DOMContentLoaded", () => {
	loadFfmpeg();
	if ('serviceWorker' in navigator) {
		navigator.serviceWorker.register('/sw.js')
			.then(reg => console.log('Service Worker registered', reg))
			.catch(err => console.log('Service Worker registration failed', err));
	}
});
