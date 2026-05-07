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

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrfToken = getCookie('csrftoken');

    document.querySelectorAll('.like-form').forEach(function (form) {
        form.addEventListener('submit', async function (event) {
            event.preventDefault();

            const postCard = form.closest('.post-card');
            const likeBtnText = postCard.querySelector('.like-btn-text');
            const likesCount = postCard.querySelector('.likes-count');

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    credentials: 'same-origin'
                });

                const data = await response.json();

                if (data.success) {
                    likeBtnText.textContent = data.liked ? '❤️ Me gusta' : '🤍 Me gusta';
                    likesCount.textContent = `${data.likes_count} me gusta${data.likes_count === 1 ? '' : 's'}`;
                }
            } catch (error) {
                console.error('Error al procesar like:', error);
            }
        });
    });

    document.querySelectorAll('.comment-form').forEach(function (form) {
        form.addEventListener('submit', async function (event) {
            event.preventDefault();

            const postCard = form.closest('.post-card');
            const textarea = form.querySelector('.comment-input');
            const commentsList = postCard.querySelector('.comments-list');
            const commentsCount = postCard.querySelector('.comments-count');
            const commentEmpty = commentsList.querySelector('.comment-empty');

            const content = textarea.value.trim();
            if (!content) return;

            const formData = new FormData();
            formData.append('content', content);

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData,
                    credentials: 'same-origin'
                });

                const data = await response.json();

                if (data.success) {
                    if (commentEmpty) {
                        commentEmpty.remove();
                    }

                    const commentItem = document.createElement('div');
                    commentItem.classList.add('comment-item');
                    commentItem.innerHTML = `
                        <div class="comment-author">${data.comment.author}</div>
                        <div class="comment-text"></div>
                        <div class="comment-date">${data.comment.created_at}</div>
                    `;

                    commentItem.querySelector('.comment-text').textContent = data.comment.content;
                    commentsList.appendChild(commentItem);

                    commentsCount.textContent = `${data.comments_count} comentario${data.comments_count === 1 ? '' : 's'}`;
                    textarea.value = '';
                } else {
                    console.error('Errores del comentario:', data.errors);
                    alert('No se pudo guardar el comentario.');
                }
            } catch (error) {
                console.error('Error al enviar comentario:', error);
            }
        });
    });
});