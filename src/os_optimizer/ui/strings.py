"""
Centralized UI strings for all languages.

To add a language:
  1. Create a new AppStrings instance below (e.g. DE, TR).
  2. Register it in LANGUAGES.
  3. Call set_language("de") before showing the main window.

Format strings use Python's .format() — callers supply named args:
  strings.get().pkg_n_updates.format(n=count)
Plural logic lives in the caller for now; a proper pluralization
library (e.g. babel) should replace this when DE/TR are added.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class AppStrings:
    # ── App ──────────────────────────────────────────────────────────────
    app_name: str
    app_platform: str

    # ── Navigation ───────────────────────────────────────────────────────
    nav_dashboard_icon: str
    nav_dashboard: str
    nav_disk_icon: str
    nav_disk: str
    nav_packages_icon: str
    nav_packages: str
    nav_health_icon: str
    nav_health: str
    nav_apps_icon: str
    nav_apps: str

    # ── Dashboard ─────────────────────────────────────────────────────────
    dash_title: str
    dash_subtitle: str
    dash_cpu: str
    dash_ram: str
    dash_disk_root: str
    dash_packages_label: str
    dash_health_label: str
    dash_checking: str
    dash_n_updates: str             # format: {n}
    dash_n_issues: str              # format: {n}
    dash_update_btn: str
    # system vitals row
    dash_uptime: str
    dash_load: str
    dash_swap: str
    dash_temp: str
    dash_temp_na: str

    # ── Disk view ─────────────────────────────────────────────────────────
    disk_title: str
    disk_subtitle: str
    disk_largest_in: str
    disk_scan_btn: str
    disk_col_path: str
    disk_col_size: str
    disk_col_pct: str
    disk_dblclick_hint: str
    disk_chart_used: str
    disk_chart_free: str

    # ── Packages view ─────────────────────────────────────────────────────
    pkg_title: str
    pkg_subtitle: str
    pkg_checking: str
    pkg_up_to_date: str
    pkg_n_available: str            # format: {n}, {s}
    pkg_refresh_btn: str
    pkg_update_btn: str
    pkg_col_name: str
    pkg_col_current: str
    pkg_col_available: str

    # ── Health view ───────────────────────────────────────────────────────
    health_title: str
    health_subtitle: str
    health_scanning: str
    health_no_issues: str
    health_n_detected: str          # format: {errors}, {es}, {warnings}, {ws}
    health_rescan_btn: str
    health_col_severity: str
    health_col_path: str
    health_col_issue: str
    health_col_fix: str
    health_col_action: str
    health_fix_btn: str

    # ── Fix dialog ────────────────────────────────────────────────────────
    fix_title: str
    fix_description: str
    fix_warn_sudo: str
    fix_apply_btn: str
    fix_close_btn: str
    fix_success: str
    fix_failed: str                 # format: {code}

    # ── Auth dialog ───────────────────────────────────────────────────────
    auth_title: str
    auth_icon: str
    auth_heading: str
    auth_description: str
    auth_placeholder: str
    auth_error_empty: str
    auth_error_wrong: str
    auth_verifying: str
    auth_skip_btn: str
    auth_confirm_btn: str

    # ── Update dialog ─────────────────────────────────────────────────────
    update_title: str
    update_close_btn: str
    update_success: str
    update_failed: str              # format: {code}

    # ── Apps view ─────────────────────────────────────────────────────────
    apps_title: str
    apps_subtitle: str
    apps_loading: str
    apps_n_packages: str            # format: {n}, {size}
    apps_search_placeholder: str
    apps_refresh_btn: str
    apps_col_name: str
    apps_col_version: str
    apps_col_size: str
    apps_col_installed: str
    apps_col_desc: str
    apps_col_action: str
    apps_remove_btn: str
    apps_remove_title: str


EN = AppStrings(
    app_name="OS Optimizer",
    app_platform="Arch Linux",

    nav_dashboard_icon="📊",
    nav_dashboard="Dashboard",
    nav_disk_icon="💾",
    nav_disk="Disk Usage",
    nav_packages_icon="📦",
    nav_packages="Packages",
    nav_health_icon="🏥",
    nav_health="Health",
    nav_apps_icon="📋",
    nav_apps="Installed Apps",

    dash_title="Dashboard",
    dash_subtitle="Live system overview",
    dash_cpu="CPU Usage",
    dash_ram="Memory",
    dash_disk_root="Disk  /",
    dash_packages_label="Packages",
    dash_health_label="Health Issues",
    dash_checking="Checking…",
    dash_n_updates="{n} updates",
    dash_n_issues="{n} issues",
    dash_update_btn="⬆  Apply All Updates Now",
    dash_uptime="Uptime",
    dash_load="Load (5 min)",
    dash_swap="Swap",
    dash_temp="CPU Temp",
    dash_temp_na="N/A",

    disk_title="Disk Usage",
    disk_subtitle="Partition overview and largest files & folders",
    disk_largest_in="Largest items in:",
    disk_scan_btn="Scan",
    disk_col_path="Path",
    disk_col_size="Size",
    disk_col_pct="% of Disk",
    disk_dblclick_hint="Double-click a row to drill in  ·  Btrfs subvolumes show — until drilled into",
    disk_chart_used="Used",
    disk_chart_free="Free",

    pkg_title="Packages",
    pkg_subtitle="Available system updates via pacman",
    pkg_checking="Checking for updates…",
    pkg_up_to_date="System is up to date.",
    pkg_n_available="{n} update{s} available",
    pkg_refresh_btn="Refresh",
    pkg_update_btn="Apply All Updates",
    pkg_col_name="Package",
    pkg_col_current="Current",
    pkg_col_available="Available",

    health_title="System Health",
    health_subtitle="Permissions, configs, and orphaned packages",
    health_scanning="Scanning…",
    health_no_issues="No issues found — system looks healthy.",
    health_n_detected="{errors} error{es}, {warnings} warning{ws} detected",
    health_rescan_btn="Rescan",
    health_col_severity="Severity",
    health_col_path="Path / Target",
    health_col_issue="Issue",
    health_col_fix="Fix Command",
    health_col_action="Action",
    health_fix_btn="Fix",

    fix_title="Apply Fix",
    fix_description="The following command will be executed:",
    fix_warn_sudo="⚠  This command requires sudo access.",
    fix_apply_btn="Apply Fix",
    fix_close_btn="Close",
    fix_success="\n✓ Fix applied successfully.",
    fix_failed="\n✗ Command exited with code {code}.",

    auth_title="Sudo Authentication",
    auth_icon="🔐",
    auth_heading="Sudo Authentication Required",
    auth_description=(
        "OS Optimizer needs sudo access to apply system updates.\n"
        "Your password is used only for this session and never stored on disk."
    ),
    auth_placeholder="Enter sudo password…",
    auth_error_empty="Please enter your password.",
    auth_error_wrong="Incorrect password. Please try again.",
    auth_verifying="Verifying…",
    auth_skip_btn="Skip (view only)",
    auth_confirm_btn="Authenticate",

    update_title="Applying Updates",
    update_close_btn="Close",
    update_success="\n✓ Update completed successfully.",
    update_failed="\n✗ Process exited with code {code}.",

    apps_title="Installed Applications",
    apps_subtitle="All packages installed via pacman, sorted by size",
    apps_loading="Loading installed packages…",
    apps_n_packages="{n} packages · {size} installed",
    apps_search_placeholder="Filter by name…",
    apps_refresh_btn="Refresh",
    apps_col_name="Package",
    apps_col_version="Version",
    apps_col_size="Installed Size",
    apps_col_installed="Installed On",
    apps_col_desc="Description",
    apps_col_action="Action",
    apps_remove_btn="Remove",
    apps_remove_title="Remove Package",
)

DE = AppStrings(
    app_name="OS Optimierer",
    app_platform="Arch Linux",

    nav_dashboard_icon="📊",
    nav_dashboard="Dashboard",
    nav_disk_icon="💾",
    nav_disk="Festplatte",
    nav_packages_icon="📦",
    nav_packages="Pakete",
    nav_health_icon="🏥",
    nav_health="Gesundheit",
    nav_apps_icon="📋",
    nav_apps="Installierte Apps",

    dash_title="Dashboard",
    dash_subtitle="Live-Systemübersicht",
    dash_cpu="CPU-Auslastung",
    dash_ram="Arbeitsspeicher",
    dash_disk_root="Festplatte  /",
    dash_packages_label="Pakete",
    dash_health_label="Probleme",
    dash_checking="Wird geprüft…",
    dash_n_updates="{n} Updates",
    dash_n_issues="{n} Probleme",
    dash_update_btn="⬆  Alle Updates jetzt installieren",
    dash_uptime="Laufzeit",
    dash_load="Last (5 Min.)",
    dash_swap="Auslagerung",
    dash_temp="CPU-Temp.",
    dash_temp_na="N/V",

    disk_title="Festplattennutzung",
    disk_subtitle="Partitionsübersicht und größte Dateien & Ordner",
    disk_largest_in="Größte Einträge in:",
    disk_scan_btn="Scannen",
    disk_col_path="Pfad",
    disk_col_size="Größe",
    disk_col_pct="% der Disk",
    disk_dblclick_hint="Doppelklick zum Einsteigen  ·  Btrfs-Subvolumes zeigen — bis zum Einsteigen",
    disk_chart_used="Belegt",
    disk_chart_free="Frei",

    pkg_title="Pakete",
    pkg_subtitle="Verfügbare Systemupdates via pacman",
    pkg_checking="Suche nach Updates…",
    pkg_up_to_date="System ist aktuell.",
    pkg_n_available="{n} Update{s} verfügbar",
    pkg_refresh_btn="Aktualisieren",
    pkg_update_btn="Alle Updates installieren",
    pkg_col_name="Paket",
    pkg_col_current="Aktuell",
    pkg_col_available="Verfügbar",

    health_title="Systemgesundheit",
    health_subtitle="Berechtigungen, Konfigurationen und verwaiste Pakete",
    health_scanning="Wird gescannt…",
    health_no_issues="Keine Probleme gefunden — System sieht gut aus.",
    health_n_detected="{errors} Fehler, {warnings} Warnung{ws} gefunden",
    health_rescan_btn="Erneut scannen",
    health_col_severity="Schwere",
    health_col_path="Pfad / Ziel",
    health_col_issue="Problem",
    health_col_fix="Befehl",
    health_col_action="Aktion",
    health_fix_btn="Beheben",

    fix_title="Behebung anwenden",
    fix_description="Der folgende Befehl wird ausgeführt:",
    fix_warn_sudo="⚠  Dieser Befehl benötigt Sudo-Zugriff.",
    fix_apply_btn="Behebung anwenden",
    fix_close_btn="Schließen",
    fix_success="\n✓ Behebung erfolgreich angewendet.",
    fix_failed="\n✗ Befehl mit Code {code} beendet.",

    auth_title="Sudo-Authentifizierung",
    auth_icon="🔐",
    auth_heading="Sudo-Zugriff erforderlich",
    auth_description=(
        "OS Optimierer benötigt Sudo-Zugriff um Updates zu installieren.\n"
        "Ihr Passwort wird nur für diese Sitzung verwendet und nie gespeichert."
    ),
    auth_placeholder="Sudo-Passwort eingeben…",
    auth_error_empty="Bitte Passwort eingeben.",
    auth_error_wrong="Falsches Passwort. Bitte erneut versuchen.",
    auth_verifying="Wird geprüft…",
    auth_skip_btn="Überspringen (nur Ansicht)",
    auth_confirm_btn="Authentifizieren",

    update_title="Updates werden installiert",
    update_close_btn="Schließen",
    update_success="\n✓ Update erfolgreich abgeschlossen.",
    update_failed="\n✗ Prozess mit Code {code} beendet.",

    apps_title="Installierte Anwendungen",
    apps_subtitle="Alle via pacman installierten Pakete, nach Größe sortiert",
    apps_loading="Pakete werden geladen…",
    apps_n_packages="{n} Pakete · {size} installiert",
    apps_search_placeholder="Nach Name filtern…",
    apps_refresh_btn="Aktualisieren",
    apps_col_name="Paket",
    apps_col_version="Version",
    apps_col_size="Installierte Größe",
    apps_col_installed="Installiert am",
    apps_col_desc="Beschreibung",
    apps_col_action="Aktion",
    apps_remove_btn="Entfernen",
    apps_remove_title="Paket entfernen",
)

TR = AppStrings(
    app_name="OS Optimizeri",
    app_platform="Arch Linux",

    nav_dashboard_icon="📊",
    nav_dashboard="Gösterge Paneli",
    nav_disk_icon="💾",
    nav_disk="Disk Kullanımı",
    nav_packages_icon="📦",
    nav_packages="Paketler",
    nav_health_icon="🏥",
    nav_health="Sağlık",
    nav_apps_icon="📋",
    nav_apps="Yüklü Uygulamalar",

    dash_title="Gösterge Paneli",
    dash_subtitle="Canlı sistem özeti",
    dash_cpu="CPU Kullanımı",
    dash_ram="Bellek",
    dash_disk_root="Disk  /",
    dash_packages_label="Paketler",
    dash_health_label="Sorunlar",
    dash_checking="Kontrol ediliyor…",
    dash_n_updates="{n} güncelleme",
    dash_n_issues="{n} sorun",
    dash_update_btn="⬆  Tüm Güncellemeleri Şimdi Uygula",
    dash_uptime="Çalışma Süresi",
    dash_load="Yük (5 dak.)",
    dash_swap="Takas",
    dash_temp="CPU Sıcaklığı",
    dash_temp_na="Yok",

    disk_title="Disk Kullanımı",
    disk_subtitle="Bölüm genel bakış ve en büyük dosya & klasörler",
    disk_largest_in="En büyük öğeler:",
    disk_scan_btn="Tara",
    disk_col_path="Yol",
    disk_col_size="Boyut",
    disk_col_pct="Disk %'si",
    disk_dblclick_hint="Klasöre girmek için çift tıklayın  ·  Btrfs alt birimleri girilene kadar — gösterir",
    disk_chart_used="Kullanılan",
    disk_chart_free="Boş",

    pkg_title="Paketler",
    pkg_subtitle="pacman aracılığıyla sistem güncellemeleri",
    pkg_checking="Güncellemeler kontrol ediliyor…",
    pkg_up_to_date="Sistem güncel.",
    pkg_n_available="{n} güncelleme mevcut",
    pkg_refresh_btn="Yenile",
    pkg_update_btn="Tüm Güncellemeleri Uygula",
    pkg_col_name="Paket",
    pkg_col_current="Mevcut",
    pkg_col_available="Yeni Sürüm",

    health_title="Sistem Sağlığı",
    health_subtitle="İzinler, yapılandırmalar ve sahipsiz paketler",
    health_scanning="Taranıyor…",
    health_no_issues="Sorun bulunamadı — sistem sağlıklı görünüyor.",
    health_n_detected="{errors} hata, {warnings} uyarı tespit edildi",
    health_rescan_btn="Yeniden Tara",
    health_col_severity="Önem",
    health_col_path="Yol / Hedef",
    health_col_issue="Sorun",
    health_col_fix="Komut",
    health_col_action="İşlem",
    health_fix_btn="Düzelt",

    fix_title="Düzeltme Uygula",
    fix_description="Aşağıdaki komut çalıştırılacak:",
    fix_warn_sudo="⚠  Bu komut sudo erişimi gerektiriyor.",
    fix_apply_btn="Düzeltmeyi Uygula",
    fix_close_btn="Kapat",
    fix_success="\n✓ Düzeltme başarıyla uygulandı.",
    fix_failed="\n✗ Komut {code} koduyla sonlandı.",

    auth_title="Sudo Kimlik Doğrulama",
    auth_icon="🔐",
    auth_heading="Sudo Erişimi Gerekli",
    auth_description=(
        "OS Optimizeri sistem güncellemelerini uygulamak için sudo erişimine ihtiyaç duyar.\n"
        "Şifreniz yalnızca bu oturum için kullanılır ve diske hiç kaydedilmez."
    ),
    auth_placeholder="Sudo şifresini girin…",
    auth_error_empty="Lütfen şifrenizi girin.",
    auth_error_wrong="Yanlış şifre. Lütfen tekrar deneyin.",
    auth_verifying="Doğrulanıyor…",
    auth_skip_btn="Atla (yalnızca görüntüle)",
    auth_confirm_btn="Kimliği Doğrula",

    update_title="Güncellemeler Uygulanıyor",
    update_close_btn="Kapat",
    update_success="\n✓ Güncelleme başarıyla tamamlandı.",
    update_failed="\n✗ İşlem {code} koduyla sonlandı.",

    apps_title="Yüklü Uygulamalar",
    apps_subtitle="pacman ile yüklenmiş tüm paketler, boyuta göre sıralı",
    apps_loading="Paketler yükleniyor…",
    apps_n_packages="{n} paket · {size} yüklü",
    apps_search_placeholder="İsme göre filtrele…",
    apps_refresh_btn="Yenile",
    apps_col_name="Paket",
    apps_col_version="Sürüm",
    apps_col_size="Yüklü Boyut",
    apps_col_installed="Yüklenme Tarihi",
    apps_col_desc="Açıklama",
    apps_col_action="İşlem",
    apps_remove_btn="Kaldır",
    apps_remove_title="Paketi Kaldır",
)


LANGUAGES: dict[str, AppStrings] = {"en": EN, "de": DE, "tr": TR}
_active: AppStrings = EN


def get() -> AppStrings:
    return _active


def set_language(code: str) -> None:
    global _active
    if code not in LANGUAGES:
        raise ValueError(f"Unsupported language: {code!r}. Available: {list(LANGUAGES)}")
    _active = LANGUAGES[code]
