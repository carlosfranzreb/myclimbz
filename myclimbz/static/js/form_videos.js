const videoFileInput = document.getElementById("videoFileMinimal");
const videoDisplayStep = document.getElementById("video-display-step");
const videoPlayer = document.getElementById("videoPlayer");
const videoFileInfo = document.getElementById("videoFileInfo");

// New: Seek elements
const seekTimeInput = document.getElementById("seekTimeInput");
const seekButton = document.getElementById("seekButton");
const videoCurrentTimeDisplay = document.getElementById("videoCurrentTime");

let currentVideoDuration = 0;

videoFileInput.addEventListener("change", function (event) {
	const file = event.target.files[0];

	if (file) {
		if (!file.type.startsWith("video/")) {
			alert("Please select a valid video file.");
			videoFileInput.value = "";
			videoDisplayStep.style.display = "none";
			return;
		}

		const videoURL = URL.createObjectURL(file);

		// Revoke previous object URL if it exists
		if (videoPlayer.previousObjectURL) {
			URL.revokeObjectURL(videoPlayer.previousObjectURL);
		}
		videoPlayer.previousObjectURL = videoURL; // Store current URL for future revocation

		videoPlayer.src = videoURL;
		videoPlayer.load();

		videoFileInfo.textContent = `Displaying: ${file.name} (${(
			file.size /
			1024 /
			1024
		).toFixed(2)} MB)`;
		videoDisplayStep.style.display = "block";
		seekTimeInput.value = ""; // Clear seek input
		videoCurrentTimeDisplay.textContent = "Current time: 0.00s"; // Reset current time display
		currentVideoDuration = 0; // Reset duration
	} else {
		videoDisplayStep.style.display = "none";
		videoPlayer.src = "";
		videoFileInfo.textContent = "";
		if (videoPlayer.previousObjectURL) {
			URL.revokeObjectURL(videoPlayer.previousObjectURL);
			videoPlayer.previousObjectURL = null;
		}
		currentVideoDuration = 0;
	}
});

// Event listener for when video metadata is loaded (to get duration)
if (videoPlayer) {
	videoPlayer.addEventListener("loadedmetadata", () => {
		currentVideoDuration = videoPlayer.duration;
		seekTimeInput.max = Math.ceil(currentVideoDuration); // Set max for input field
	});

	// Event listener to update current time display
	videoPlayer.addEventListener("timeupdate", () => {
		videoCurrentTimeDisplay.textContent = `Current time: ${videoPlayer.currentTime.toFixed(
			2
		)}s`;
	});
}

// Event listener for seek button
seekButton.addEventListener("click", () => {
	const timeInSeconds = parseFloat(seekTimeInput.value);
	if (
		!isNaN(timeInSeconds) &&
		timeInSeconds >= 0 &&
		timeInSeconds <= currentVideoDuration
	) {
		videoPlayer.currentTime = timeInSeconds;
	} else if (
		!isNaN(timeInSeconds) &&
		currentVideoDuration > 0 &&
		timeInSeconds > currentVideoDuration
	) {
		alert(
			`Please enter a time between 0 and ${Math.floor(
				currentVideoDuration
			)} seconds.`
		);
		videoPlayer.currentTime = currentVideoDuration; // Seek to end if user enters too high
	} else if (!isNaN(timeInSeconds) && timeInSeconds < 0) {
		alert("Time cannot be negative. Please enter a positive number.");
		videoPlayer.currentTime = 0; // Seek to beginning
	} else {
		alert("Please enter a valid number for seconds.");
	}
});
