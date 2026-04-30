document.addEventListener('DOMContentLoaded', function () {
    const body = document.body;

    const postModal = document.getElementById('postModal');
    const postOverlay = document.getElementById('postModalOverlay');
    const openPostBtn = document.getElementById('openPostModal');
    const closePostBtn = document.getElementById('closePostModal');

    const projectModal = document.getElementById('projectModal');
    const projectOverlay = document.getElementById('projectModalOverlay');
    const openProjectBtn = document.getElementById('openProjectModal');
    const closeProjectBtn = document.getElementById('closeProjectModal');

    function lockScroll() {
        body.classList.add('modal-open');
    }

    function unlockScrollIfNeeded() {
        const postVisible = postModal && !postModal.classList.contains('hidden');
        const projectVisible = projectModal && !projectModal.classList.contains('hidden');

        if (!postVisible && !projectVisible) {
            body.classList.remove('modal-open');
        }
    }

    function openModal(modal, overlay) {
        if (!modal || !overlay) return;
        modal.classList.remove('hidden');
        overlay.classList.remove('hidden');
        lockScroll();
    }

    function closeModal(modal, overlay) {
        if (!modal || !overlay) return;
        modal.classList.add('hidden');
        overlay.classList.add('hidden');
        unlockScrollIfNeeded();
    }

    if (openPostBtn) {
        openPostBtn.addEventListener('click', function () {
            openModal(postModal, postOverlay);
        });
    }

    if (closePostBtn) {
        closePostBtn.addEventListener('click', function () {
            closeModal(postModal, postOverlay);
        });
    }

    if (postOverlay) {
        postOverlay.addEventListener('click', function () {
            closeModal(postModal, postOverlay);
        });
    }

    if (openProjectBtn) {
        openProjectBtn.addEventListener('click', function () {
            openModal(projectModal, projectOverlay);
        });
    }

    if (closeProjectBtn) {
        closeProjectBtn.addEventListener('click', function () {
            closeModal(projectModal, projectOverlay);
        });
    }

    if (projectOverlay) {
        projectOverlay.addEventListener('click', function () {
            closeModal(projectModal, projectOverlay);
        });
    }

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            closeModal(postModal, postOverlay);
            closeModal(projectModal, projectOverlay);
        }
    });
});