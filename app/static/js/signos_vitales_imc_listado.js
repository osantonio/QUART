document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("imcSearchInput");
  const tableRows = document.querySelectorAll(".imc-row");
  const resultsCount = document.getElementById("imcResultsCount");
  const cards = document.querySelectorAll("[data-imc-card]");

  if (!tableRows.length) return;

  let activeCategoria = "Todos";
  let searchTerm = "";
  const totalItems = tableRows.length;

  const normalizar = (str) =>
    (str || "")
      .toString()
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");

  const updateCounter = (visible) => {
    if (resultsCount) {
      resultsCount.textContent = `Mostrando ${visible} de ${totalItems} beneficiarios`;
    }
  };

  const aplicarFiltros = () => {
    const term = normalizar(searchTerm);
    let visibles = 0;

    tableRows.forEach((row) => {
      const rowCat = row.getAttribute("data-categoria") || "";
      const rowSearch = normalizar(row.getAttribute("data-search") || "");

      const matchCategoria =
        activeCategoria === "Todos" || rowCat === activeCategoria;
      const matchSearch = term === "" || rowSearch.includes(term);

      if (matchCategoria && matchSearch) {
        row.style.display = "";
        visibles++;
      } else {
        row.style.display = "none";
      }
    });

    updateCounter(visibles);
  };

  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      searchTerm = e.target.value || "";

      if (searchTerm === "") {
        activeCategoria = "Todos";
        cards.forEach((c) => c.classList.remove("ring-2", "ring-primary"));
      }

      aplicarFiltros();
    });
  }

  cards.forEach((card) => {
    card.addEventListener("click", () => {
      const categoria = card.getAttribute("data-imc-card") || "Todos";

      if (activeCategoria === categoria) {
        activeCategoria = "Todos";
        cards.forEach((c) => c.classList.remove("ring-2", "ring-primary"));
      } else {
        activeCategoria = categoria;
        cards.forEach((c) => c.classList.remove("ring-2", "ring-primary"));
        if (categoria !== "Todos") {
          card.classList.add("ring-2", "ring-primary");
        }
      }

      aplicarFiltros();
    });
  });

  updateCounter(totalItems);
});
