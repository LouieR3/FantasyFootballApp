// Scroll reveal using IntersectionObserver (no libraries)
// reveal on enter + fade-out on exit (reverse scroll)

const items = document.querySelectorAll(".reveal");
const toTop = document.getElementById("toTop");

const io = new IntersectionObserver(
    (entries) => {
        entries.forEach((e) => {
            if (e.isIntersecting) {
                e.target.classList.add("show");
            } else {
                // reverse scroll: fade out when item leaves viewport
                e.target.classList.remove("show");
            }
        });
    },
    {
        threshold: 0.18,
        rootMargin: "0px 0px -8% 0px",
    }
);

items.forEach((el) => io.observe(el));

// Go Top button after 100px
function onScroll() {
    if (window.scrollY > 100) toTop.classList.add("show");
    else toTop.classList.remove("show");
}

window.addEventListener("scroll", onScroll, { passive: true });
onScroll();

toTop.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
});
