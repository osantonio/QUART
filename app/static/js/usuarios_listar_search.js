document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("searchInput");
  const tableRows = document.querySelectorAll(".user-row");
  const emptyState = document.getElementById("emptyState");
  const tableBody = document.getElementById("userTableBody");
  const resultsCount = document.getElementById("resultsCount");

  if (!searchInput) {
    return;
  }

  const totalItems = tableRows.length;

  const updateCounter = (visibleCount) => {
    if (resultsCount) {
      const entity = resultsCount.getAttribute("data-entity") || "elementos";
      resultsCount.textContent = `Mostrando ${visibleCount} de ${totalItems} ${entity}`;
    }
  };

  // Inicializar contador al cargar la página
  updateCounter(totalItems);

  searchInput.addEventListener("input", function (e) {
    const searchTerm = e.target.value.toLowerCase().trim();
    let visibleCount = 0;

    tableRows.forEach((row) => {
      const searchData = (row.getAttribute("data-search") || "").toLowerCase();
      if (searchData.includes(searchTerm)) {
        row.style.display = "";
        visibleCount++;
      } else {
        row.style.display = "none";
      }
    });

    updateCounter(visibleCount);

    // Gestionar estado vacío
    if (visibleCount === 0 && searchTerm !== "") {
      if (tableBody) tableBody.style.display = "none";
      if (emptyState) emptyState.classList.remove("hidden");
    } else {
      if (tableBody) tableBody.style.display = "";
      if (emptyState) emptyState.classList.add("hidden");
    }
  });
});
