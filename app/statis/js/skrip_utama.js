/**
 * Skrip Utama - AI Proposal Reviewer
 *
 * JavaScript untuk menangani interaksi pengguna,
 * upload file, dan submission review proposal.
 */

// ============================================
// KONSTANTA
// ============================================
const UKURAN_MAKS_MB = 10;
const EKSTENSI_DIDUKUNG = [".pdf", ".docx"];
const API_BASE_URL = "/api";

// ============================================
// STATE
// ============================================
let berkasYangDipilih = null;
let sidebarCollapsed = false;

// ============================================
// UTILITAS
// ============================================

/**
 * Format ukuran file ke string yang mudah dibaca.
 * @param {number} bytes - Ukuran dalam bytes
 * @returns {string} - Ukuran yang diformat
 */
function formatUkuranBerkas(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const ukuran = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + ukuran[i];
}

/**
 * Validasi file yang dipilih.
 * @param {File} berkas - File yang akan divalidasi
 * @returns {object} - { valid: boolean, pesan: string }
 */
function validasiBerkas(berkas) {
  // Cek ekstensi
  const namaBerkas = berkas.name.toLowerCase();
  const ekstensiValid = EKSTENSI_DIDUKUNG.some((ext) =>
    namaBerkas.endsWith(ext)
  );

  if (!ekstensiValid) {
    return {
      valid: false,
      pesan: `Format tidak didukung. Gunakan: ${EKSTENSI_DIDUKUNG.join(", ")}`,
    };
  }

  // Cek ukuran
  const ukuranMaksByte = UKURAN_MAKS_MB * 1024 * 1024;
  if (berkas.size > ukuranMaksByte) {
    return {
      valid: false,
      pesan: `Ukuran file melebihi batas ${UKURAN_MAKS_MB} MB`,
    };
  }

  return { valid: true, pesan: "" };
}

/**
 * Menampilkan atau menyembunyikan loading overlay.
 * @param {boolean} tampilkan - true untuk menampilkan
 */
function toggleLoading(tampilkan) {
  const overlay = document.getElementById("loadingOverlay");
  if (overlay) {
    overlay.classList.toggle("active", tampilkan);
  }
}

/**
 * Menampilkan notifikasi toast.
 * @param {string} pesan - Pesan notifikasi
 * @param {string} tipe - Tipe notifikasi (sukses, error, peringatan)
 */
function tampilkanNotifikasi(pesan, tipe = "info") {
  // Untuk sementara gunakan alert
  alert(pesan);
}

// ============================================
// SIDEBAR NAVIGATION
// ============================================

/**
 * Toggle sidebar collapsed state.
 */
function toggleSidebar() {
  const sidebar = document.querySelector(".sidebar");
  const mainContent = document.querySelector(".main-content");

  sidebarCollapsed = !sidebarCollapsed;

  if (sidebar) {
    sidebar.classList.toggle("collapsed", sidebarCollapsed);
  }
  if (mainContent) {
    mainContent.classList.toggle("sidebar-collapsed", sidebarCollapsed);
  }

  // Simpan preferensi
  localStorage.setItem("sidebarCollapsed", sidebarCollapsed);
}

/**
 * Toggle mobile sidebar.
 */
function toggleMobileSidebar() {
  const sidebar = document.querySelector(".sidebar");
  const overlay = document.querySelector(".sidebar-overlay");

  if (sidebar) {
    sidebar.classList.toggle("mobile-open");
  }
  if (overlay) {
    overlay.classList.toggle("active");
  }
}

/**
 * Toggle tema gelap/terang.
 */
function toggleTema() {
  const root = document.documentElement;
  const temaSekarang = root.getAttribute("data-tema");
  const temaBaru = temaSekarang === "gelap" ? "terang" : "gelap";

  root.setAttribute("data-tema", temaBaru);
  localStorage.setItem("tema", temaBaru);

  // Update ikon
  const ikon = document.querySelector(".toggle-tema .nav-icon");
  if (ikon) {
    ikon.innerHTML =
      temaBaru === "gelap"
        ? '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>'
        : '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>';
  }
}

// ============================================
// FILE UPLOAD
// ============================================

/**
 * Inisialisasi zona upload dengan drag-and-drop.
 */
