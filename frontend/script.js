// Global variables
let currentUser = null;
let providers = [];
let vms = [];
let templates = {};
let clusters = {};
let networks = {};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    initializeEventListeners();
    loadDashboard();
});

// Authentication functions
function checkAuth() {
    // If we are on the login or register page, don't do anything.
    if (window.location.pathname.endsWith('/login.html') || window.location.pathname.endsWith('/register.html')) {
        console.log('On login/register page, skipping auth check');
        return;
    }

    console.log('Checking authentication...');
    fetch('/api/profile')
        .then(response => {
            console.log('Auth check response status:', response.status);
            if (response.ok) {
                return response.json();
            } else {
                // Handle authentication errors
                if (response.status === 401 || response.status === 422) {
                    return response.json().then(errorData => {
                        console.log('Authentication error:', errorData);
                        // Clear cookies for any JWT-related errors
                        if (errorData.msg && (
                            errorData.msg.includes('Subject must be a string') ||
                            errorData.msg.includes('Invalid token') ||
                            errorData.msg.includes('Token has expired') ||
                            errorData.msg.includes('Token decode error') ||
                            errorData.msg.includes('Invalid header padding')
                        )) {
                            console.log('JWT error detected, clearing cookies');
                            clearJWTCookies();
                        }
                        window.location.href = '/login.html';
                        throw new Error('Authentication failed');
                    }).catch(() => {
                        // If we can't parse the error response, just redirect
                        console.log('Not authenticated, redirecting to login');
                        window.location.href = '/login.html';
                        throw new Error('Not authenticated');
                    });
                } else {
                    // If not authenticated, redirect to login page.
                    console.log('Not authenticated, redirecting to login');
                    window.location.href = '/login.html';
                    throw new Error('Not authenticated');
                }
            }
        })
        .then(data => {
            console.log('Authentication successful, user data:', data);
            
            // Check if we got an error message in the response data
            if (data.msg && (
                data.msg.includes('Subject must be a string') ||
                data.msg.includes('Invalid token') ||
                data.msg.includes('Token has expired') ||
                data.msg.includes('Token decode error') ||
                data.msg.includes('Invalid header padding')
            )) {
                console.log('JWT token error in response data, clearing cookies and redirecting to login');
                // Clear cookies and redirect to login
                clearJWTCookies();
                window.location.href = '/login.html';
                return;
            }
            
            currentUser = data.logged_in_as;
            const userNameElement = document.getElementById('user-name');
            if (userNameElement && currentUser) {
                // Handle cases where Prenom or Nom might be undefined
                const firstName = currentUser.Prenom || '';
                const lastName = currentUser.Nom || '';
                const username = currentUser.Username || 'User';
                
                // Display name with fallback to username if names are not available
                if (firstName || lastName) {
                    userNameElement.textContent = `${firstName} ${lastName}`.trim();
                } else {
                    userNameElement.textContent = username;
                }
            }
        })
        .catch(error => {
            // We only need to log errors that are not 'Not authenticated'
            if (error.message !== 'Not authenticated') {
                console.error('Authentication check failed:', error);
            }
        });
}

