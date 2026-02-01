function initSidebar() {
  const aside = document.querySelector("[data-sidebar-lg]");
  const overlay = document.querySelector("[data-sidebar-overlay]");
  const panel = document.querySelector("[data-sidebar-panel]");
  const backdrop = document.querySelector("[data-sidebar-backdrop]");
  const storageKey = "sidebar-lg-state";

  const isLg = () =>
    window.matchMedia && window.matchMedia("(min-width: 1024px)").matches;

  // Desktop Toggle Logic
  const toggleDesktop = () => {
    if (!aside) return;
    const isHidden = aside.classList.contains("lg:hidden");
    if (isHidden) {
      aside.classList.remove("lg:hidden");
      aside.classList.add("lg:block");
      localStorage.setItem(storageKey, "visible");
    } else {
      aside.classList.remove("lg:block");
      aside.classList.add("lg:hidden");
      localStorage.setItem(storageKey, "hidden");
    }
  };

  const initDesktopState = () => {
    if (!aside) return;
    const stored = localStorage.getItem(storageKey);
    if (stored === "hidden") {
      aside.classList.add("lg:hidden");
      aside.classList.remove("lg:block");
    } else if (stored === "visible") {
      aside.classList.remove("lg:hidden");
      aside.classList.add("lg:block");
    }
  };

  // Mobile Toggle Logic
  const openMobile = () => {
    if (!overlay || !panel || !backdrop) return;
    overlay.classList.remove("pointer-events-none");
    panel.classList.remove("-translate-x-full");
    backdrop.classList.remove("opacity-0", "pointer-events-none");
    backdrop.classList.add("opacity-100");
  };

  const closeMobile = () => {
    if (!overlay || !panel || !backdrop) return;
    panel.classList.add("-translate-x-full");
    backdrop.classList.add("opacity-0", "pointer-events-none");
    backdrop.classList.remove("opacity-100");
    setTimeout(() => {
      overlay.classList.add("pointer-events-none");
    }, 300);
  };

  // Event Listeners for Sidebar Toggles
  const toggleButtons = document.querySelectorAll("[data-sidebar-toggle]");
  toggleButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      if (isLg()) {
        toggleDesktop();
      } else {
        openMobile();
      }
    });
  });

  // Event Listeners for Submenus
  const submenuToggles = document.querySelectorAll("[data-submenu-toggle]");
  submenuToggles.forEach((toggle) => {
    toggle.addEventListener("click", (e) => {
      e.preventDefault();
      const submenuId = toggle.getAttribute("data-submenu-toggle");
      const submenu = document.getElementById(submenuId);
      const chevron = toggle.querySelector("[data-submenu-chevron]");

      if (submenu) {
        submenu.classList.toggle("hidden");
        if (chevron) {
          chevron.classList.toggle("rotate-180");
        }
      }
    });
  });

  // Mobile Close Actions
  const closeButtons = document.querySelectorAll("[data-sidebar-close]");
  closeButtons.forEach((btn) => btn.addEventListener("click", closeMobile));

  if (backdrop) {
    backdrop.addEventListener("click", closeMobile);
  }

  // Initialize
  initDesktopState();
}

document.addEventListener("DOMContentLoaded", initSidebar);


