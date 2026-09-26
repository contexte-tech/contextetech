// Thème choisi par le visiteur, appliqué avant l'affichage pour éviter un flash (chargé de façon bloquante dans <head>)
try { var m = localStorage.getItem("theme"); if (m === "light" || m === "dark") document.documentElement.dataset.theme = m; } catch (e) {}
