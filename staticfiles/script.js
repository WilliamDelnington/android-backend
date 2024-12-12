document.getElementById('dataForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const confirmSave = confirm('Are you sure you want to upload this data?');
    if (!confirmSave) {
        return;
    }

    const data = {
        sourceName: document.getElementById('sourceName').value,
        author: document.getElementById('author').value,
        url: document.getElementById('url').value,
        urlToImage: document.getElementById('urlToImage').value,
        title: document.getElementById('title').value,
        description: document.getElementById('description').value,
        content: document.getElementById('content').value,
        publishedAt: document.getElementById('publishedAt').value,
    };

    // Lưu dữ liệu vào localStorage
    saveToLocalStorage(data);

    // Gửi dữ liệu lên API
    await sendDataToAPI(data);

    // Hiển thị dữ liệu mới lên danh sách
    displayDataList();

    document.getElementById('dataForm').reset();
});

// Thêm sự kiện cho nút "Xem form đã lưu"
document.getElementById('viewSavedFormsBtn').addEventListener('click', function() {
    const dataList = document.getElementById('dataList');
    if (dataList.style.display === 'none') {
        displayDataList();
        dataList.style.display = 'block'; // Hiển thị danh sách
    } else {
        dataList.style.display = 'none'; // Ẩn danh sách
    }
});

// Hàm lưu dữ liệu vào localStorage
function saveToLocalStorage(data) {
    let savedData = JSON.parse(localStorage.getItem('formData')) || [];
    savedData.push(data);
    localStorage.setItem('formData', JSON.stringify(savedData));
}

// Hàm gửi dữ liệu qua API
async function sendDataToAPI(data) {
    try {
        const response = await fetch('https://example.com/api/save-data', { // Thay URL bằng API thật
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data), // Chuyển dữ liệu sang JSON
        });

        if (response.ok) {
            const result = await response.json();
            alert('Data saved successfully: ' + JSON.stringify(result));
        } else {
            alert('Failed to save data. Status: ' + response.status);
        }
    } catch (error) {
        console.error('Error saving data:', error);
        alert('An error occurred while saving the data.');
    }
}

// Hàm hiển thị danh sách các bài viết đã lưu
function displayDataList() {
    const savedData = JSON.parse(localStorage.getItem('formData')) || [];
    const dataList = document.getElementById('dataList');
    dataList.innerHTML = '';

    savedData.forEach((data, index) => {
        const dataItem = document.createElement('div');
        dataItem.className = 'data-item';
        dataItem.innerHTML = `
            <p><strong>Source Name:</strong> ${data.sourceName}</p>
            <p><strong>Author:</strong> ${data.author}</p>
            <p><strong>URL:</strong> <a href="${data.url}" target="_blank">${data.url}</a></p>
            <p><strong>URL to Image:</strong> <a href="${data.urlToImage}" target="_blank">${data.urlToImage}</a></p>
            <p><strong>Title:</strong> ${data.title}</p>
            <p><strong>Description:</strong> ${data.description}</p>
            <p><strong>Content:</strong> ${data.content}</p>
            <p><strong>Published At:</strong> ${new Date(data.publishedAt).toLocaleString()}</p>
            <button onclick="loadData(${index})">Load Data</button>
        `;
        dataList.appendChild(dataItem);
    });
}

// Hàm tải dữ liệu đã lưu vào form
function loadData(index) {
    const savedData = JSON.parse(localStorage.getItem('formData')) || [];
    const data = savedData[index];

    if (data) {
        document.getElementById('sourceName').value = data.sourceName;
        document.getElementById('author').value = data.author;
        document.getElementById('url').value = data.url;
        document.getElementById('urlToImage').value = data.urlToImage;
        document.getElementById('title').value = data.title;
        document.getElementById('description').value = data.description;
        document.getElementById('content').value = data.content;
        document.getElementById('publishedAt').value = data.publishedAt;
    } else {
        alert('No data found!');
    }
}
