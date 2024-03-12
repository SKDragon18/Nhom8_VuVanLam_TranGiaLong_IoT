// chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
//   if (request.action === 'urlBeforeNavigate') {
//     const urlBeforeNavigate = request.url;
//     console.log('URL trước khi truy cập từ background:', urlBeforeNavigate);
//     alert("Bạn đang truy cập trang có địa chỉ " + urlBeforeNavigate);
//     // Thực hiện các hành động trên trang web nếu cần

//     // Ví dụ: gửi thông điệp tới background
//     // chrome.runtime.sendMessage({ action: 'performActionOnUrlBeforeNavigate', url: urlBeforeNavigate });
//   }
// });