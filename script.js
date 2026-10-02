/* =========================================
   CAMPUSKART JAVASCRIPT
========================================= */

document.addEventListener("DOMContentLoaded", function () {


    /* =====================================
       ELEMENTS
    ===================================== */

    const searchInput =
        document.getElementById("searchInput");

    const searchBtn =
        document.getElementById("searchBtn");

    const vendorCards =
        document.querySelectorAll(".vendor-card");

    const quickButtons =
        document.querySelectorAll(".quick-btn");

    const categoryCards =
        document.querySelectorAll(".category-card");

    const sortSelect =
        document.getElementById("sortSelect");

    const nearMeBtn =
        document.getElementById("nearMeBtn");

    const menuBtn =
        document.getElementById("menuBtn");

    const navLinks =
        document.querySelector(".nav-links");

    const listBusinessBtn =
        document.getElementById("listBusinessBtn");


    /* =====================================
       SEARCH
    ===================================== */

    function searchVendors(searchText = "") {

        const query =
            searchText.toLowerCase().trim();


        vendorCards.forEach(function (card) {

            const name =
                card.dataset.name.toLowerCase();

            const category =
                card.dataset.category.toLowerCase();

            const description =
                card.querySelector("p")
                    .innerText
                    .toLowerCase();


            const matches =
                name.includes(query) ||
                category.includes(query) ||
                description.includes(query);


            if (matches || query === "") {

                card.classList.remove("hidden");

            } else {

                card.classList.add("hidden");

            }

        });


        document
            .getElementById("vendors")
            .scrollIntoView({
                behavior: "smooth"
            });
    }


    /* =====================================
       SEARCH BUTTON
    ===================================== */

    searchBtn.addEventListener(
        "click",
        function () {

            searchVendors(
                searchInput.value
            );

        }
    );


    /* =====================================
       ENTER SEARCH
    ===================================== */

    searchInput.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Enter") {

                searchVendors(
                    searchInput.value
                );

            }

        }
    );


    /* =====================================
       QUICK SEARCH
    ===================================== */

    quickButtons.forEach(function (button) {

        button.addEventListener(
            "click",
            function () {

                const searchValue =
                    button.dataset.search;

                searchInput.value =
                    searchValue;

                searchVendors(
                    searchValue
                );

            }
        );

    });


    /* =====================================
       CATEGORY CLICK
    ===================================== */

    categoryCards.forEach(function (card) {

        card.addEventListener(
            "click",
            function () {

                const category =
                    card.dataset.category;

                searchInput.value =
                    category;

                searchVendors(
                    category
                );

            }
        );

    });


    /* =====================================
       SORT
    ===================================== */

    sortSelect.addEventListener(
        "change",
        function () {

            const value =
                sortSelect.value;

            const grid =
                document.getElementById(
                    "vendorGrid"
                );

            const cards =
                Array.from(vendorCards);


            if (value === "rating") {

                cards.sort(function (a, b) {

                    return (
                        Number(b.dataset.rating) -
                        Number(a.dataset.rating)
                    );

                });

            }


            if (value === "distance") {

                cards.sort(function (a, b) {

                    return (
                        Number(a.dataset.distance) -
                        Number(b.dataset.distance)
                    );

                });

            }


            if (value === "price") {

                cards.sort(function (a, b) {

                    return (
                        Number(a.dataset.price) -
                        Number(b.dataset.price)
                    );

                });

            }


            cards.forEach(function (card) {

                grid.appendChild(card);

            });

        }
    );


    /* =====================================
       NEAR ME
    ===================================== */

    nearMeBtn.addEventListener(
        "click",
        function () {

            vendorCards.forEach(function (card) {

                const distance =
                    Number(card.dataset.distance);


                if (distance <= 1) {

                    card.classList.remove(
                        "hidden"
                    );

                } else {

                    card.classList.add(
                        "hidden"
                    );

                }

            });


            document
                .getElementById("vendors")
                .scrollIntoView({
                    behavior: "smooth"
                });

        }
    );


    /* =====================================
       FAVORITE
    ===================================== */

    document
        .querySelectorAll(".favorite")
        .forEach(function (button) {

            button.addEventListener(
                "click",
                function (event) {

                    event.stopPropagation();

                    button.classList.toggle(
                        "active"
                    );


                    if (
                        button.classList.contains(
                            "active"
                        )
                    ) {

                        button.innerHTML = "♥";

                    } else {

                        button.innerHTML = "♡";

                    }

                }
            );

        });


    /* =====================================
       DETAILS
    ===================================== */

    document
        .querySelectorAll(".details-btn")
        .forEach(function (button) {

            button.addEventListener(
                "click",
                function () {

                    const vendor =
                        button.dataset.vendor;


                    alert(
                        "Vendor: " +
                        vendor +
                        "\n\n" +
                        "More details, services, pricing " +
                        "and contact information can be " +
                        "connected through the backend/database."
                    );

                }
            );

        });


    /* =====================================
       MAP
    ===================================== */

    document
        .querySelectorAll(".map-btn")
        .forEach(function (button) {

            button.addEventListener(
                "click",
                function () {

                    const vendor =
                        button.dataset.vendor;


                    alert(
                        "📍 Google Maps\n\n" +
                        vendor +
                        "\n\n" +
                        "Google Maps API integration " +
                        "can be connected here."
                    );

                }
            );

        });


    /* =====================================
       MOBILE MENU
    ===================================== */

    menuBtn.addEventListener(
        "click",
        function () {

            navLinks.classList.toggle(
                "active"
            );

        }
    );


    /* =====================================
       CLOSE MOBILE MENU
    ===================================== */

    navLinks
        .querySelectorAll("a")
        .forEach(function (link) {

            link.addEventListener(
                "click",
                function () {

                    navLinks.classList.remove(
                        "active"
                    );

                }
            );

        });


    /* =====================================
       LIST BUSINESS
    ===================================== */

    listBusinessBtn.addEventListener(
        "click",
        function () {

            alert(
                "Vendor Registration\n\n" +
                "Here vendors can register their business, " +
                "add products/services, price, contact details " +
                "and location."
            );

        }
    );


    /* =====================================
       NAVBAR SHADOW
    ===================================== */

    window.addEventListener(
        "scroll",
        function () {

            const navbar =
                document.querySelector(
                    ".navbar"
                );


            if (window.scrollY > 30) {

                navbar.style.boxShadow =
                    "0 5px 25px rgba(16,24,40,0.08)";

            } else {

                navbar.style.boxShadow =
                    "none";

            }

        }
    );


    console.log(
        "CampusKart 🚀 Ready!"
    );

});