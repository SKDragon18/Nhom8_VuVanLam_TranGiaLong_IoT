let isContinue = false;
chrome.storage.local.get("url", function (data) {
  // Hiển thị URL trong popup
  document.getElementById("url").textContent = data.url;
});

// Lắng nghe sự kiện nhấp vào nút tiếp tục
document.getElementById("continue").addEventListener("click", function () {
  isContinue = true;
  // Lấy URL của trang web mà người dùng sắp truy cập từ bộ nhớ cục bộ
  chrome.storage.local.get("url", function (data) {
    // Cập nhật URL của tab hiện tại thành URL của trang web đó
    chrome.tabs.update({ url: data.url });
  });
  // Gửi tin nhắn đến background script với lựa chọn của người dùng
  chrome.runtime.sendMessage({ type: "userChoice", value: isContinue });
});

// Lắng nghe sự kiện nhấp vào nút trở lại
document.getElementById("back").addEventListener("click", function () {
  isContinue=false;
  // Lấy thông tin về tab hiện tại
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    // Lấy ID của tab hiện tại
    let currentTabId = tabs[0].id;
    // Lấy thông tin về tab trước đó
    chrome.tabs.get(currentTabId, function (tab) {
      // Lấy URL của tab trước đó
      let previousUrl = tab.openerTabId;
      // Cập nhật URL của tab hiện tại thành URL của tab trước đó
      chrome.tabs.update({ url: previousUrl });
    });
  });
  // Gửi tin nhắn đến background script với lựa chọn của người dùng
  chrome.runtime.sendMessage({ type: "userChoice", value: isContinue });
});