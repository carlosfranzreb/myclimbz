// Variables related to video display
const videoFileInput = document.getElementById("videoFile");
const videoDisplayStep = document.getElementById("video-display-step");
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
		videoDisplayStep.style.display = "none";
		return;
	}

	// Create the video
	const videoURL = URL.createObjectURL(file);
	videoPlayer.previousObjectURL = videoURL; // Store current URL for future revocation

	videoPlayer.src = videoURL;
	videoPlayer.load();
	videoDisplayStep.style.display = "block";
});

// Seek the video's timestamp (in seconds) that matches the caller's value
// TODO: If the input value is a start, its corresponding end must be at least the same value
function navigateVideo(event) {
	const timeInSeconds = parseFloat(event.target.value);
	if (!isNaN(timeInSeconds)) videoPlayer.currentTime = timeInSeconds;
}

// Add video clips before the form is submitted
async function addVideos() {
	// Return if there is no video
	const videoFile = videoFileInput.files[0];
	if (!videoFile) return alert("There is no video");

	// Ensure FFmpeg is loaded
	while (!ffmpegLoaded)
		await new Promise((resolve) => setTimeout(resolve, 50));

	// Write the original file into FFmpeg’s in-MEM filesystem once
	ffmpeg.FS("writeFile", "input.mp4", await fetchFile(videoFile));

	// Add the video to the form fields
	const dt = new DataTransfer();
	dt.items.add(videoFile);
	document.querySelectorAll("#sections-container>div").forEach((div) => {
		let startValue = div.querySelector("input[id*='start']").value;
		let endValue = div.querySelector("input[id*='end']").value;
		let fileInput = div.querySelector("input[type=file]");
		let sectionId = start.id.split("-")[1];

		// Build a unique output filename
		const outName = `section_${sectionId}.mp4`;

		// Run the clip command
		// -ss before -i is faster but less accurate; here we do it after for frame-accurate cutting
		ffmpeg.run(
			"-i",
			"input.mp4",
			"-ss",
			startValue,
			"-to",
			endValue,
			"-c",
			"copy",
			outName
		);

		// Read the clipped file back out
		const data = ffmpeg.FS("readFile", outName);
		const clipBlob = new Blob([data.buffer], { type: "video/mp4" });

		// Create a new File so it can be attached to the <input type="file">
		const clipFile = new File(
			[clipBlob],
			// you can keep the original name or generate your own:
			`${videoFile.name.replace(/\.[^.]+$/, "")}_clip${i}.mp4`,
			{ type: "video/mp4" }
		);

		// Stick it into the file input
		const dt = new DataTransfer();
		dt.items.add(clipFile);
		fileInput.files = dt.files;
	});

	// validate the form
	let form = document.querySelector("#sections-0-file").form;
	if (!form.checkValidity()) {
		form.reportValidity();
		return;
	}

	// Submit the form
	form.submit();
}

const toBlobURLPatched = async (url, mimeType, patcher) => {
	var resp = await fetch(url);
	var body = await resp.text();
	if (patcher) body = patcher(body);
	var blob = new Blob([body], { type: mimeType });
	return URL.createObjectURL(blob);
};

const toBlobURL = async (url, mimeType) => {
	var resp = await fetch(url);
	var body = await resp.blob();
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
async function loadFfmpeg() {
	const baseURLFFMPEG = "https://unpkg.com/@ffmpeg/ffmpeg@0.12.6/dist/umd";
	const ffmpegBlobURL = await toBlobURLPatched(
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
	ffmpeg.on("log", ({ message }) => {
		logDiv.innerHTML = message;
		console.log(message);
	});
	await ffmpeg.load(config);
	ffmpegLoaded = true;
}

document.addEventListener("DOMContentLoaded", () => {
	loadFfmpeg();
});
