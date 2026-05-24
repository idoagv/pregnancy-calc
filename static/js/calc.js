// Show only the active mode's input pane. Pure progressive enhancement —
// the server still handles the calculation on submit.
(function () {
    const panes = document.querySelectorAll('.pane[data-mode]');
    const radios = document.querySelectorAll('.tabs input[name="mode"]');

    function sync() {
        const selected = document.querySelector('.tabs input[name="mode"]:checked');
        const mode = selected ? selected.value : 'lmp';
        panes.forEach(p => {
            p.classList.toggle('active', p.dataset.mode === mode);
        });
    }

    radios.forEach(r => r.addEventListener('change', sync));
    sync();
})();