// Utility function to clear all JWT-related cookies
function clearJWTCookies() {
    const cookiesToClear = [
        'access_token_cookie',
        'refresh_token_cookie', 
        'csrf_access_token',
        'csrf_refresh_token'
    ];
    
    cookiesToClear.forEach(cookieName => {
        // Clear for root path
        document.cookie = `${cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
        // Clear for current path (just in case)
        document.cookie = `${cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=${window.location.pathname};`;
        // Clear without path specification
        document.cookie = `${cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC;`;
    });
}

function logout() {
    fetch('/logout')
        .then(() => {
            // Clear all JWT cookies manually as well
            clearJWTCookies();
            window.location.href = '/login.html';
        })
        .catch(error => {
            console.error('Logout failed:', error);
            // Clear cookies even if logout request fails
            clearJWTCookies();
            window.location.href = '/login.html';
        });
}

// Tab management
function showTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(tab => tab.classList.remove('active'));
    
    // Remove active class from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab content
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Load tab-specific data
    switch(tabName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'create-vm':
            loadCloneVMOptions();
            break;
        case 'vm-list':
            loadVMList();
            break;
        case 'settings':
            loadSettings();
            break;
    }
}

function handleLogin(event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    const form = event ? event.target : document.getElementById('loginForm');
    const formData = new FormData(form);
    const loginData = {
        Username: formData.get('username'),
        password: formData.get('password')
    };

    fetch('/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginData),
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            return response.json().then(data => {
                throw new Error(data.message || 'Login failed');
            });
        }
    })
    .then(data => {
        window.location.replace('/');
    })
    .catch(error => {
        alert('Login failed: ' + error.message);
    });
    
    return false;
}

// Event listeners
function initializeEventListeners() {
    // Form submissions
    document.getElementById('loginForm')?.addEventListener('submit', handleLogin);
    document.getElementById('clone-vm-form')?.addEventListener('submit', handleCloneVM);
    document.getElementById('vmware-config-form')?.addEventListener('submit', handleVMwareConfig);
    document.getElementById('nutanix-config-form')?.addEventListener('submit', handleNutanixConfig);
    document.getElementById('general-settings-form')?.addEventListener('submit', handleGeneralSettings);
    document.getElementById('clone-provider')?.addEventListener('change', updateCloneFormOptions);

    
    // Add change event listener for clone source VM
    document.getElementById('clone-source-vm')?.addEventListener('change', (event) => {
        const selectedOption = event.target.options[event.target.selectedIndex];
        if (!selectedOption.value) return;

        const vmProvider = selectedOption.textContent.match(/\(([^)]+)\)/)?.[1];

        if (vmProvider) {
            const providerSelect = document.getElementById('clone-provider');
            providerSelect.value = vmProvider.toLowerCase();
            
            // Trigger change event to update the form
            updateCloneFormOptions();
        }
    });
}

// Dashboard functions
async function loadDashboard() {
    try {
        showLoading(true);
        
        // Load provider status
        const statusResponse = await fetch('/api/providers/status');
        const statusData = await statusResponse.json();
        
        if (statusData.success) {
            displayProviderStatus(statusData.providers);
        }
        
        // Load VM statistics
        const vmsResponse = await fetch('/api/vms');
        const vmsData = await vmsResponse.json();
        
        if (vmsData.success) {
            displayVMStats(vmsData.vms);
        }
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showNotification('Error loading dashboard data', 'error');
    } finally {
        showLoading(false);
    }
}

function displayProviderStatus(providers) {
    const statusContainer = document.getElementById('provider-status');
    statusContainer.innerHTML = '';
    
    Object.entries(providers).forEach(([name, info]) => {
        const statusDiv = document.createElement('div');
        statusDiv.className = 'provider-status';
        
        const indicator = document.createElement('div');
        indicator.className = `status-indicator ${info.enabled ? (info.connected ? 'online' : 'offline') : 'disabled'}`;
        
        const label = document.createElement('span');
        label.textContent = `${name.toUpperCase()}: ${info.enabled ? (info.connected ? 'Online' : 'Offline') : 'Disabled'}`;
        
        statusDiv.appendChild(indicator);
        statusDiv.appendChild(label);
        statusContainer.appendChild(statusDiv);
    });
}

function displayVMStats(vms) {
    const statsContainer = document.getElementById('vm-stats');
    
    const totalVMs = vms.length;
    const runningVMs = vms.filter(vm => vm.state === 'running').length;
    const stoppedVMs = vms.filter(vm => vm.state === 'stopped').length;
    const vmwareVMs = vms.filter(vm => vm.hypervisor === 'vmware').length;
    const nutanixVMs = vms.filter(vm => vm.hypervisor === 'nutanix').length;
    
    statsContainer.innerHTML = `
        <div class="stat-item">
            <strong>Total VMs:</strong> ${totalVMs}
        </div>
        <div class="stat-item">
            <strong>Running:</strong> ${runningVMs}
        </div>
        <div class="stat-item">
            <strong>Stopped:</strong> ${stoppedVMs}
        </div>
        <div class="stat-item">
            <strong>VMware:</strong> ${vmwareVMs}
        </div>
        <div class="stat-item">
            <strong>Nutanix:</strong> ${nutanixVMs}
        </div>
    `;
}



// Clone VM functions   
async function loadCloneVMOptions() {
    try {
        // Load providers
        const providersResponse = await fetch('/api/providers');
        const providersData = await providersResponse.json();
        
        if (providersData.success) {
            providers = providersData.providers;
            await updateProviderOptions('clone-provider', providers);
        }
        
        // Load VMs for source selection
        await loadVMList(); // Ensure we have the latest VM list
        loadVMsForCloning();
        
        // Load templates, clusters, networks
        await loadResourceOptions();
        
    } catch (error) {
        console.error('Error loading clone VM options:', error);
        showNotification('Error loading options', 'error');
    }
}

async function loadVMsForCloning() {
    const sourceSelect = document.getElementById('clone-source-vm');
    sourceSelect.innerHTML = '<option value="">Select Source VM</option>';

    try {
        const response = await fetch('/api/templates');
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.templates) {
                data.templates.forEach(template => {
                    const vmwareOption = document.createElement('option');
                    vmwareOption.value = template;
                    vmwareOption.textContent = `${template} (vmware)`;
                    vmwareOption.dataset.provider = 'vmware';
                    sourceSelect.appendChild(vmwareOption);
                    
                    const nutanixOption = document.createElement('option');
                    nutanixOption.value = template;
                    nutanixOption.textContent = `${template} (nutanix)`;
                    nutanixOption.dataset.provider = 'nutanix';
                    sourceSelect.appendChild(nutanixOption);
                });
            }
        }
        
        // Don't add existing VMs to templates - templates are separate
        
    } catch (error) {
        console.error('Error loading VMs for cloning:', error);
        showNotification('Failed to load source VMs', 'error');
    }
}

async function updateCloneFormOptions() {
    const provider = document.getElementById('clone-provider').value;
    const nutanixOptions = document.getElementById('nutanix-clone-options');
    
    if (provider === 'nutanix') {
        nutanixOptions.style.display = 'block';
        await updateNutanixOptions('clone');
    } else {
        nutanixOptions.style.display = 'none';
    }
    
    // Filter by selected provider without reloading
    const sourceSelect = document.getElementById('clone-source-vm');
    const options = sourceSelect.options;
    
    for (let i = 1; i < options.length; i++) {
        const option = options[i];
        const optionProvider = option.dataset.provider;
        
        if (!provider || optionProvider === provider) {
            option.style.display = '';
        } else {
            option.style.display = 'none';
        }
    }
}

async function handleCloneVM(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const vmData = Object.fromEntries(formData.entries());
    
    try {
        showLoading(true);
        
        const response = await fetch('/api/vms/clone', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(vmData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`VM '${vmData.vm_name}' cloned successfully!`, 'success');
            event.target.reset();
            updateCloneFormOptions(); // Reset form options
        } else {
            showNotification(`Error cloning VM: ${result.error}`, 'error');
        }
        
    } catch (error) {
        console.error('Error cloning VM:', error);
        showNotification('Error cloning VM', 'error');
    } finally {
        showLoading(false);
    }
}

// VM List functions
async function loadVMList() {
    try {
        showLoading(true);
        
        const response = await fetch('/api/vms');
        const data = await response.json();
        
        if (data.success) {
            vms = data.vms;
            displayVMList(vms);
        } else {
            showNotification('Error loading VM list', 'error');
        }
        
    } catch (error) {
        console.error('Error loading VM list:', error);
        showNotification('Error loading VM list', 'error');
    } finally {
        showLoading(false);
    }
}

function displayVMList(vmList) {
    const tbody = document.getElementById('vm-table-body');
    tbody.innerHTML = '';
    
    vmList.forEach(vm => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${vm.name}</td>
            <td><span class="provider-badge ${vm.hypervisor}">${vm.hypervisor.toUpperCase()}</span></td>
            <td><span class="vm-state ${vm.state}">${vm.state}</span></td>
            <td>${vm.cpu}</td>
            <td>${vm.ram}</td>
            <td>${vm.ip_address || 'N/A'}</td>
            <td class="vm-actions">
                ${vm.state === 'running' ? 
                    `<button class="btn btn-warning btn-sm" onclick="controlVM('${vm.name}', 'stop', '${vm.hypervisor}')">Stop</button>` :
                    `<button class="btn btn-success btn-sm" onclick="controlVM('${vm.name}', 'start', '${vm.hypervisor}')">Start</button>`
                }
                <button class="btn btn-secondary btn-sm" onclick="controlVM('${vm.name}', 'restart', '${vm.hypervisor}')">Restart</button>
                <button class="btn btn-info btn-sm" onclick="openConsole('${vm.name}', '${vm.hypervisor}')">Console</button>
                <button class="btn btn-danger btn-sm" onclick="deleteVM('${vm.name}', '${vm.hypervisor}')">Delete</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function filterVMs() {
    const filterProvider = document.getElementById('filter-provider').value;
    
    if (filterProvider) {
        const filteredVMs = vms.filter(vm => vm.hypervisor === filterProvider);
        displayVMList(filteredVMs);
    } else {
        displayVMList(vms);
    }
}

function refreshVMList() {
    loadVMList();
}

// VM Control functions
async function controlVM(vmName, action, provider) {
    try {
        showLoading(true);
        
        const response = await fetch(`/api/vms/${vmName}/${action}?provider=${provider}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
            loadVMList(); // Refresh the list
        } else {
            showNotification(`Error: ${result.error}`, 'error');
        }
        
    } catch (error) {
        console.error(`Error ${action} VM:`, error);
        showNotification(`Error ${action} VM`, 'error');
    } finally {
        showLoading(false);
    }
}

async function deleteVM(vmName, provider) {
    if (!confirm(`Are you sure you want to delete VM '${vmName}'? This action cannot be undone.`)) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`/api/vms/${vmName}?provider=${provider}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
            loadVMList(); // Refresh the list
        } else {
            showNotification(`Error: ${result.error}`, 'error');
        }
        
    } catch (error) {
        console.error('Error deleting VM:', error);
        showNotification('Error deleting VM', 'error');
    } finally {
        showLoading(false);
    }
}

// Console access function
async function openConsole(vmName, provider) {
    try {
        showLoading(true);
        
        const response = await fetch(`/api/vms/${vmName}/console?provider=${provider}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            if (result.console_type === 'web') {
                // For Nutanix web console
                showNotification(`Opening web console for VM '${vmName}'`, 'info');
                
                // Show console URL in a modal or new window
                const consoleWindow = window.open(result.console_url, '_blank', 'width=1200,height=800');
                if (!consoleWindow) {
                    // If popup blocked, show URL to user
                    const message = `Console URL: ${result.console_url}\n\n${result.instructions}`;
                    alert(message);
                }
            } else {
                // For VMware desktop console
                showNotification(result.message, 'success');
            }
        } else {
            showNotification(`Error opening console: ${result.error}`, 'error');
        }
        
    } catch (error) {
        console.error('Error opening console:', error);
        showNotification('Error opening console', 'error');
    } finally {
        showLoading(false);
    }
}

