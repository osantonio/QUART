function initImcHistorial() {
  const canvas = document.getElementById("pesoChart");
  const mensaje = document.getElementById("pesoMensaje");
  const exportBtn = document.getElementById("pesoExportPng");
  const resetBtn = document.getElementById("pesoResetZoom");
  const endpointEl = document.querySelector("[data-imc-historial-endpoint]");
  if (!canvas || !mensaje || !endpointEl) return;

  const endpoint = endpointEl.getAttribute("data-imc-historial-endpoint");
  let chart = null;

  const buildChart = (labels, values) => {
    if (!window.Chart) return;
    if (chart) {
      chart.data.labels = labels;
      chart.data.datasets[0].data = values;
      chart.update();
      return;
    }
    chart = new Chart(canvas, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Peso (kg)",
            data: values,
            borderColor: "#2563eb",
            backgroundColor: "rgba(37,99,235,0.2)",
            pointRadius: 4,
            pointHoverRadius: 6,
            tension: 0.25,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          tooltip: {
            callbacks: {
              title: (items) => "Fecha: " + items[0].label,
              label: (item) => "Peso: " + item.parsed.y + " kg",
            },
          },
          zoom: {
            pan: {
              enabled: true,
              mode: "x",
            },
            zoom: {
              wheel: { enabled: true },
              pinch: { enabled: true },
              mode: "x",
            },
          },
          legend: { display: false },
        },
        scales: {
          x: {
            ticks: {
              autoSkip: true,
              maxTicksLimit: 8,
            },
          },
          y: {
            beginAtZero: false,
            title: {
              display: true,
              text: "Peso (kg)",
            },
          },
        },
      },
    });
  };

  const cargar = async () => {
    try {
      const res = await fetch(endpoint, { headers: { Accept: "application/json" } });
      if (!res.ok) {
        const data = await res.json().catch(() => null);
        mensaje.textContent = (data && data.error) || "No se pudo cargar el historial de peso.";
        return;
      }
      const data = await res.json();
      const items = data.items || [];
      if (items.length === 0) {
        mensaje.textContent = "No hay registros de peso disponibles.";
        buildChart([], []);
        return;
      }
      const labels = items.map((item) => new Date(item.fecha).toLocaleDateString("es-CO"));
      const values = items.map((item) => item.peso);
      mensaje.textContent = "Mostrando " + items.length + " registros.";
      buildChart(labels, values);
    } catch (err) {
      mensaje.textContent = "Error al cargar datos del servidor.";
    }
  };

  if (exportBtn) {
    exportBtn.addEventListener("click", () => {
      if (!chart) return;
      const link = document.createElement("a");
      link.href = chart.toBase64Image("image/png", 1);
      link.download = "historial-peso.png";
      link.click();
    });
  }

  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      if (chart && chart.resetZoom) chart.resetZoom();
    });
  }

  const scheduleResize = () => {
    if (!chart) return;
    setTimeout(() => {
      if (chart) chart.resize();
    }, 200);
  };

  window.addEventListener("resize", scheduleResize);

  const sidebarToggles = document.querySelectorAll("[data-sidebar-toggle]");
  sidebarToggles.forEach((btn) => {
    btn.addEventListener("click", scheduleResize);
  });

  cargar();
}

document.addEventListener("DOMContentLoaded", initImcHistorial);

