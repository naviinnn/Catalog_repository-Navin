console.log('script.js: File loaded and parsed.');

document.addEventListener('DOMContentLoaded', () => {
    console.log('script.js: DOMContentLoaded event fired.');

    // --- DOM Element References & Utility ---
    const getById = (id) => document.getElementById(id);

    const ui = {
        // Auth elements
        logoutBtn: getById('logoutBtn'),
        loggedInUserSpan: getById('loggedInUser'),

        // Main action buttons
        createCatalogBtn: getById('createCatalogBtn'),

        // Modals & their close buttons
        catalogModal: getById('catalogModal'),
        closeModalBtn: getById('closeModalBtn'),
        confirmModal: getById('confirmModal'),
        closeConfirmModalBtn: getById('closeConfirmModalBtn'),
        
        // Forms
        catalogForm: getById('catalogForm'),
        loginForm: getById('loginForm'), 
        

        // Form fields (for direct access via ui.fieldName)
        catalogId: getById('catalogId'), // Hidden field for update
        catalogName: getById('catalogName'),
        catalogDescription: getById('catalogDescription'),
        startDate: getById('startDate'),
        endDate: getById('endDate'),
        status: getById('status'),
        // Error spans for catalog form
        catalogNameError: getById('catalogNameError'),
        catalogDescriptionError: getById('catalogDescriptionError'),
        startDateError: getById('startDateError'),
        endDateError: getById('endDateError'),
        statusError: getById('statusError'),

        // Login form fields
        usernameOrEmail: getById('username_or_email'),
        password: getById('password'),

        // Form submission & action buttons
        submitCatalogBtn: getById('submitCatalogBtn'),
        confirmDeleteBtn: getById('confirmDeleteBtn'),
        cancelDeleteBtn: getById('cancelDeleteBtn'),

        // Table & messages
        catalogTableBody: getById('catalogTableBody'),
        noCatalogsMessage: getById('noCatalogsMessage'),
        messageContainer: getById('message-container'),
        loadingSpinner: getById('loadingSpinner'),

        // Text elements
        mainTitle: getById('mainTitle'),
        confirmMessage: getById('confirmMessage'),

        // Search and Filter controls
        searchCatalog: getById('searchCatalog'),
        statusFilter: getById('statusFilter'),

        // Pagination elements
        prevPageBtn: getById('prevPageBtn'),
        nextPageBtn: getById('nextPageBtn'),
        currentPageSpan: getById('currentPageSpan'),
        totalPagesSpan: getById('totalPagesSpan'),
    };

    // --- State Variables ---
    let currentDeleteCatalogId = null;
    let currentPage = 1; // Current page number
    const itemsPerPage = 10; // Changed back to 10
    let totalPages = 1; // Total number of pages

    // --- UI Feedback & Modal Management ---

    /** Shows a modal by adding the 'show' class and setting aria-hidden. */
    const showModal = (modalElement) => {
        if (modalElement) { // Ensure element exists before trying to show
            modalElement.classList.add('show');
            modalElement.setAttribute('aria-hidden', 'false');
        }
    };

    /** Hides a modal by removing the 'show' class and setting aria-hidden. */
    const hideModal = (modalElement) => {
        if (modalElement) { // Ensure element exists before trying to hide
            modalElement.classList.remove('show');
            modalElement.setAttribute('aria-hidden', 'true');
        }
    };

    /** Resets the main catalog form to its initial 'Create' state. */
    const resetCatalogForm = () => {
        if (ui.catalogForm) { // Check if form exists
            ui.catalogForm.reset();
        }
        if (ui.catalogId) { ui.catalogId.value = ''; } // Clear the hidden ID field for new creations
        if (ui.submitCatalogBtn) { ui.submitCatalogBtn.textContent = 'Create Catalog'; }
        if (ui.catalogModal) { ui.catalogModal.querySelector('h2').textContent = 'Create New Catalog'; }
        clearFormErrorMessages();
    };

    /** Clears all validation error messages displayed on the forms. */
    const clearFormErrorMessages = () => {
        document.querySelectorAll('.error-text').forEach(el => el.textContent = '');
    };

    /** Displays a temporary success or error message to the user. */
    const showMessage = (message, type = 'success') => {
        if (!ui.messageContainer) {
            console.warn('Message container not found. Cannot display message:', message);
            return;
        }
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        ui.messageContainer.innerHTML = ''; // Clear previous messages
        ui.messageContainer.appendChild(alertDiv);
        setTimeout(() => alertDiv.remove(), 5000); // Auto-hide after 5 seconds
    };

    /** Shows the loading spinner. */
    const showSpinner = () => {
        if (ui.loadingSpinner) { ui.loadingSpinner.classList.add('show'); }
    };

    /** Hides the loading spinner. */
    const hideSpinner = () => {
        if (ui.loadingSpinner) { ui.loadingSpinner.classList.remove('show'); }
    };

    /** Updates the visibility of authentication-related UI elements. */
    const updateAuthUI = () => {
        const username = localStorage.getItem('username'); // Check for username

        if (ui.logoutBtn) {
            ui.logoutBtn.style.display = username ? 'inline-block' : 'none';
        }
        if (ui.loggedInUserSpan) {
            ui.loggedInUserSpan.textContent = username ? `Welcome, ${username}!` : '';
            ui.loggedInUserSpan.style.display = username ? 'inline-block' : 'none';
        }
        if (ui.createCatalogBtn) {
            ui.createCatalogBtn.style.display = username ? 'inline-block' : 'none';
        }
    };

    /**
     * Helper to get a cookie by name.
     * @param {string} name The name of the cookie to retrieve.
     * @returns {string|null} The cookie value or null if not found.
     */
    const getCookie = (name) => {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    };

    // --- API Interaction Layer ---

    /**
     * Handles API requests with integrated loading, error feedback, and JWT inclusion.
     * Includes CSRF token for modifying requests (POST, PUT, DELETE).
     * @param {string} url - The API endpoint URL.
     * @param {Object} options - Fetch API options (method, headers, body).
     * @returns {Promise<Object>} - The JSON data from the successful response.
     * @throws {Error} - If the network request fails or the API returns an error.
     */
    const apiRequest = async (url, options = {}) => {
        showSpinner();
        
        // Prepare headers, ensuring Content-Type for JSON and CSRF token for modifying methods
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers // Merge any existing headers
        };

        const method = options.method ? options.method.toUpperCase() : 'GET';
        if (['POST', 'PUT', 'DELETE'].includes(method)) {
            const csrfToken = getCookie('csrf_access_token');
            if (csrfToken) {
                headers['X-CSRF-TOKEN'] = csrfToken;
            } else {
                console.warn('CSRF token (csrf_access_token) not found. Request might fail.');
            }
        }

        try {
            const response = await fetch(url, { ...options, headers });
            const data = await response.json();
            hideSpinner();

            if (!response.ok) {
                if (response.status === 401 || response.status === 403) {
                    showMessage(data.message || 'Session expired. Please log in again.', 'error');
                    localStorage.removeItem('username');
                    updateAuthUI();
                    window.location.href = '/login'; 
                }
                throw new Error(data.details || data.message || 'An unknown error occurred.');
            }
            return data;
        } catch (error) {
            hideSpinner();
            console.error('API Request Error:', error);
            showMessage(error.message || 'Network error: Could not connect to the server.', 'error');
            throw error;
        }
    };

    /** Fetches and displays all catalogs, with optional search term, status filter, and pagination. */
    const fetchAndDisplayAllCatalogs = async () => {
        console.log('fetchAndDisplayAllCatalogs: Function called.'); 

        const searchTerm = ui.searchCatalog ? ui.searchCatalog.value.trim() : '';
        const statusFilter = ui.statusFilter ? ui.statusFilter.value : '';
        console.log(`DEBUG: statusFilter value from UI: '${statusFilter}'`);

        let url = `/api/catalogs`;
        const params = new URLSearchParams();
        if (searchTerm) {
            params.append('search', searchTerm);
        }
        if (statusFilter) { 
            params.append('status', statusFilter);
        }
        // Add pagination parameters
        params.append('page', currentPage);
        params.append('per_page', itemsPerPage);

        if (params.toString()) {
            url += `?${params.toString()}`;
        }

        console.log('Fetching catalogs from URL:', url); 
        try {
            const result = await apiRequest(url);
            const catalogs = result.data || [];
            const totalCatalogs = result.total_catalogs || 0; // Get total count from API

            console.log('Received catalogs:', catalogs); 
            console.log('Total catalogs (for pagination):', totalCatalogs);

            // Update pagination info
            totalPages = Math.ceil(totalCatalogs / itemsPerPage);
            if (ui.currentPageSpan) ui.currentPageSpan.textContent = currentPage;
            if (ui.totalPagesSpan) ui.totalPagesSpan.textContent = totalPages;

            // Enable/disable pagination buttons
            if (ui.prevPageBtn) ui.prevPageBtn.disabled = currentPage <= 1;
            if (ui.nextPageBtn) ui.nextPageBtn.disabled = currentPage >= totalPages;

            if (ui.catalogTableBody) {
                ui.catalogTableBody.innerHTML = ''; // Clear existing table rows
            }

            if (catalogs.length > 0) {
                if (ui.noCatalogsMessage) { ui.noCatalogsMessage.style.display = 'none'; }
                catalogs.forEach(catalog => {
                    if (ui.catalogTableBody) { // Ensure table body exists before inserting row
                        const row = ui.catalogTableBody.insertRow();
                        row.setAttribute('data-id', catalog.catalog_id); // Store ID on row for easy access
                        row.innerHTML = `
                            <td data-label="ID">${catalog.catalog_id}</td>
                            <td data-label="Name">${catalog.catalog_name}</td>
                            <td data-label="Description">${catalog.catalog_description}</td>
                            <td data-label="Start Date">${catalog.start_date}</td>
                            <td data-label="End Date">${catalog.end_date}</td>
                            <td data-label="Status">${catalog.status}</td>
                            <td class="actions">
                                ${localStorage.getItem('username') ? `
                                    <button class="btn-small btn-edit-color" data-id="${catalog.catalog_id}">Edit</button>
                                    <button class="btn-small btn-danger-color" data-id="${catalog.catalog_id}">Delete</button>
                                ` : ''}
                            </td>
                        `;
                    }
                });
                console.log('Catalogs rendered successfully.'); 
            } else {
                if (ui.noCatalogsMessage) { ui.noCatalogsMessage.style.display = 'block'; } 
                console.log('No catalogs found to display.');
            }
        } catch (error) {
            // Error already handled by apiRequest, just ensure no-catalogs message is shown
            if (ui.noCatalogsMessage) { ui.noCatalogsMessage.style.display = 'block'; }
            console.error('Error fetching and displaying catalogs:', error);
        }
    };

    /** Fetches a single catalog by ID and populates the main catalog form for editing. */
    const fetchCatalogForEdit = async (catalogId) => {
        try {
            const result = await apiRequest(`/api/catalogs/${catalogId}`);
            const catalog = result.data;
            if (catalog) {
                if (ui.catalogId) { ui.catalogId.value = catalog.catalog_id; }
                if (ui.catalogName) { ui.catalogName.value = catalog.catalog_name; }
                if (ui.catalogDescription) { ui.catalogDescription.value = catalog.catalog_description; }
                if (ui.startDate) { ui.startDate.value = catalog.start_date; }
                if (ui.endDate) { ui.endDate.value = catalog.end_date; }
                if (ui.status) { ui.status.value = catalog.status; }

                if (ui.catalogModal) { ui.catalogModal.querySelector('h2').textContent = 'Edit Catalog'; }
                if (ui.submitCatalogBtn) { ui.submitCatalogBtn.textContent = 'Update Catalog'; }
                
                showModal(ui.catalogModal);
            } else {
                showMessage(`Catalog ID ${catalogId} not found.`, 'error');
            }
        } catch (error) {
            // Error already handled by apiRequest
        }
    };

    /** Sends a request to save (create or update) a catalog via the API. */
    const saveCatalog = async (catalogData, catalogId = null) => {
        const method = catalogId ? 'PUT' : 'POST';
        const url = catalogId ? `/api/catalogs/${catalogId}` : '/api/catalogs';

        try {
            const result = await apiRequest(url, {
                method: method,
                // Headers are now handled by apiRequest function
                body: JSON.stringify(catalogData),
            });
            showMessage(result.message, 'success');
            hideModal(ui.catalogModal);
            // After saving, reset page to 1 to ensure new/updated item is visible
            currentPage = 1; 
            resetCatalogForm();
            fetchAndDisplayAllCatalogs();
        } catch (error) {
            if (error.message) {
                const errorMessage = error.message;
                // Check if error elements exist before setting textContent
                if (ui.catalogNameError && errorMessage.includes("Name")) ui.catalogNameError.textContent = errorMessage;
                else if (ui.catalogDescriptionError && errorMessage.includes("Description")) ui.catalogDescriptionError.textContent = errorMessage;
                else if (ui.startDateError && errorMessage.includes("Start Date")) ui.startDateError.textContent = errorMessage;
                else if (ui.endDateError && errorMessage.includes("End Date")) ui.endDateError.textContent = errorMessage;
                else if (ui.statusError && errorMessage.includes("Status")) ui.statusError.textContent = errorMessage;
                else showMessage(errorMessage, 'error');
            }
        }
    };

    /** Displays the confirmation modal for deletion. */
    const promptForDelete = (catalogId) => {
        currentDeleteCatalogId = catalogId;
        if (ui.confirmMessage) {
            ui.confirmMessage.textContent = `Are you sure you want to delete catalog ID ${currentDeleteCatalogId}? This action cannot be undone.`;
        }
        showModal(ui.confirmModal);
    };

    /** Sends a request to delete a catalog by its ID via the API. */
    const deleteCatalog = async (catalogId) => {
        try {
            const result = await apiRequest(`/api/catalogs/${catalogId}`, { method: 'DELETE' });
            showMessage(result.message, 'success');
            // After deleting, reset page to 1 to ensure consistent view
            currentPage = 1;
            fetchAndDisplayAllCatalogs();
        } catch (error) {
            // Error already handled by apiRequest
        } finally {
            hideModal(ui.confirmModal);
            currentDeleteCatalogId = null;
            if (ui.confirmMessage) { ui.confirmMessage.textContent = ""; }
        }
    };

    // --- Client-side Form Validation ---

    /**
     * Validates the inputs of the main catalog form.
     * Provides immediate feedback to the user.
     * @returns {boolean} - True if all inputs are valid, false otherwise.
     */
    const validateCatalogForm = () => {
        clearFormErrorMessages();
        let isValid = true;

        const name = ui.catalogName ? ui.catalogName.value.trim() : '';
        const description = ui.catalogDescription ? ui.catalogDescription.value.trim() : '';
        const startDate = ui.startDate ? ui.startDate.value : '';
        const endDate = ui.endDate ? ui.endDate.value : '';
        const status = ui.status ? ui.status.value : '';

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        if (!name) { if (ui.catalogNameError) ui.catalogNameError.textContent = 'Name is required.'; isValid = false; }
        else if (name.length > 30) { if (ui.catalogNameError) ui.catalogNameError.textContent = 'Name cannot exceed 30 characters.'; isValid = false; }
        
        if (!description) { if (ui.catalogDescriptionError) ui.catalogDescriptionError.textContent = 'Description is required.'; isValid = false; }
        else if (description.length > 50) { if (ui.catalogDescriptionError) ui.catalogDescriptionError.textContent = 'Description cannot exceed 50 characters.'; isValid = false; }
        
        if (!startDate) { if (ui.startDateError) ui.startDateError.textContent = 'Start Date is required.'; isValid = false; }
        else if (new Date(startDate) < today) { if (ui.startDateError) ui.startDateError.textContent = 'Start Date cannot be in the past.'; isValid = false; }

        if (!endDate) { if (ui.endDateError) ui.endDateError.textContent = 'End Date is required.'; isValid = false; }
        else if (new Date(endDate) < today) { if (ui.endDateError) ui.endDateError.textContent = 'End Date cannot be in the past.'; isValid = false; }

        if (startDate && endDate && new Date(startDate) > new Date(endDate)) {
            if (ui.endDateError) ui.endDateError.textContent = 'End Date cannot be before Start Date.'; isValid = false;
        }

        const allowedStatuses = ['active', 'inactive']; // Updated allowed statuses
        const statusLower = status.toLowerCase();
        if (!status) { if (ui.statusError) ui.statusError.textContent = 'Status is required.'; isValid = false; }
        else if (!allowedStatuses.includes(statusLower)) {
            if (ui.statusError) ui.statusError.textContent = `Invalid status. Allowed: ${allowedStatuses.join(', ')}.`; isValid = false;
        }

        return isValid;
    };

    // --- Event Listeners Initialization ---

    // Login Form Submission (only present on login.html)
    if (ui.loginForm) {
        ui.loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            clearFormErrorMessages(); // Clear any previous errors

            const username_or_email = ui.usernameOrEmail.value.trim();
            const password = ui.password.value.trim();

            if (!username_or_email || !password) {
                showMessage('Username/Email and password are required.', 'error');
                return;
            }

            try {
                const result = await apiRequest('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username_or_email, password })
                });
                
                if (result.message === "Login successful." && result.redirect_to) {
                    localStorage.setItem('username', result.data.username); // Store username
                    showMessage('Login successful!', 'success');
                    window.location.href = result.redirect_to; // Redirect to home page
                } else {
                    showMessage(result.message || 'Login failed. Please try again.', 'error');
                }
            } catch (error) {
                // Error handled by apiRequest, message already shown
            }
        });
    }

    // Logout Button (only present on index.html)
    if (ui.logoutBtn) {
        ui.logoutBtn.addEventListener('click', async () => {
            try {
                const result = await apiRequest('/api/logout', { method: 'POST' });
                if (result.message === "Logout successful." && result.redirect_to) {
                    localStorage.removeItem('username'); // Clear stored username
                    showMessage('Logout successful!', 'success');
                    window.location.href = result.redirect_to; // Redirect to login page
                } else {
                    showMessage(result.message || 'Logout failed. Please try again.', 'error');
                }
            } catch (error) {
                // Error handled by apiRequest, message already shown
            }
        });
    }

    // Main action buttons (only present on index.html)
    if (ui.createCatalogBtn) {
        ui.createCatalogBtn.addEventListener('click', () => {
            resetCatalogForm();
            showModal(ui.catalogModal);
        });
    }

    // Search and Filter listeners
    if (ui.searchCatalog) {
        ui.searchCatalog.addEventListener('input', () => {
            currentPage = 1; // Reset to first page on new search
            fetchAndDisplayAllCatalogs();
        });
    }
    if (ui.statusFilter) { 
        ui.statusFilter.addEventListener('change', () => { 
            console.log("Status filter changed. Calling fetchAndDisplayAllCatalogs.");
            currentPage = 1; // Reset to first page on new filter
            fetchAndDisplayAllCatalogs();
        });
    }

    // Pagination button listeners
    if (ui.prevPageBtn) {
        ui.prevPageBtn.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                fetchAndDisplayAllCatalogs();
            }
        });
    }
    if (ui.nextPageBtn) {
        ui.nextPageBtn.addEventListener('click', () => {
            if (currentPage < totalPages) {
                currentPage++;
                fetchAndDisplayAllCatalogs();
            }
        });
    }

    // Close buttons for all modals
    if (ui.closeModalBtn) { ui.closeModalBtn.addEventListener('click', () => hideModal(ui.catalogModal)); }
    if (ui.closeConfirmModalBtn) { ui.closeConfirmModalBtn.addEventListener('click', () => hideModal(ui.confirmModal)); }
    
    // Close modals when clicking outside their content (event delegation on window)
    window.addEventListener('click', (event) => {
        if (ui.catalogModal && event.target === ui.catalogModal) hideModal(ui.catalogModal);
        if (ui.confirmModal && event.target === ui.confirmModal) hideModal(ui.confirmModal);
    });

    // Main catalog form submission
    if (ui.catalogForm) {
        ui.catalogForm.addEventListener('submit', (event) => {
            event.preventDefault(); // Prevent default form submission (page reload)
            if (validateCatalogForm()) {
                const catalogId = ui.catalogId ? ui.catalogId.value : null; // Will be null if creating new
                const catalogData = {
                    name: ui.catalogName ? ui.catalogName.value.trim() : '',
                    description: ui.catalogDescription ? ui.catalogDescription.value.trim() : '',
                    start_date: ui.startDate ? ui.startDate.value : '',
                    end_date: ui.endDate ? ui.endDate.value : '',
                    status: ui.status ? ui.status.value.toLowerCase() : '' // Ensure status is lowercase for backend consistency
                };
                saveCatalog(catalogData, catalogId);
            }
        });
    }

    // Event delegation for Edit/Delete buttons dynamically added to the table
    // CRITICAL: Ensure this matches the class names in index.html
    if (ui.catalogTableBody) {
        ui.catalogTableBody.addEventListener('click', (event) => {
            const target = event.target;
            if (target.classList.contains('btn-small')) { // Check for any small button
                const catalogId = target.dataset.id; // Get ID from data-id attribute
                if (target.classList.contains('btn-edit-color')) { // Specific edit button
                    fetchCatalogForEdit(catalogId);
                } else if (target.classList.contains('btn-danger-color')) { // Specific delete button
                    promptForDelete(catalogId);
                }
            }
        });
    }

    // Confirmation modal buttons
    if (ui.confirmDeleteBtn) {
        ui.confirmDeleteBtn.addEventListener('click', () => {
            if (currentDeleteCatalogId) {
                deleteCatalog(currentDeleteCatalogId);
            }
            // These lines are also in deleteCatalog's finally block, but harmless here
            hideModal(ui.confirmModal);
            currentDeleteCatalogId = null;
            if (ui.confirmMessage) { ui.confirmMessage.textContent = ""; }
        });
    }

    if (ui.cancelDeleteBtn) {
        ui.cancelDeleteBtn.addEventListener('click', () => {
            hideModal(ui.confirmModal);
            currentDeleteCatalogId = null;
            if (ui.confirmMessage) { ui.confirmMessage.textContent = ""; }
        });
    }

    // --- Initial Application Load ---
    // Only fetch and display catalogs if on the index.html page
    if (window.location.pathname === '/home') {
        fetchAndDisplayAllCatalogs();
        updateAuthUI(); // Update UI on page load to reflect login status
    }
});