function initUploadZone() {
  const uploadZone = document.getElementById("uploadZone");
  const fileInput = document.getElementById("berkasProposal");

  if (!uploadZone || !fileInput) return;

  // Drag events
  ["dragenter", "dragover"].forEach((eventType) => {
    uploadZone.addEventListener(eventType, (e) => {
      e.preventDefault();
      uploadZone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach((eventType) => {
    uploadZone.addEventListener(eventType, (e) => {
      e.preventDefault();
      uploadZone.classList.remove("dragover");
    });
  });

  // Drop handler
  uploadZone.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  });

  // File input change
  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      handleFileSelect(e.target.files[0]);
    }
  });
}

/**
 * Handle file selection.
 * @param {File} berkas - File yang dipilih
 */
function handleFileSelect(berkas) {
  const uploadZone = document.getElementById("uploadZone");
  const uploadContent = document.querySelector(".upload-content");
  const uploadPreview = document.getElementById("uploadPreview");

  // Validasi
  const validasi = validasiBerkas(berkas);
  if (!validasi.valid) {
    tampilkanNotifikasi(validasi.pesan, "error");
    return;
  }

  berkasYangDipilih = berkas;

  // Update UI
  if (uploadZone) {
    uploadZone.classList.add("has-file");
  }
  if (uploadContent) {
    uploadContent.style.display = "none";
  }
  if (uploadPreview) {
    uploadPreview.style.display = "flex";

    // Update preview info
    const fileNameEl = uploadPreview.querySelector(".file-name");
    const fileSizeEl = uploadPreview.querySelector(".file-size");

    if (fileNameEl) fileNameEl.textContent = berkas.name;
    if (fileSizeEl) fileSizeEl.textContent = formatUkuranBerkas(berkas.size);
  }
}

/**
 * Reset file upload.
 */
function resetUpload() {
  berkasYangDipilih = null;

  const uploadZone = document.getElementById("uploadZone");
  const uploadContent = document.querySelector(".upload-content");
  const uploadPreview = document.getElementById("uploadPreview");
  const fileInput = document.getElementById("berkasProposal");

  if (uploadZone) uploadZone.classList.remove("has-file");
  if (uploadContent) uploadContent.style.display = "block";
  if (uploadPreview) uploadPreview.style.display = "none";
  if (fileInput) fileInput.value = "";
}

// ============================================
// FORM SUBMISSION
// ============================================

/**
 * Submit form review proposal.
 * @param {Event} e - Event object
 */
async function submitReview(e) {
  e.preventDefault();

  // Validasi file
  if (!berkasYangDipilih) {
    tampilkanNotifikasi("Silakan pilih file proposal terlebih dahulu", "error");
    return;
  }

  // Ambil jenis proposal
  const jenisProposal = document.getElementById("jenisProposal")?.value;
  if (!jenisProposal) {
    tampilkanNotifikasi("Silakan pilih jenis proposal", "error");
    return;
  }

  // Show loading
  toggleLoading(true);

  try {
    // Prepare form data
    const formData = new FormData();
    formData.append("berkas", berkasYangDipilih);
    formData.append("jenis_proposal", jenisProposal);

    // Submit ke API
    const response = await fetch(`${API_BASE_URL}/review`, {
      method: "POST",
      body: formData,
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.detail || "Terjadi kesalahan");
    }

    // Tampilkan hasil
    if (result.berhasil && result.data) {
      tampilkanHasil(result.data);
    } else {
      throw new Error(result.pesan || "Review gagal");
    }
  } catch (error) {
    console.error("Error:", error);
    tampilkanNotifikasi(error.message, "error");
  } finally {
    toggleLoading(false);
  }
}

// ============================================
// HASIL DISPLAY
// ============================================

/**
 * Tampilkan hasil evaluasi.
 * @param {object} hasil - Objek hasil evaluasi
 */