// Settings functions
async function loadSettings() {
    try {
        // Load current configuration
        const configResponse = await fetch('/api/config');
        const configData = await configResponse.json();
        
        // Load current provider status
        const statusResponse = await fetch('/api/providers/status');
        const statusData = await statusResponse.json();
        
        if (configData.success && statusData.success) {
            updateSettingsForm(configData.config, statusData.providers);
        }
        
    } catch (error) {
        console.error('Error loading settings:', error);
        showNotification('Error loading settings', 'error');
    }
}

function updateSettingsForm(config, providers) {
    // Update VMware settings
    const vmwareConfig = config.providers?.vmware || {};
    const vmwareStatus = providers.vmware || {};
    
    document.getElementById('vmware-enabled').checked = vmwareStatus.enabled || false;
    document.getElementById('vmware-vmrun-path').value = vmwareConfig.vmrun_path || '';
    document.getElementById('vmware-templates-dir').value = vmwareConfig.templates_directory || '';
    
    // Update Nutanix settings
    const nutanixConfig = config.providers?.nutanix || {};
    const nutanixStatus = providers.nutanix || {};
    
    document.getElementById('nutanix-enabled').checked = nutanixStatus.enabled || false;
    document.getElementById('nutanix-pc-ip').value = nutanixConfig.prism_central_ip || '';
    document.getElementById('nutanix-pe-ip').value = nutanixConfig.prism_element_ip || '';
    document.getElementById('nutanix-username').value = nutanixConfig.username || '';
    document.getElementById('nutanix-password').value = ''; // Don't show password
    document.getElementById('nutanix-port').value = nutanixConfig.port || 9440;
    
    // Update general settings
    document.getElementById('default-provider').value = config.default_provider || 'vmware';
}

