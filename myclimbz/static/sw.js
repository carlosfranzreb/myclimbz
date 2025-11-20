/**
 * Handles the 'backgroundfetchsuccess' event in the service worker when a Background Fetch completes successfully.
 * The two other listeners are similar: 'fail' informs when a fetch fails, and 'click' sends the user to the app,
 * which is opened if needed, when the user clicks on the fetch UI.
 *
 * Actions performed:
 * - Extends the service worker's lifetime with event.waitUntil while asynchronous tasks run.
 * - If Notification.permission === 'granted', displays a notification titled "Video Upload Complete".
 * - Retrieves all controlled client pages via self.clients.matchAll() and posts a message to each client:
 *   { type: "BACKGROUND_FETCH_SUCCESS", id: event.registration.id } to inform in-app pages about the completed fetch.
 *
 * Notes:
 * - This runs in the service worker global scope (self).
 * - Relies on BackgroundFetchEvent semantics (event.registration provides the registration id).
 *
 * @param {BackgroundFetchEvent} event - The background fetch success event dispatched to the service worker.
 * @returns {void}
 * @listens ServiceWorkerGlobalScope#backgroundfetchsuccess
 */
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