function tampilkanHasil(hasil) {
  const hasilContainer = document.getElementById("hasilContainer");
  if (!hasilContainer) return;

  // Update skor
  const skorNilai = document.getElementById("skorNilai");
  const skorBar = document.getElementById("skorBarFill");

  if (skorNilai) skorNilai.textContent = hasil.skor;
  if (skorBar) skorBar.style.width = `${hasil.skor}%`;

  // Update detail skor jika ada
  if (hasil.detail_skor) {
    updateDetailSkor(hasil.detail_skor);
  }

  // Update kekuatan
  updateFeedbackList("daftarKekuatan", hasil.daftar_kekuatan, "kekuatan");

  // Update kelemahan
  updateFeedbackList("daftarKelemahan", hasil.daftar_kelemahan, "kelemahan");

  // Update saran
  updateFeedbackList("daftarSaran", hasil.daftar_saran, "saran");

  // Update ringkasan
  const ringkasanText = document.getElementById("ringkasanText");
  if (ringkasanText) {
    ringkasanText.textContent = hasil.ringkasan;
  }

  // Tampilkan container hasil
  hasilContainer.classList.add("visible");

  // Scroll ke hasil
  hasilContainer.scrollIntoView({ behavior: "smooth" });
}

/**
 * Update detail skor cards.
 * @param {object} detailSkor - Objek detail skor
 */
function updateDetailSkor(detailSkor) {
  const detailGrid = document.getElementById("detailSkorGrid");
  if (!detailGrid) return;

  const aspekLabels = {
    latar_belakang: "Latar Belakang",
    formulasi_masalah: "Formulasi Masalah",
    tujuan: "Tujuan",
    metodologi: "Metodologi",
    luaran: "Luaran",
  };

  let html = "";
  for (const [key, value] of Object.entries(detailSkor)) {
    const label = aspekLabels[key] || key;
    const persen = (value / 20) * 100;

    html += `
            <div class="detail-card">
                <div class="detail-card-header">
                    <span class="detail-card-title">${label}</span>
                    <span class="detail-card-skor">${value}/20</span>
                </div>
                <div class="detail-bar">
                    <div class="detail-bar-fill" style="width: ${persen}%"></div>
                </div>
            </div>
        `;
  }

  detailGrid.innerHTML = html;
}

/**
 * Update feedback list (kekuatan/kelemahan/saran).
 * @param {string} elementId - ID element container
 * @param {array} items - Array of items
 * @param {string} tipe - Tipe feedback
 */
function updateFeedbackList(elementId, items, tipe) {
  const container = document.getElementById(elementId);
  if (!container || !items) return;

  const icons = {
    kekuatan:
      '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
    kelemahan:
      '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    saran:
      '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
  };

  let html = "";
  items.forEach((item) => {
    html += `
            <li class="feedback-item ${tipe}">
                <svg class="feedback-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    ${icons[tipe]}
                </svg>
                <span>${item}</span>
            </li>
        `;
  });

  container.innerHTML = html;
}

/**
 * Reset dan sembunyikan hasil.
 */
