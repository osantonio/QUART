document.addEventListener("DOMContentLoaded", () => {
  const widget = document.getElementById("widget-imc");
  if (!widget) return;

  const endpoint = widget.getAttribute("data-imc-endpoint");
  const tableBody = document.getElementById("imcTableBody");
  const lastUpdatedEl = document.getElementById("imcLastUpdated");
  const lastUpdatedDot = document.getElementById("imcLastUpdatedDot");
  const totalTextEl = document.getElementById("imcTotalTexto");
  const categoriaSelect = document.getElementById("imcFiltroCategoria");
  const edadMinInput = document.getElementById("imcEdadMin");
  const edadMaxInput = document.getElementById("imcEdadMax");
  const resumenEl = document.getElementById("imcDistribucionResumen");
  const exportPdfBtn = document.getElementById("imcExportPdf");
  const exportExcelBtn = document.getElementById("imcExportExcel");
  const chartCanvas = document.getElementById("imcChart");

  if (!tableBody || !endpoint) return;

  const state = {
    items: [],
    filtered: [],
    signatures: new Map(),
    rows: new Map(),
    chart: null,
  };

  const categoriaColor = (categoria) => {
    if (categoria === "Normal") return "#28a745";
    if (categoria === "Sobrepeso") return "#ffc107";
    if (categoria === "Obesidad") return "#dc3545";
    return null;
  };

  const formatImc = (valor) => {
    if (valor === null || valor === undefined) return "—";
    return Number(valor).toFixed(2);
  };

  const buildRow = (item) => {
    const tr = document.createElement("tr");
    tr.className = "hover:bg-secondary/5 transition-none";
    tr.innerHTML = `
      <td class="px-6 py-3 text-sm" data-imc-nombre></td>
      <td class="px-6 py-3 text-sm" data-imc-edad></td>
      <td class="px-6 py-3 text-sm" data-imc-valor></td>
      <td class="px-6 py-3 text-sm" data-imc-categoria></td>
    `;
    updateRow(tr, item);
    return tr;
  };

  const updateRow = (tr, item) => {
    const nombreCell = tr.querySelector("[data-imc-nombre]");
    const edadCell = tr.querySelector("[data-imc-edad]");
    const imcCell = tr.querySelector("[data-imc-valor]");
    const catCell = tr.querySelector("[data-imc-categoria]");

    if (nombreCell) {
      nombreCell.innerHTML = `<a href="/signos-vitales/${item.id}" class="font-semibold text-foreground/80 hover:underline">${item.nombre}</a>`;
    }
    if (edadCell) {
      edadCell.textContent = item.edad ?? "—";
    }
    if (imcCell) {
      imcCell.textContent = formatImc(item.imc);
    }
    if (catCell) {
      const color = categoriaColor(item.categoria);
      if (color) {
        const textColor = item.categoria === "Sobrepeso" ? "#212529" : "#ffffff";
        catCell.innerHTML = `<span class="px-2 py-1 rounded text-[11px] font-bold uppercase tracking-widest" style="background-color:${color};color:${textColor};">${item.categoria}</span>`;
      } else {
        catCell.textContent = item.categoria;
      }
    }
  };

  const syncTable = (items) => {
    const incoming = new Set();

    items.forEach((item) => {
      incoming.add(item.id);
      const signature = `${item.nombre}|${item.edad}|${item.imc}|${item.categoria}`;
      const existingSig = state.signatures.get(item.id);
      let row = state.rows.get(item.id);

      if (!row) {
        row = buildRow(item);
        tableBody.appendChild(row);
        state.rows.set(item.id, row);
        state.signatures.set(item.id, signature);
        return;
      }

      if (signature !== existingSig) {
        updateRow(row, item);
        state.signatures.set(item.id, signature);
      }
    });

    Array.from(state.rows.keys()).forEach((id) => {
      if (!incoming.has(id)) {
        const row = state.rows.get(id);
        if (row) row.remove();
        state.rows.delete(id);
        state.signatures.delete(id);
      }
    });

    if (items.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="4" class="px-6 py-12 text-center text-sm text-muted-foreground/60">
            No hay datos disponibles
          </td>
        </tr>
      `;
      state.rows.clear();
      state.signatures.clear();
    }
  };

  const computeDistribucion = (items) => {
    const categorias = ["Bajo peso", "Normal", "Sobrepeso", "Obesidad"];
    const counts = { "Bajo peso": 0, Normal: 0, Sobrepeso: 0, Obesidad: 0 };
    let totalValidos = 0;

    items.forEach((item) => {
      if (item.imc === null || item.imc === undefined) return;
      if (counts[item.categoria] === undefined) return;
      counts[item.categoria] += 1;
      totalValidos += 1;
    });

    return categorias.map((cat) => {
      const count = counts[cat];
      const porcentaje = totalValidos > 0 ? (count / totalValidos) * 100 : 0;
      return { categoria: cat, cantidad: count, porcentaje };
    });
  };

  const updateResumen = (distribucion) => {
    if (!resumenEl) return;
    resumenEl.innerHTML = "";
    distribucion.forEach((item) => {
      const span = document.createElement("span");
      span.className = "px-2 py-1 rounded border border-border/40";
      span.textContent = `${item.categoria}: ${item.cantidad} (${item.porcentaje.toFixed(1)}%)`;
      resumenEl.appendChild(span);
    });
  };

  const updateChart = (items) => {
    if (!window.Chart || !chartCanvas) return;
    const distribucion = computeDistribucion(items);
    const labels = distribucion.map(
      (d) => `${d.categoria} (${d.porcentaje.toFixed(1)}% · ${d.cantidad})`
    );
    const dataValues = distribucion.map((d) => d.cantidad);
    const colors = ["#6c757d", "#28a745", "#ffc107", "#dc3545"];

    if (!state.chart) {
      state.chart = new Chart(chartCanvas, {
        type: "bar",
        data: {
          labels,
          datasets: [
            {
              data: dataValues,
              backgroundColor: colors,
            },
          ],
        },
        options: {
          indexAxis: "y",
          responsive: true,
          plugins: {
            legend: { display: false },
          },
          scales: {
            x: { beginAtZero: true },
          },
        },
      });
    } else {
      state.chart.data.labels = labels;
      state.chart.data.datasets[0].data = dataValues;
      state.chart.update();
    }

    updateResumen(distribucion);
  };

  const applyFilters = () => {
    const categoria = categoriaSelect.value;
    const minEdad = edadMinInput.value ? Number(edadMinInput.value) : null;
    const maxEdad = edadMaxInput.value ? Number(edadMaxInput.value) : null;

    state.filtered = state.items.filter((item) => {
      if (categoria !== "Todas" && item.categoria !== categoria) return false;
      if (minEdad !== null && item.edad < minEdad) return false;
      if (maxEdad !== null && item.edad > maxEdad) return false;
      return true;
    });

    if (totalTextEl) {
      totalTextEl.textContent = `Total: ${state.filtered.length}`;
    }

    syncTable(state.filtered);
    updateChart(state.filtered);
  };

  const cargarDatos = async () => {
    try {
      const res = await fetch(endpoint, {
        headers: { Accept: "application/json" },
      });
      if (!res.ok) return;

      const data = await res.json();
      state.items = data.items || [];

      const hora = data.actualizado_en ? new Date(data.actualizado_en) : new Date();
      if (lastUpdatedEl) {
        lastUpdatedEl.textContent = hora.toLocaleString("es-CO");
      }
      if (lastUpdatedDot) {
        lastUpdatedDot.classList.remove("bg-primary/60");
        lastUpdatedDot.classList.add("bg-primary");
        setTimeout(() => {
          lastUpdatedDot.classList.remove("bg-primary");
          lastUpdatedDot.classList.add("bg-primary/60");
        }, 600);
      }

      applyFilters();
    } catch {
      if (lastUpdatedEl) {
        lastUpdatedEl.textContent = "Sin conexión";
      }
    }
  };

  const exportPdf = () => {
    if (!window.jspdf || !window.jspdf.jsPDF) return;
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    doc.setFontSize(18);
    doc.text("APS", 14, 16);
    doc.setFontSize(12);
    doc.text("Asilo Perpetuo Socorro", 14, 24);
    doc.setFontSize(10);
    doc.text(`Reporte IMC - ${new Date().toLocaleDateString("es-CO")}`, 14, 32);

    let y = 40;
    doc.setFontSize(11);
    doc.text("Beneficiario", 14, y);
    doc.text("Edad", 110, y);
    doc.text("IMC", 130, y);
    doc.text("Categoría", 150, y);
    y += 6;

    state.filtered.forEach((item) => {
      if (y > 280) {
        doc.addPage();
        y = 20;
      }
      doc.text(String(item.nombre), 14, y);
      doc.text(String(item.edad ?? "—"), 110, y);
      doc.text(String(formatImc(item.imc)), 130, y);
      doc.text(String(item.categoria), 150, y);
      y += 6;
    });

    doc.save("reporte-imc.pdf");
  };

  const exportExcel = () => {
    if (!window.XLSX) return;
    const rows = state.filtered.map((item) => ({
      Beneficiario: item.nombre,
      Edad: item.edad,
      IMC:
        item.imc === null || item.imc === undefined
          ? ""
          : Number(item.imc).toFixed(2),
      Categoria: item.categoria,
    }));

    const worksheet = XLSX.utils.json_to_sheet(rows);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "IMC");
    XLSX.writeFile(workbook, "reporte-imc.xlsx");
  };

  if (categoriaSelect) {
    categoriaSelect.addEventListener("change", applyFilters);
  }
  if (edadMinInput) {
    edadMinInput.addEventListener("input", applyFilters);
  }
  if (edadMaxInput) {
    edadMaxInput.addEventListener("input", applyFilters);
  }
  if (exportPdfBtn) {
    exportPdfBtn.addEventListener("click", exportPdf);
  }
  if (exportExcelBtn) {
    exportExcelBtn.addEventListener("click", exportExcel);
  }

  cargarDatos();
  setInterval(cargarDatos, 30000);
});

