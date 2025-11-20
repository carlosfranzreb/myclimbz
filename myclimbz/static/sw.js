self.addEventListener("backgroundfetchsuccess", (event) => {
	console.log("[Service Worker] Background Fetch Success", event);
	event.waitUntil(
		(async function () {
			// Notify the user
			if (Notification.permission === "granted") {
				self.registration.showNotification("Video Upload Complete", {
					body: "Your videos have been successfully uploaded.",
				});
			}

			// Notify client pages (optional, for in-app updates)
			const clients = await self.clients.matchAll();
			clients.forEach((client) => {
				client.postMessage({
					type: "BACKGROUND_FETCH_SUCCESS",
					id: event.registration.id,
				});
			});
		})()
	);
});

self.addEventListener("backgroundfetchfail", (event) => {
	console.log("[Service Worker] Background Fetch Failed", event);
	event.waitUntil(
		(async function () {
			if (Notification.permission === "granted") {
				self.registration.showNotification("Video Upload Failed", {
					body: "There was an error uploading your videos.",
				});
			}

			const clients = await self.clients.matchAll();
			clients.forEach((client) => {
				client.postMessage({
					type: "BACKGROUND_FETCH_FAIL",
					id: event.registration.id,
				});
			});
		})()
	);
});

self.addEventListener("backgroundfetchclick", (event) => {
	console.log("[Service Worker] Background Fetch Clicked", event);
	event.waitUntil(
		(async function () {
			const clients = await self.clients.matchAll();
			if (clients.length > 0) {
				clients[0].focus();
			} else {
				self.clients.openWindow("/");
			}
		})()
	);
});
