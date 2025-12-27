function toggleSub(id) {
    const el = document.getElementById(id);
    el.style.display = el.style.display === "block" ? "none" : "block";
}

function openForm(category, subcategory) {
    window.location.href =
        `/complaint?category=${encodeURIComponent(category)}&subcategory=${encodeURIComponent(subcategory)}`;
}
