function setupUserMenu() {
  const button = document.getElementById("user-menu-button");
  const menu = document.getElementById("user-menu");
  if (!button || !menu) {
    return;
  }
  button.addEventListener("click", (event) => {
    event.stopPropagation();
    menu.classList.toggle("hidden");
  });
  document.addEventListener("click", () => {
    if (!menu.classList.contains("hidden")) {
      menu.classList.add("hidden");
    }
  });
}

window.addEventListener("DOMContentLoaded", setupUserMenu);

