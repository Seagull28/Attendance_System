// ... existing code ...
document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const startButton = document.getElementById('startCapture');
    const rollNumberInput = document.getElementById('rollNumber');
    const faceCountSpan = document.getElementById('faceCount');
    const capturedImages = document.getElementById('capturedImages');
    let faceCount = 0;
    let stream = null;

    async function initializeCamera() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
            video.play();
        } catch (err) {
            console.error("Error accessing camera:", err);
            alert("Error accessing camera. Please check permissions and ensure no other application is using the camera.");
        }
    }

    async function captureFace() {
        if (!rollNumberInput.value) {
            alert("Please enter a roll number");
            return;
        }
        if (faceCount >= 5) {
            alert("Face has already been captured!");
            return;
        }
        if (!video.srcObject) {
            alert("Camera not initialized");
            return;
        }
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/jpeg');
        try {
            const response = await fetch('/dashboard/face-capture/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: `image=${encodeURIComponent(imageData)}&roll_number=${rollNumberInput.value}`
            });
            const data = await response.json();
            if (data.success) {
                faceCount++;
                faceCountSpan.textContent = faceCount;
                displayCapturedImage(imageData);
                startButton.disabled = true;
                startButton.textContent = 'Face Captured';
            } else {
                alert(data.error || "Failed to capture face");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Error capturing face");
        }
    }

    function displayCapturedImage(imageData) {
        const img = document.createElement('img');
        img.src = imageData;
        img.className = 'captured-image';
        img.style.width = '100px';
        img.style.height = '100px';
        capturedImages.appendChild(img);
    }

    function getCookie(name) {
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
    }

    // Initialize camera immediately when DOM is loaded
    initializeCamera();
    startButton.addEventListener('click', captureFace);

    // Optional: Clean up camera stream when leaving the page
    window.addEventListener('beforeunload', function() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    });
});
// ... existing code ...