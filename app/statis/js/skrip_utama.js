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
const EKSTENSI_DIDUKUNG = ['.pdf', '.docx'];
const API_BASE_URL = '/api';

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
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const ukuran = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + ukuran[i];
}

/**
 * Validasi file yang dipilih.
 * @param {File} berkas - File yang akan divalidasi
 * @returns {object} - { valid: boolean, pesan: string }
 */
function validasiBerkas(berkas) {
    // Cek ekstensi
    const namaBerkas = berkas.name.toLowerCase();
    const ekstensiValid = EKSTENSI_DIDUKUNG.some(ext => namaBerkas.endsWith(ext));
    
    if (!ekstensiValid) {
        return {
            valid: false,
            pesan: `Format tidak didukung. Gunakan: ${EKSTENSI_DIDUKUNG.join(', ')}`
        };
    }

    // Cek ukuran
    const ukuranMaksByte = UKURAN_MAKS_MB * 1024 * 1024;
    if (berkas.size > ukuranMaksByte) {
        return {
            valid: false,
            pesan: `Ukuran file melebihi batas ${UKURAN_MAKS_MB} MB`
        };
    }

    return { valid: true, pesan: '' };
}

/**
 * Menampilkan atau menyembunyikan loading overlay.
 * @param {boolean} tampilkan - true untuk menampilkan
 */
function toggleLoading(tampilkan) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.toggle('active', tampilkan);
    }
}

/**
 * Menampilkan notifikasi toast.
 * @param {string} pesan - Pesan notifikasi
 * @param {string} tipe - Tipe notifikasi (sukses, error, peringatan)
 */
function tampilkanNotifikasi(pesan, tipe = 'info') {
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
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    sidebarCollapsed = !sidebarCollapsed;
    
    if (sidebar) {
        sidebar.classList.toggle('collapsed', sidebarCollapsed);
    }
    if (mainContent) {
        mainContent.classList.toggle('sidebar-collapsed', sidebarCollapsed);
    }

    // Simpan preferensi
    localStorage.setItem('sidebarCollapsed', sidebarCollapsed);
}

/**
 * Toggle mobile sidebar.
 */
function toggleMobileSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    if (sidebar) {
        sidebar.classList.toggle('mobile-open');
    }
    if (overlay) {
        overlay.classList.toggle('active');
    }
}

/**
 * Toggle tema gelap/terang.
 */
function toggleTema() {
    const root = document.documentElement;
    const temaSekarang = root.getAttribute('data-tema');
    const temaBaru = temaSekarang === 'gelap' ? 'terang' : 'gelap';
    
    root.setAttribute('data-tema', temaBaru);
    localStorage.setItem('tema', temaBaru);

    // Update ikon
    const ikon = document.querySelector('.toggle-tema .nav-icon');
    if (ikon) {
        ikon.innerHTML = temaBaru === 'gelap' ? 
            '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>' :
            '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>';
    }
}

// ============================================
// FILE UPLOAD
// ============================================

/**
 * Inisialisasi zona upload dengan drag-and-drop.
 */
