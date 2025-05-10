// Variables related to video display
const videoFileInput = document.getElementById("videoFileMinimal");
const videoDisplayStep = document.getElementById("video-display-step");
const videoPlayer = document.getElementById("videoPlayer");
const videoFileInfo = document.getElementById("videoFileInfo");

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

	videoFileInfo.textContent = `Displaying: ${file.name} (${(
		file.size /
		1024 /
		1024
	).toFixed(2)} MB)`;
	videoDisplayStep.style.display = "block";
});

// Seek the video's timestamp (in seconds) that matches the caller's value
// TODO: If the input value is a start, its corresponding end must be at least the same value
function navigateVideo(event) {
	const timeInSeconds = parseFloat(event.target.value);
	if (!isNaN(timeInSeconds)) videoPlayer.currentTime = timeInSeconds;
}
