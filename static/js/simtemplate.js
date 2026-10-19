document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;
  const menuButton = document.querySelector("[data-menu-toggle]");
  const toast = document.querySelector(".toast-message");

  menuButton?.addEventListener("click", () => {
    if (window.matchMedia("(max-width: 991.98px)").matches) {
      body.classList.toggle("sidebar-open");
    } else {
      body.classList.toggle("sidebar-collapse");
    }
  });

  document
    .querySelectorAll("[data-print]")
    .forEach((button) =>
      button.addEventListener("click", () => window.print()),
    );

  const chartCanvas = document.querySelector("#activityChart");
  if (chartCanvas && window.Chart) {
    new window.Chart(chartCanvas, {
      type: "bar",
      data: {
        labels: ["Lun.", "Mar.", "Mer.", "Jeu.", "Ven.", "Sam.", "Dim."],
        datasets: [
          {
            label: "Commandes",
            data: [18, 25, 21, 32, 28, 13, 20],
            backgroundColor: "#0d6efd",
            borderRadius: 4,
            maxBarThickness: 20,
          },
          {
            label: "Ventes",
            data: [12, 19, 16, 23, 24, 9, 17],
            backgroundColor: "#a8c8fb",
            borderRadius: 4,
            maxBarThickness: 20,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: { usePointStyle: true, boxWidth: 7, padding: 16 },
          },
        },
        scales: {
          x: { grid: { display: false } },
          y: {
            beginAtZero: true,
            ticks: { precision: 0 },
            border: { display: false },
          },
        },
      },
    });
  }

  document.querySelectorAll("[data-toast]").forEach((button) => {
    button.addEventListener("click", () => {
      if (!toast) return;
      toast.textContent = button.dataset.toast || "Action effectuée.";
      toast.classList.add("show");
      window.setTimeout(() => toast.classList.remove("show"), 2600);
    });
  });

  const tabButtons = [...document.querySelectorAll("[data-tab-target]")];
  tabButtons.forEach((button) =>
    button.addEventListener("click", () => {
      const selected = button.dataset.tabTarget;
      tabButtons.forEach((item) => {
        const active = item === button;
        item.classList.toggle("active", active);
        item.setAttribute("aria-selected", String(active));
      });
      document.querySelectorAll("[data-tab-panel]").forEach((panel) => {
        panel.hidden = panel.dataset.tabPanel !== selected;
      });
    }),
  );

  const stateButtons = [...document.querySelectorAll("[data-state-target]")];
  stateButtons.forEach((button) =>
    button.addEventListener("click", () => {
      const selected = button.dataset.stateTarget;
      stateButtons.forEach((item) => {
        const active = item === button;
        item.classList.toggle("btn-primary", active);
        item.classList.toggle("btn-outline-primary", !active);
        item.setAttribute("aria-pressed", String(active));
      });
      document.querySelectorAll("[data-interface-state]").forEach((panel) => {
        panel.hidden = panel.dataset.interfaceState !== selected;
      });
    }),
  );

  document.querySelectorAll("[data-mail-select]").forEach((button) =>
    button.addEventListener("click", () => {
      const selected = button.dataset.mailSelect;
      document
        .querySelectorAll("[data-mail-select]")
        .forEach((item) => item.classList.toggle("active", item === button));
      document.querySelectorAll("[data-mail-panel]").forEach((panel) => {
        panel.hidden = panel.dataset.mailPanel !== selected;
      });
    }),
  );

  const mailboxSearch = document
    .querySelector("[data-mail-list]")
    ?.parentElement?.querySelector("[data-table-search]");
  mailboxSearch?.addEventListener("input", () => {
    const query = mailboxSearch.value.trim().toLocaleLowerCase("fr");
    document.querySelectorAll("[data-mail-select]").forEach((item) => {
      item.hidden = !item.textContent.toLocaleLowerCase("fr").includes(query);
    });
  });

  const table = document.querySelector("[data-demo-table]");
  if (table) {
    const rows = [...table.querySelectorAll("tbody tr")];
    const search = document.querySelector("[data-table-search]");
    const status = document.querySelector("[data-table-status]");
    const pageSize = 6;
    let currentPage = 1;
    let visibleRows = rows;

    const render = () => {
      const start = (currentPage - 1) * pageSize;
      rows.forEach((row) => {
        row.hidden = true;
      });
      visibleRows.slice(start, start + pageSize).forEach((row) => {
        row.hidden = false;
      });
      const range = document.querySelector("[data-table-range]");
      if (range)
        range.textContent = visibleRows.length
          ? `${start + 1}–${Math.min(start + pageSize, visibleRows.length)} sur ${visibleRows.length}`
          : "0 résultat";
      const pageLabel = document.querySelector("[data-table-page]");
      if (pageLabel)
        pageLabel.textContent = `${currentPage} / ${Math.max(1, Math.ceil(visibleRows.length / pageSize))}`;
      document.querySelectorAll("[data-page-prev]").forEach((button) => {
        button.disabled = currentPage <= 1;
      });
      document.querySelectorAll("[data-page-next]").forEach((button) => {
        button.disabled =
          currentPage >= Math.ceil(visibleRows.length / pageSize);
      });
      const empty = document.querySelector("[data-table-empty]");
      if (empty) empty.hidden = visibleRows.length > 0;
    };

    const filter = () => {
      const query = (search?.value || "").trim().toLocaleLowerCase("fr");
      const selectedStatus = status?.value || "";
      visibleRows = rows.filter((row) => {
        const matchesText = row.textContent
          .toLocaleLowerCase("fr")
          .includes(query);
        const matchesStatus =
          !selectedStatus || row.dataset.status === selectedStatus;
        return matchesText && matchesStatus;
      });
      currentPage = 1;
      render();
    };

    search?.addEventListener("input", filter);
    status?.addEventListener("change", filter);
    document.querySelectorAll("[data-page-prev]").forEach((button) =>
      button.addEventListener("click", () => {
        currentPage = Math.max(1, currentPage - 1);
        render();
      }),
    );
    document.querySelectorAll("[data-page-next]").forEach((button) =>
      button.addEventListener("click", () => {
        currentPage += 1;
        render();
      }),
    );
    document.querySelectorAll("[data-sort-column]").forEach((button) =>
      button.addEventListener("click", () => {
        const column = Number(button.dataset.sortColumn);
        const direction = button.dataset.direction === "asc" ? "desc" : "asc";
        button.dataset.direction = direction;
        rows.sort(
          (a, b) =>
            a.cells[column].textContent.localeCompare(
              b.cells[column].textContent,
              "fr",
              { numeric: true },
            ) * (direction === "asc" ? 1 : -1),
        );
        rows.forEach((row) => table.tBodies[0].append(row));
        filter();
      }),
    );
    document.querySelectorAll("[data-column-toggle]").forEach((toggle) =>
      toggle.addEventListener("change", () => {
        const column = Number(toggle.dataset.columnToggle);
        [...table.rows].forEach((row) => {
          if (row.cells[column]) row.cells[column].hidden = !toggle.checked;
        });
      }),
    );
    document.querySelectorAll("[data-export-csv]").forEach((button) =>
      button.addEventListener("click", () => {
        const values = [
          [...table.tHead.rows[0].cells].map((cell) => cell.textContent.trim()),
          ...visibleRows.map((row) =>
            [...row.cells].map((cell) => cell.textContent.trim()),
          ),
        ];
        const csv = values
          .map((row) =>
            row.map((value) => `"${value.replaceAll('"', '""')}"`).join(";"),
          )
          .join("\r\n");
        const link = document.createElement("a");
        link.href = URL.createObjectURL(
          new Blob(["\ufeff", csv], { type: "text/csv;charset=utf-8" }),
        );
        link.download = "liste-simtemplate.csv";
        link.click();
        URL.revokeObjectURL(link.href);
      }),
    );
    render();
  }

  document.querySelectorAll("[data-delete-row]").forEach((button) =>
    button.addEventListener("click", () => {
      const row = button.closest("tr");
      if (row && window.confirm("Retirer cette ligne de la démonstration ?")) {
        row.remove();
        row.dispatchEvent(new Event("change", { bubbles: true }));
        window.location.reload();
      }
    }),
  );

  const wizard = document.querySelector("[data-wizard]");
  if (wizard) {
    let step = 0;
    const panels = [...wizard.querySelectorAll("[data-wizard-panel]")];
    const indicators = [...wizard.querySelectorAll("[data-wizard-step]")];
    const showStep = () => {
      panels.forEach((panel, index) => {
        panel.hidden = index !== step;
      });
      indicators.forEach((indicator, index) => {
        indicator.classList.toggle("active", index === step);
        indicator.classList.toggle("done", index < step);
      });
      wizard.querySelector("[data-wizard-back]").disabled = step === 0;
      wizard.querySelector("[data-wizard-next]").hidden =
        step === panels.length - 1;
      wizard.querySelector("[data-wizard-submit]").hidden =
        step !== panels.length - 1;
    };
    wizard.querySelector("[data-wizard-back]").addEventListener("click", () => {
      step = Math.max(0, step - 1);
      showStep();
    });
    wizard.querySelector("[data-wizard-next]").addEventListener("click", () => {
      const required = [...panels[step].querySelectorAll("[required]")];
      const invalid = required.find((field) => !field.reportValidity());
      if (!invalid) {
        step = Math.min(panels.length - 1, step + 1);
        showStep();
      }
    });
    wizard.addEventListener("submit", (event) => {
      event.preventDefault();
      showToast("Inscription de démonstration terminée.");
    });
    showStep();
  }

  document.querySelectorAll("[data-date-range]").forEach((form) => {
    const startDate = form.querySelector("[data-start-date]");
    const endDate = form.querySelector("[data-end-date]");
    const startTime = form.querySelector("[data-start-time]");
    const endTime = form.querySelector("[data-end-time]");
    if (!startDate || !endDate) return;
    const validateRange = () => {
      endDate.setCustomValidity("");
      if (startDate.value && endDate.value && endDate.value < startDate.value) {
        endDate.setCustomValidity(
          "La date de fin doit être égale ou postérieure à la date de début.",
        );
        return;
      }
      if (
        startDate.value &&
        endDate.value === startDate.value &&
        startTime?.value &&
        endTime?.value &&
        endTime.value <= startTime.value
      ) {
        endTime.setCustomValidity(
          "L’heure de fin doit être postérieure à l’heure de début.",
        );
        return;
      }
      endTime?.setCustomValidity("");
    };
    [startDate, endDate, startTime, endTime]
      .filter(Boolean)
      .forEach((field) => field.addEventListener("input", validateRange));
    form.addEventListener("submit", validateRange);
  });

  document.querySelectorAll("[data-password-match]").forEach((form) => {
    const password = form.querySelector("[data-password-new]");
    const confirmation = form.querySelector("[data-password-confirm]");
    if (!password || !confirmation) return;
    const validateMatch = () =>
      confirmation.setCustomValidity(
        password.value === confirmation.value
          ? ""
          : "Les deux mots de passe ne correspondent pas.",
      );
    password.addEventListener("input", validateMatch);
    confirmation.addEventListener("input", validateMatch);
    form.addEventListener("submit", validateMatch);
  });

  document.querySelectorAll("[data-demo-form]").forEach((form) =>
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (form.reportValidity())
        showToast(
          form.dataset.success || "Formulaire validé en mode démonstration.",
        );
    }),
  );

  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("show");
    window.setTimeout(() => toast.classList.remove("show"), 2800);
  }
});
