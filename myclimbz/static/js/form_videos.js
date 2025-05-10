document.addEventListener("DOMContentLoaded", () => {
	const videoFileInput = document.getElementById("videoFileMinimal");
	const videoDisplayStep = document.getElementById("video-display-step");
	const videoPlayer = document.getElementById("videoPlayer");
	const videoFileInfo = document.getElementById("videoFileInfo");

	if (videoFileInput) {
		videoFileInput.addEventListener("change", function (event) {
			const file = event.target.files[0];

			if (file) {
				// Check if the file is a video
				if (!file.type.startsWith("video/")) {
					alert("Please select a valid video file.");
					videoFileInput.value = ""; // Reset the input
					videoDisplayStep.style.display = "none";
					return;
				}

				const videoURL = URL.createObjectURL(file);

				videoPlayer.src = videoURL;
				videoPlayer.load(); // Important to load the new source

				videoFileInfo.textContent = `Displaying: ${file.name} (${(
					file.size /
					1024 /
					1024
				).toFixed(2)} MB)`;
				videoDisplayStep.style.display = "block";

				// Optional: Revoke the object URL when the video is no longer needed
				// to free up resources. For example, when a new video is selected
				// or the page is unloaded.
				videoPlayer.onloadedmetadata = () => {
					// If there was a previous object URL, revoke it
					if (videoPlayer.previousObjectURL) {
						URL.revokeObjectURL(videoPlayer.previousObjectURL);
					}
					videoPlayer.previousObjectURL = videoURL;
				};
			} else {
				videoDisplayStep.style.display = "none";
				videoPlayer.src = "";
				videoFileInfo.textContent = "";
				if (videoPlayer.previousObjectURL) {
					URL.revokeObjectURL(videoPlayer.previousObjectURL);
					videoPlayer.previousObjectURL = null;
				}
			}
		});
	} else {
		console.error("Video file input 'videoFileMinimal' not found!");
	}
});
