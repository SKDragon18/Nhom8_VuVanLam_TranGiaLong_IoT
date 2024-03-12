
var isPopup = false; // Khai báo biến isPopup
let isContinue = false;
let mainFrameNavigated = false;
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  // Kiểm tra loại tin nhắn
  if (request.type === "userChoice") {
    // Lấy giá trị của biến isContinue
    isContinue = request.value;
  }
})

chrome.webNavigation.onCommitted.addListener(function (details) {
  // Kiểm tra xem có phải là tab hiện tại hay không
  if (details.frameId === 0) {
    // Đặt lại giá trị của biến isContinue thành false
    isContinue = false;
  }
});

chrome.webNavigation.onBeforeNavigate.addListener(function (details) {
  if (details.frameId === 0 && !mainFrameNavigated) {
    const urlBeforeNavigate = details.url;
    console.log('URL trước khi truy cập:', urlBeforeNavigate);
    mainFrameNavigated = true;
    // Sử dụng phương thức startsWith để kiểm tra URL của popup
    if (urlBeforeNavigate.endsWith("popup/popup.html") || urlBeforeNavigate.indexOf("//new-tab-page/") != -1) {
      isPopup = true; // đặt trạng thái là popup
      return; // bỏ qua xử lý
    } else {
      isPopup = false; // đặt trạng thái là bình thường
    };


    // Kiểm tra xem người dùng có chọn tiếp tục hay không
    if (isContinue) {
      return; // bỏ qua xử lý
    };
    // Gửi url về server để xử lý
    const dataToSend = { "url": urlBeforeNavigate };

    fetch('http://localhost:5000/process_data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(dataToSend),
    })
      .then(response => response.json())
      .then(data => {
        // Xử lý kết quả từ server (ví dụ: in ra console)
        console.log('Server response:', data.result);
        if (data.result != "benign" && !isPopup) {
          
          chrome.storage.local.set({ url: urlBeforeNavigate }, function () {
            // Tạo một tab mới với URL của popup
            chrome.tabs.update(details.tabId, { url: "popup/popup.html" });
          });
        }
      })
      .catch(error => {
        console.error('Error:', error);
      })

  }
  mainFrameNavigated = false;
});


// Thêm sự kiện onCompleted để đặt lại biến mainFrameNavigated
// chrome.webNavigation.onCompleted.addListener(function (details) {
//   if (details.frameId === 0) {
//     mainFrameNavigated = false;
//   }
// });