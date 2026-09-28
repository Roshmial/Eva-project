---
name: user-local-libreoffice-rendering
description: "Use when PPTX rendering needs LibreOffice without sudo."
---
# User-local LibreOffice rendering

Use extracted Ubuntu deb packages when no office renderer or sudo is available. Keep installation and profiles under Hermes scratch, not system directories.

1. Query `apt-get --print-uris --yes --download-only --no-install-recommends install libreoffice-impress`; download the listed packages and extract each with `dpkg-deb -x` into one local root.
2. Rewrite absolute symlinks only within that extracted root when their targets exist in the root. Put `usr/lib/libreoffice/program` BEFORE `usr/lib/x86_64-linux-gnu` in process-local LD_LIBRARY_PATH; otherwise UNO may seek unorc next to the library symlink.
3. Patch extracted `program/fundamentalrc`: BRAND_BASE_DIR and both CONFIGURATION_LAYERS registry URLs must point to the extracted root.
4. Copy `usr/lib/libreoffice/share/.registry/` contents into extracted `etc/libreoffice/registry/`. Deb extraction does not run post-install scripts; absent main.xcd causes DeploymentException or unspecified application errors.
5. Supply a local fontconfig file with an extracted fonts directory and writable cache; set FONTCONFIG_FILE and SAL_USE_VCLPLUGIN=svp. Use an isolated `-env:UserInstallation=file:///...` profile.
6. Run headless PDF conversion; javaldx warning is nonfatal for Impress export. Render PDF pages with PyMuPDF if Poppler is absent.
7. Inspect rendered images, repair visible faults, and rerender affected slides. Do not confuse PPTX text extraction or success exit codes with visual validation.

Preserve reference assets by comparing image blobs and geometry, not filenames alone; replacement decks may already have altered raster images. Inspect embedded raster diagrams for old labels and unsupported numerical examples, since text extraction cannot see them.