async function handleVMwareConfig(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const config = {
        provider: 'vmware',
        config: {
            enabled: document.getElementById('vmware-enabled').checked,
            vmrun_path: formData.get('vmware-vmrun-path'),
            templates_directory: formData.get('vmware-templates-dir')
        }
    };
    
    await updateProviderConfig(config);
}

async function handleNutanixConfig(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const config = {
        provider: 'nutanix',
        config: {
            enabled: document.getElementById('nutanix-enabled').checked,
            prism_central_ip: formData.get('nutanix-pc-ip'),
            prism_element_ip: formData.get('nutanix-pe-ip'),
            username: formData.get('nutanix-username'),
            password: formData.get('nutanix-password'),
            port: parseInt(formData.get('nutanix-port')) || 9440
        }
    };
    
    await updateProviderConfig(config);
}

async function handleGeneralSettings(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const defaultProvider = formData.get('default-provider');
    
    try {
        const response = await fetch('/api/config/default-provider', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ provider: defaultProvider })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Default provider updated successfully', 'success');
        } else {
            showNotification(`Error: ${result.error}`, 'error');
        }
        
    } catch (error) {
        console.error('Error updating general settings:', error);
        showNotification('Error updating settings', 'error');
    }
}

async function updateProviderConfig(config) {
    try {
        showLoading(true);
        
        const response = await fetch('/api/config/providers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
            loadSettings(); // Refresh settings
        } else {
            showNotification(`Error: ${result.error}`, 'error');
        }
        
    } catch (error) {
        console.error('Error updating provider config:', error);
        showNotification('Error updating configuration', 'error');
    } finally {
        showLoading(false);
    }
}

