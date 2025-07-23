// static/admin/js/nepali_datepicker_init.js

// This function needs to run after the DOM is fully loaded and Django's own JS
// has processed the admin forms. Django's built-in datepicker script (if active)
// might attach to 'vDateField', so ensure our script runs after that or correctly
// overrides/coexists.

// Using a common pattern for Django admin JS
(function($) {
    $(document).ready(function() {
        // Select input fields that have the 'vDateField' class.
        // These are the ones where Django's admin usually puts its date pickers.
        // Our custom form field applies this class.
        var nepaliDateInputs = $('.vDateField');

        nepaliDateInputs.each(function() {
            // Check if nepaliDatePicker function is available
            if (typeof $(this).nepaliDatePicker === 'function') {
                $(this).nepaliDatePicker({
                    dateFormat: "%Y-%m-%d", // Standard format for Nepali date input
                    closeOnDateSelect: true,
                    language: "english" // Set to "nepali" if you want Nepali numerals in the picker
                });
            } else {
                console.warn("nepaliDatePicker function not found. Ensure the JS library is loaded.");
            }
        });
    });
})(django.jQuery); // Use django.jQuery to ensure compatibility with Django Admin's jQuery instance