function initUploadZone() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('berkasProposal');
    
    if (!uploadZone || !fileInput) return;

    // Drag events
    ['dragenter', 'dragover'].forEach(eventType => {
        uploadZone.addEventListener(eventType, (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(eventType => {
        uploadZone.addEventListener(eventType, (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
        });
    });

    // Drop handler
    uploadZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
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
    const uploadZone = document.getElementById('uploadZone');
    const uploadContent = document.querySelector('.upload-content');
    const uploadPreview = document.getElementById('uploadPreview');
    
    // Validasi
    const validasi = validasiBerkas(berkas);
    if (!validasi.valid) {
        tampilkanNotifikasi(validasi.pesan, 'error');
        return;
    }

    berkasYangDipilih = berkas;
    
    // Update UI
    if (uploadZone) {
        uploadZone.classList.add('has-file');
    }
    if (uploadContent) {
        uploadContent.style.display = 'none';
    }
    if (uploadPreview) {
        uploadPreview.style.display = 'flex';
        
        // Update preview info
        const fileNameEl = uploadPreview.querySelector('.file-name');
        const fileSizeEl = uploadPreview.querySelector('.file-size');
        
        if (fileNameEl) fileNameEl.textContent = berkas.name;
        if (fileSizeEl) fileSizeEl.textContent = formatUkuranBerkas(berkas.size);
    }
}

/**
 * Reset file upload.
 */
function resetUpload() {
    berkasYangDipilih = null;
    
    const uploadZone = document.getElementById('uploadZone');
    const uploadContent = document.querySelector('.upload-content');
    const uploadPreview = document.getElementById('uploadPreview');
    const fileInput = document.getElementById('berkasProposal');
    
    if (uploadZone) uploadZone.classList.remove('has-file');
    if (uploadContent) uploadContent.style.display = 'block';
    if (uploadPreview) uploadPreview.style.display = 'none';
    if (fileInput) fileInput.value = '';
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
        tampilkanNotifikasi('Silakan pilih file proposal terlebih dahulu', 'error');
        return;
    }

    // Ambil jenis proposal
    const jenisProposal = document.getElementById('jenisProposal')?.value;
    if (!jenisProposal) {
        tampilkanNotifikasi('Silakan pilih jenis proposal', 'error');
        return;
    }

    // Show loading
    toggleLoading(true);

    try {
        // Prepare form data
        const formData = new FormData();
        formData.append('berkas', berkasYangDipilih);
        formData.append('jenis_proposal', jenisProposal);

        // Submit ke API
        const response = await fetch(`${API_BASE_URL}/review`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Terjadi kesalahan');
        }

        // Tampilkan hasil
        if (result.berhasil && result.data) {
            tampilkanHasil(result.data);
        } else {
            throw new Error(result.pesan || 'Review gagal');
        }

    } catch (error) {
        console.error('Error:', error);
        tampilkanNotifikasi(error.message, 'error');
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
    const hasilContainer = document.getElementById('hasilContainer');
    if (!hasilContainer) return;

    // Update skor
    const skorNilai = document.getElementById('skorNilai');
    const skorBar = document.getElementById('skorBarFill');
    
    if (skorNilai) skorNilai.textContent = hasil.skor;
    if (skorBar) skorBar.style.width = `${hasil.skor}%`;

    // Update detail skor jika ada
    if (hasil.detail_skor) {
        updateDetailSkor(hasil.detail_skor);
    }

    // Update kekuatan
    updateFeedbackList('daftarKekuatan', hasil.daftar_kekuatan, 'kekuatan');

    // Update kelemahan  
    updateFeedbackList('daftarKelemahan', hasil.daftar_kelemahan, 'kelemahan');

    // Update saran
    updateFeedbackList('daftarSaran', hasil.daftar_saran, 'saran');

    // Update ringkasan
    const ringkasanText = document.getElementById('ringkasanText');
    if (ringkasanText) {
        ringkasanText.textContent = hasil.ringkasan;
    }

    // Tampilkan container hasil
    hasilContainer.classList.add('visible');
    
    // Scroll ke hasil
    hasilContainer.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Update detail skor cards.
 * @param {object} detailSkor - Objek detail skor
 */
function updateDetailSkor(detailSkor) {
    const detailGrid = document.getElementById('detailSkorGrid');
    if (!detailGrid) return;

    const aspekLabels = {
        latar_belakang: 'Latar Belakang',
        formulasi_masalah: 'Formulasi Masalah',
        tujuan: 'Tujuan',
        metodologi: 'Metodologi',
        luaran: 'Luaran'
    };

    let html = '';
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
        kekuatan: '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
        kelemahan: '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
        saran: '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>'
    };

    let html = '';
    items.forEach(item => {
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
    const hasilContainer = document.getElementById('hasilContainer');
    if (hasilContainer) {
        hasilContainer.classList.remove('visible');
    }
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Load preferensi tema
    const temaTersimpan = localStorage.getItem('tema');
    if (temaTersimpan) {
        document.documentElement.setAttribute('data-tema', temaTersimpan);
    }

    // Load preferensi sidebar
    const sidebarTersimpan = localStorage.getItem('sidebarCollapsed');
    if (sidebarTersimpan === 'true') {
        toggleSidebar();
    }

    // Init upload zone
    initUploadZone();

    // Form submit handler
    const formReview = document.getElementById('formReview');
    if (formReview) {
        formReview.addEventListener('submit', submitReview);
    }

    // Sidebar toggle
    const btnToggleSidebar = document.querySelector('.sidebar-toggle');
    if (btnToggleSidebar) {
        btnToggleSidebar.addEventListener('click', toggleSidebar);
    }

    // Mobile menu
    const btnMobileMenu = document.querySelector('.mobile-menu-btn');
    if (btnMobileMenu) {
        btnMobileMenu.addEventListener('click', toggleMobileSidebar);
    }

    // Sidebar overlay (close on click)
    const sidebarOverlay = document.querySelector('.sidebar-overlay');
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', toggleMobileSidebar);
    }

    // Tema toggle
    const btnToggleTema = document.querySelector('.toggle-tema');
    if (btnToggleTema) {
        btnToggleTema.addEventListener('click', toggleTema);
    }

    console.log('AI Proposal Reviewer - Berhasil diinisialisasi');
});
