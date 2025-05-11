// Sağ tık menüsünü oluştur
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "checkNews",
    title: "Haber Kontrol ile Analiz Et",
    contexts: ["link"]
  });
});

// Sağ tık menüsüne tıklandığında
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "checkNews") {
    // Seçilen linki al
    const newsUrl = info.linkUrl;
    
    // Yeni sekmede Haber Kontrol sitesini aç
    chrome.tabs.create({
      url: `http://localhost:5000/?url=${encodeURIComponent(newsUrl)}`
    });
  }
}); 