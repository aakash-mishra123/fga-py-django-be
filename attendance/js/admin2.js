// admin_filters.js
document.addEventListener('DOMContentLoaded', function () {
    var clearFiltersButton = document.createElement('button');
    clearFiltersButton.textContent = 'Clear All Filters';
    clearFiltersButton.className = 'button';
    clearFiltersButton.style.marginLeft = '8px';
    clearFiltersButton.addEventListener('click', function () {
        var filterForm = document.querySelector('.changelist-filter');
        var filterInputs = filterForm.querySelectorAll('input[type="text"], select');
        filterInputs.forEach(function (input) {
            input.value = '';
        });
        filterForm.submit();
    });
    var filterOptions = document.querySelector('.search-filter-helpers');
    filterOptions.appendChild(clearFiltersButton);
});
