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

});

// This is a generic script to initialize components used in the template.
// You can expand this file for your custom scripts.

$(document).ready(function() {
    
    // Initialize DataTables with responsive feature
    // Use a class like .datatable on your tables to apply this
    $('.datatable').DataTable({
        responsive: true,
        // You can add other default options here
        // order: [[0, 'desc']]
    });

    // Initialize Nepali Date Picker
    // Use a class like .nepali-datepicker on your input fields
    $(".nepali-datepicker").nepaliDatePicker({
        ndpYear: true,
        ndpMonth: true,
        ndpYearCount: 10
    });

    // Set active class on sidebar nav links based on current URL
    const currentUrl = window.location.href;
    $('.sidebar-nav a.nav-link, .offcanvas a.nav-link').each(function () {
        if (this.href === currentUrl) {
            $(this).addClass('active');
        }
    });

});