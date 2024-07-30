console.log('Hello world');

// Helper function to add event listener to multiple elements
function addEventListeners(elements, event, handler) {
    elements.forEach(element => {
        element.addEventListener(event, handler);
    });
}

// Check if an element exists in the DOM
function elementExists(selector) {
    return document.querySelector(selector) !== null;
}

// Toggle class function
function toggleClass(element, className) {
    element.classList.toggle(className);
}

// Mobile Nav Hide Show
if (elementExists('.mobile-menu')) {
    // Initialize content cloning
    var mobileMenuContent = document.querySelector('.main-header .nav-outer .main-menu').innerHTML;
    document.querySelector('.mobile-menu .menu-box .menu-outer').innerHTML += mobileMenuContent;
    document.querySelector('.sticky-header .main-menu').innerHTML += mobileMenuContent;

    // Dropdown Button
    addEventListeners(Array.from(document.querySelectorAll('.mobile-menu li.dropdown .dropdown-btn')), 'click', function () {
        toggleClass(this, 'open');
        var submenu = this.nextElementSibling;
        if (submenu.style.display === "block") {
            submenu.style.display = "none";
        } else {
            submenu.style.display = "block";
        }
    });

    // Menu Toggle Btn
    document.querySelector('.mobile-nav-toggler').addEventListener('click', function () {
        document.body.classList.add('mobile-menu-visible');
    });

    // Menu close actions
    addEventListeners(Array.from(document.querySelectorAll('.mobile-menu .menu-backdrop, .mobile-menu .close-btn, .scroll-nav li a')), 'click', function () {
        document.body.classList.remove('mobile-menu-visible');
    });
}