function resetHasil() {
  const hasilContainer = document.getElementById("hasilContainer");
  if (hasilContainer) {
    hasilContainer.classList.remove("visible");
  }
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener("DOMContentLoaded", () => {
  // Load preferensi tema
  const temaTersimpan = localStorage.getItem("tema");
  if (temaTersimpan) {
    document.documentElement.setAttribute("data-tema", temaTersimpan);
  }

  // Load preferensi sidebar
  const sidebarTersimpan = localStorage.getItem("sidebarCollapsed");
  if (sidebarTersimpan === "true") {
    toggleSidebar();
  }

  // Init upload zone
  initUploadZone();

  // Form submit handler
  const formReview = document.getElementById("formReview");
  if (formReview) {
    formReview.addEventListener("submit", submitReview);
  }

  // Sidebar toggle
  const btnToggleSidebar = document.querySelector(".sidebar-toggle");
  if (btnToggleSidebar) {
    btnToggleSidebar.addEventListener("click", toggleSidebar);
  }

  // Mobile menu
  const btnMobileMenu = document.querySelector(".mobile-menu-btn");
  if (btnMobileMenu) {
    btnMobileMenu.addEventListener("click", toggleMobileSidebar);
  }

  // Sidebar overlay (close on click)
  const sidebarOverlay = document.querySelector(".sidebar-overlay");
  if (sidebarOverlay) {
    sidebarOverlay.addEventListener("click", toggleMobileSidebar);
  }

  // Tema toggle
  const btnToggleTema = document.querySelector(".toggle-tema");
  if (btnToggleTema) {
    btnToggleTema.addEventListener("click", toggleTema);
  }

  // Navigation links
  const navLinks = document.querySelectorAll(".nav-link");
  navLinks.forEach((link) => {
    link.addEventListener("click", handleNavigation);
  });

  // Load halaman sesuai hash
  const hash = window.location.hash || "#beranda";
  navigasiKe(hash.replace("#", ""));

  console.log("AI Proposal Reviewer - Berhasil diinisialisasi");
});

// ============================================
// NAVIGATION
// ============================================

/**
 * Handle klik navigasi.
 */
function handleNavigation(e) {
  e.preventDefault();
  const href = this.getAttribute("href");
  const page = href.replace("#", "");

  navigasiKe(page);
  window.location.hash = href;

  // Close mobile sidebar
  if (window.innerWidth <= 768) {
    toggleMobileSidebar();
  }
}

/**
 * Navigasi ke halaman tertentu.
 * @param {string} page - Nama halaman (beranda/review/riwayat/pengaturan)
 */
function navigasiKe(page) {
  // Update active nav link
  const navLinks = document.querySelectorAll(".nav-link");
  navLinks.forEach((link) => {
    const href = link.getAttribute("href").replace("#", "");
    if (href === page || (href === "/" && page === "beranda")) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });

  // Show/hide sections
  const sections = document.querySelectorAll(".content-section");
  sections.forEach((section) => {
    section.classList.remove("active");
  });

  let targetSection;
  switch (page) {
    case "review":
      targetSection = document.getElementById("section-beranda");
      break;
    case "riwayat":
      targetSection = document.getElementById("section-riwayat");
      muatRiwayat();
      muatStatistik();
      break;
    case "pengaturan":
      targetSection = document.getElementById("section-pengaturan");
      muatPengaturan();
      break;
    default:
      targetSection = document.getElementById("section-beranda");
  }

  if (targetSection) {
    targetSection.classList.add("active");
  }
}

// ============================================
// RIWAYAT REVIEW
// ============================================

/**
 * Memuat riwayat review dari API.
 */
async function muatRiwayat() {
  const container = document.getElementById("riwayatList");

  try {
    container.innerHTML =
      '<div class="loading-spinner" style="margin: 2rem auto;"></div>';

    const response = await fetch(`${API_BASE_URL}/riwayat?limit=50`);
    const data = await response.json();

    if (!data.berhasil || !data.data || data.data.length === 0) {
      container.innerHTML = `
                <div class="empty-state">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 48px; height: 48px; opacity: 0.3;">
                        <path d="M9 11l3 3L22 4" />
                        <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
                    </svg>
                    <p>Belum ada riwayat review</p>
                </div>
            `;
      return;
    }

    container.innerHTML = data.data
      .map(
        (item) => `
            <div class="riwayat-item" onclick="tampilkanDetailRiwayat(${
              item.id
            })">
                <div class="riwayat-header">
                    <div>
                        <div class="riwayat-title">
                            📄 ${escapeHtml(item.nama_berkas)}
                            <span class="badge badge-${
                              item.jenis_proposal
                            }">${item.jenis_proposal.toUpperCase()}</span>
                        </div>
                        <div class="riwayat-meta">
                            <span>📅 ${formatTanggal(
                              item.tanggal_review
                            )}</span>
                            ${
                              item.ukuran_berkas
                                ? `<span>📦 ${formatUkuranBerkas(
                                    item.ukuran_berkas
                                  )}</span>`
                                : ""
                            }
                        </div>
                    </div>
                    <div class="riwayat-skor">${item.skor}</div>
                </div>
                <div class="riwayat-actions" onclick="event.stopPropagation()">
                    <button class="btn btn-ghost btn-sm" onclick="tampilkanDetailRiwayat(${
                      item.id
                    })">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 16px; height: 16px;">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                            <circle cx="12" cy="12" r="3" />
                        </svg>
                        Lihat Detail
                    </button>
                    <button class="btn btn-ghost btn-sm" onclick="hapusRiwayat(${
                      item.id
                    })" style="color: var(--warna-bahaya);">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 16px; height: 16px;">
                            <polyline points="3 6 5 6 21 6" />
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                        </svg>
                        Hapus
                    </button>
                </div>
            </div>
        `
      )
      .join("");
  } catch (error) {
    console.error("Gagal memuat riwayat:", error);
    container.innerHTML = `
            <div class="empty-state">
                <p style="color: var(--warna-bahaya);">❌ Gagal memuat riwayat</p>
                <button class="btn btn-primer btn-sm" onclick="muatRiwayat()">Coba Lagi</button>
            </div>
        `;
  }
}

/**
 * Memuat statistik review.
 */
async function muatStatistik() {
  try {
    const response = await fetch(`${API_BASE_URL}/statistik`);
    const data = await response.json();

    if (data.berhasil && data.data) {
      const stats = data.data;
      document.getElementById("statTotalReview").textContent =
        stats.total_review || 0;
      document.getElementById("statRataRata").textContent =
        stats.rata_rata_skor || 0;
      document.getElementById("statTertinggi").textContent =
        stats.skor_tertinggi || 0;
      document.getElementById("statTerendah").textContent =
        stats.skor_terendah || "-";
    }
  } catch (error) {
    console.error("Gagal memuat statistik:", error);
  }
}

/**
 * Menampilkan detail riwayat review.
 */
async function tampilkanDetailRiwayat(id) {
  try {
    const response = await fetch(`${API_BASE_URL}/riwayat/${id}`);
    const data = await response.json();

    if (data.berhasil && data.data) {
      const review = data.data;

      // Tampilkan di section beranda
      navigasiKe("review");

      // Populate hasil
      tampilkanHasil({
        skor: review.skor,
        detail_skor: review.detail_skor,
        daftar_kekuatan: review.daftar_kekuatan,
        daftar_kelemahan: review.daftar_kelemahan,
        daftar_saran: review.daftar_saran,
        ringkasan: review.ringkasan,
      });
    }
  } catch (error) {
    console.error("Gagal memuat detail:", error);
    tampilkanNotifikasi("Gagal memuat detail review", "error");
  }
}

/**
 * Menghapus riwayat review.
 */
async function hapusRiwayat(id) {
  if (!confirm("Yakin ingin menghapus review ini?")) {
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/riwayat/${id}`, {
      method: "DELETE",
    });
    const data = await response.json();

    if (data.berhasil) {
      tampilkanNotifikasi("Review berhasil dihapus", "success");
      muatRiwayat();
      muatStatistik();
    } else {
      tampilkanNotifikasi("Gagal menghapus review", "error");
    }
  } catch (error) {
    console.error("Gagal menghapus review:", error);
    tampilkanNotifikasi("Gagal menghapus review", "error");
  }
}

// ============================================
// PENGATURAN
// ============================================

/**
 * Memuat pengaturan aplikasi.
 */
async function muatPengaturan() {
  try {
    const response = await fetch(`${API_BASE_URL}/pengaturan`);
    const data = await response.json();

    if (data.berhasil && data.data) {
      const config = data.data;
      document.getElementById("settingModel").textContent = config.model || "-";
      document.getElementById("settingEndpoint").textContent =
        config.endpoint || "-";
      document.getElementById("settingMaxSize").textContent = `${
        config.ukuran_maks_mb || 10
      } MB`;

      const apiKeyBadge = config.api_key_tersedia
        ? '<span class="badge badge-success">✓ Tersedia</span>'
        : '<span class="badge badge-warning">❌ Tidak Tersedia</span>';
      document.getElementById("settingApiKey").innerHTML = apiKeyBadge;
    }
  } catch (error) {
    console.error("Gagal memuat pengaturan:", error);
  }
}

// Radio buttons untuk tema
document.addEventListener("DOMContentLoaded", function () {
  const radioTema = document.querySelectorAll('input[name="tema"]');
  radioTema.forEach((radio) => {
    radio.addEventListener("change", function () {
      if (this.value === "gelap") {
        document.documentElement.setAttribute("data-tema", "gelap");
        localStorage.setItem("tema", "gelap");
      } else {
        document.documentElement.setAttribute("data-tema", "terang");
        localStorage.setItem("tema", "terang");
      }
    });
  });

  // Set initial radio state
  const temaSaat = localStorage.getItem("tema") || "terang";
  document.querySelector(
    `input[name="tema"][value="${temaSaat}"]`
  ).checked = true;
});

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Format tanggal ke string yang mudah dibaca.
 */
function formatTanggal(tanggalStr) {
  const tanggal = new Date(tanggalStr);
  const options = {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  };
  return tanggal.toLocaleDateString("id-ID", options);
}

/**
 * Escape HTML untuk mencegah XSS.
 */
function escapeHtml(text) {
  const map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  };
  return text.replace(/[&<>"']/g, (m) => map[m]);
}
