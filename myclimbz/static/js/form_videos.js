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
	uploadingOverlay.innerHTML =
		"<h1 style='color: #fff;'>Uploading videos... Please wait.</h1>";
	document.body.appendChild(uploadingOverlay);

	// Ensure FFmpeg is loaded
	while (!ffmpegLoaded)
		await new Promise((resolve) => setTimeout(resolve, 50));

	// Write the original file into FFmpeg’s filesystem
	await ffmpeg.writeFile("input.mp4", await fetchFile(videoPlayer.src));

	// Add the video to the form fields
	const sectionPromises = Array.from(
		document.querySelectorAll("#sections-container>div")
	).map(async (div) => {
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
	});

	// validate and submit the form
	await Promise.all(sectionPromises);
	let form = document.querySelector("#sections-0-file").form;
	if (!form.checkValidity()) {
		form.reportValidity();
		document.body.removeChild(uploadingOverlay);
		return;
	}
	form.submit();
}

const toBlobURLPatched = async (url, mimeType, patcher) => {
	var resp = await fetch(url);
	var body = await resp.text();
	if (patcher) body = patcher(body);
	var blob = new Blob([body], { type: mimeType });
	return URL.createObjectURL(blob);
};

// TODO: merge this with `toBlobURLPatched`
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
// TODO: check if all the modules are really needed
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
	ffmpeg.on("log", (log) => console.log(log));
	await ffmpeg.load(config);
	ffmpegLoaded = true;
}

document.addEventListener("DOMContentLoaded", () => {
	loadFfmpeg();
});
