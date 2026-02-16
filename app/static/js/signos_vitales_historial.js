document.addEventListener("DOMContentLoaded", () => {
  const tipoButtons = document.querySelectorAll("[data-filter-tipo]");
  const searchInput = document.getElementById("searchHistorialInput");
  const rows = Array.from(document.querySelectorAll("tbody tr"));

  let currentTipo = "";

  function aplicarFiltros() {
    const term = (searchInput?.value || "").toLowerCase().trim();
    let visibles = 0;

    rows.forEach((row) => {
      const rowTipo = (row.dataset.tipo || "").toLowerCase();
      const rowSearch = (row.dataset.search || "").toLowerCase();

      const coincideTipo = !currentTipo || rowTipo === currentTipo;
      const coincideTexto = !term || rowSearch.includes(term);

      if (coincideTipo && coincideTexto) {
        row.classList.remove("hidden");
        visibles += 1;
      } else {
        row.classList.add("hidden");
      }
    });

    const counter = document.getElementById("resultsHistorialCount");
    if (counter) {
      counter.textContent = `Mostrando ${visibles} registros`;
    }
  }

  tipoButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const tipo = (btn.dataset.filterTipo || "").toLowerCase();

      if (currentTipo === tipo) {
        currentTipo = "";
        tipoButtons.forEach((b) => b.classList.remove("ring-2", "ring-primary"));
      } else {
        currentTipo = tipo;
        tipoButtons.forEach((b) => b.classList.remove("ring-2", "ring-primary"));
        btn.classList.add("ring-2", "ring-primary");
      }

      aplicarFiltros();
    });
  });

  if (searchInput) {
    searchInput.addEventListener("input", aplicarFiltros);
  }
});
