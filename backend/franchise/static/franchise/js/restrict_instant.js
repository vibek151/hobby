// static/franchise/js/restrict_instant.js
(function() {
    document.addEventListener('DOMContentLoaded', function() {
        
        const getCookie = (name) => {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        };

        document.querySelectorAll('.auto-toggle-restriction').forEach(box => {
            box.addEventListener('change', function() {
                const pk = this.getAttribute('data-id');
                const row = this.closest('tr');
                const csrftoken = getCookie('csrftoken');
                
                row.style.opacity = '0.4'; 

                // Use a relative path to ensure it hits the ModelAdmin-defined URL
                fetch(`ajax-toggle-restriction/${pk}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                })
                .then(res => res.json())
                .then(data => {
                    row.style.opacity = '1';
                    if (data.status === 'success') {
                        row.style.backgroundColor = '#d4edda';
                        setTimeout(() => { row.style.backgroundColor = ''; }, 500);
                    } else {
                        alert("Error: " + (data.message || "Could not save"));
                        this.checked = !this.checked; 
                    }
                })
                .catch(err => {
                    row.style.opacity = '1';
                    this.checked = !this.checked;
                    alert("Network error.");
                });
            });
        });
    });
})();