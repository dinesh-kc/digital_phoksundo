// static/js/scripts.js
document.addEventListener('DOMContentLoaded', function() {
  // Time display function (if you keep using it)
  function updateTime() {
    const now = new Date();
    const options = {
      timeZone: 'Asia/Kathmandu',
      year: 'numeric', month: 'long', day: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit',
      hour12: true
    };
    const timeElement = document.getElementById('current-time');
    if (timeElement) {
      timeElement.innerText = now.toLocaleString('en-US', options);
    }
  }
  setInterval(updateTime, 1000);
  updateTime();

 
