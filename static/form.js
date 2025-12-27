// Simple client-side validation
document.querySelector("form").addEventListener("submit", function (e) {
    const mobile = document.querySelector("input[name='mobile']").value;

    if (mobile.length < 10) {
        alert("Please enter a valid mobile number");
        e.preventDefault();
    }
});