// Utility functions
async function loadResourceOptions() {
    try {
        // Load templates (now returns combined list)
        const templatesResponse = await fetch('/api/templates');
        const templatesData = await templatesResponse.json();
        if (templatesData.success) {
            templates = { combined: templatesData.templates };
        }
        
        // Load clusters
        const clustersResponse = await fetch('/api/clusters');
        const clustersData = await clustersResponse.json();
        if (clustersData.success) {
            clusters = clustersData.clusters;
        }
        
        // Load networks
        const networksResponse = await fetch('/api/networks');
        const networksData = await networksResponse.json();
        if (networksData.success) {
            networks = networksData.networks;
        }
        
    } catch (error) {
        console.error('Error loading resource options:', error);
    }
}

async function updateProviderOptions(selectId, providers) {
    const select = document.getElementById(selectId);
    select.innerHTML = '<option value="">Select Platform</option>';
    
    // Get provider status to show availability
    try {
        const statusResponse = await fetch('/api/providers/status');
        const statusData = await statusResponse.json();
        const providerStatus = statusData.success ? statusData.providers : {};
        
        providers.forEach(provider => {
            const option = document.createElement('option');
            option.value = provider;
            
            const status = providerStatus[provider];
            const isEnabled = status && status.enabled;
            const isConnected = status && status.connected;
            
            let displayName = provider === 'vmware' ? 'VMware Workstation' : 'Nutanix AHV';
            
            if (!isEnabled) {
                displayName += ' (Disabled)';
                option.disabled = true;
                option.style.color = '#999';
            } else if (!isConnected) {
                displayName += ' (Not Connected)';
                option.style.color = '#ff6b6b';
            } else {
                displayName += ' (Ready)';
                option.style.color = '#51cf66';
            }
            
            option.textContent = displayName;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error getting provider status:', error);
        // Fallback to basic display
        providers.forEach(provider => {
            const option = document.createElement('option');
            option.value = provider;
            option.textContent = provider === 'vmware' ? 'VMware Workstation' : 'Nutanix AHV';
            select.appendChild(option);
        });
    }
}

async function updateNutanixOptions(prefix) {
    const provider = 'nutanix';
    
    // Update clusters
    const clusterSelect = document.getElementById(`${prefix}-cluster`);
    clusterSelect.innerHTML = '<option value="">Select Cluster</option>';
    if (clusters[provider]) {
        clusters[provider].forEach(cluster => {
            const option = document.createElement('option');
            option.value = cluster;
            option.textContent = cluster;
            clusterSelect.appendChild(option);
        });
    }
    
    // Update networks
    const networkSelect = document.getElementById(`${prefix}-network`);
    networkSelect.innerHTML = '<option value="">Select Network</option>';
    if (networks[provider]) {
        networks[provider].forEach(network => {
            const option = document.createElement('option');
            option.value = network;
            option.textContent = network;
            networkSelect.appendChild(option);
        });
    }
    
    // Update templates (for create form only)
    if (prefix === 'create') {
        const templateSelect = document.getElementById('create-template');
        templateSelect.innerHTML = '<option value="">Create from scratch</option>';
        if (templates.combined) {
            templates.combined.forEach(template => {
                const option = document.createElement('option');
                option.value = template;
                option.textContent = template;
                templateSelect.appendChild(option);
            });
        }
    }
}

function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = show ? 'flex' : 'none';
}

function showNotification(message, type = 'info') {
    const notificationArea = document.getElementById('notification-area');
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div>${message}</div>
    `;
    
    notificationArea.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
    
    // Remove on click
    notification.addEventListener('click', () => {
        notification.remove();
    });
}