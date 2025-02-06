        // Function to update the time and date
        function updateTime() {
            const now = new Date();
            // Format the date (e.g., "October 10, 2023")
            const options = { year: 'numeric', month: 'long', day: 'numeric' };
            const dateString = now.toLocaleDateString(undefined, options);
            document.getElementById('current-date').textContent = dateString;
            // Format the time with seconds (e.g., "14:35:07")
            const timeString = now.toLocaleTimeString();
            document.getElementById('current-time').textContent = timeString;
        }
    
        // Update the time every second
        setInterval(updateTime, 1000);
    
        // Initialize the time and date immediately
        updateTime();
    
        // Function to trigger the loading animation
        function startLoadingAnimation() {
            const dateTimeContainer = document.getElementById('date-time-container');
            const loadingAnimation = document.getElementById('loading-animation');
    
            // Collapse the date and time
            dateTimeContainer.classList.add('animate-collapse');
            setTimeout(() => {
                dateTimeContainer.classList.add('hidden');
                loadingAnimation.classList.remove('hidden');
            }, 300); // Match the duration of the collapse animation
        }
    
        // Add event listeners to all links to trigger the loading animation
        document.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', (event) => {
                // Prevent default behavior for demonstration purposes (remove this line in production)
                // event.preventDefault();
    
                // Start the loading animation
                startLoadingAnimation();
            });
        });


    // Function to mark a notification as read
    function markAsRead(notificationId) {
        // Send a GET request to mark the notification as read
        fetch(`/mark_as_read/BDT {notificationId}/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'  // Include CSRF token
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Remove the bold styling to indicate it's read
                document.getElementById('notification-' + notificationId).classList.remove('font-bold');
            }
        })
        .catch(error => console.error('Error:', error));
    }

    // Attach event listeners to notification items to mark them as read
    document.querySelectorAll('.notification-item').forEach(item => {
        item.addEventListener('click', function () {
            const notificationId = this.dataset.notificationId;
            markAsRead(notificationId);
        });
    });






