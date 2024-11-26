document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.btn');
    const contentArea = document.getElementById('content-area');

    buttons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();

            const action = this.textContent.trim();

            // Dynamically update the content without reloading the page
            if (action === 'Food & Meal Management') {
                contentArea.innerHTML = `
                    <h2>Food & Meal Management Menu</h2>
                    <ul>
                        <li><a href="#" class="btn btn-primary" onclick="loadSubMenu('Add Food Item')">Add Food Item</a></li>
                        <li><a href="#" class="btn btn-primary" onclick="loadSubMenu('Browse Food Database')">Browse Food Database</a></li>
                        <li><a href="#" class="btn btn-primary" onclick="loadSubMenu('Show Items')">Show Items</a></li>
                        <li><a href="#" class="btn btn-primary" onclick="loadSubMenu('Meal Planning')">Meal Planning</a></li>
                        <li><a href="#" class="btn btn-primary" onclick="loadSubMenu('Food Log')">Food Log</a></li>
                        <li><a href="#" class="btn btn-danger" onclick="goBack()">Go Back</a></li>
                    </ul>
                `;
            } else {
                contentArea.innerHTML = `<h2>${action} page loaded</h2>`;
            }
        });
    });
});

// Function to load submenu content dynamically
function loadSubMenu(submenu) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `<h2>${submenu} content loaded</h2>`;
}

// Go back to the main menu
function goBack() {
    window.location.href = '/';
}
