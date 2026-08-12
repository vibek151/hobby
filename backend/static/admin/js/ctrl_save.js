document.addEventListener('keydown', function(e) {
    console.log("CTRL SAVE LOADED");
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();

        const saveBtn = document.querySelector('input[name="_save"]');

        if (saveBtn) {
            saveBtn.click();
        }
    }

});