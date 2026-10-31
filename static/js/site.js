// Mobile menu
const toggle = document.querySelector(".menu-toggle");
const nav = document.getElementById("nav");
toggle?.addEventListener("click", () => {
  const open = nav.classList.toggle("open");
  toggle.setAttribute("aria-expanded", open);
});

// Category filter on the auction examples page
document.querySelectorAll(".chip[data-filter]").forEach((chip) => {
  chip.addEventListener("click", () => {
    const cat = chip.dataset.filter;
    document.querySelectorAll(".chip").forEach((c) => c.classList.toggle("is-active", c === chip));
    document.querySelectorAll(".card[data-cat]").forEach((card) => {
      card.hidden = cat !== "all" && card.dataset.cat !== cat;
    });
  });
});

// Hide open auctions whose date has passed (the site may not have been rebuilt yet)
const today = new Date().toISOString().slice(0, 10);
document.querySelectorAll(".card[data-until]").forEach((card) => {
  if (card.dataset.until < today) card.remove();
});
