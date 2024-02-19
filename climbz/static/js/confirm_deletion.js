// If the user clicks on a button to delete something, a confirmation dialog is shown
document.addEventListener('click', event => {
    for (let element of [event.target, event.target.parentNode]) {
        if (element.tagName === 'A' && element.href.includes('delete_')) {
            if (!confirm("Please confirm the deletion.")) {
                event.preventDefault();
                event.stopPropagation();

            }
        }
    }
});