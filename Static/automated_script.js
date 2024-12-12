const API_KEY = '89d7986bba034ac7be253db7e949c576'

const types = "Samsung"
let input_url = null
const output_url = ""
const data = {
    sourceName: types,
    
}

input_url = `https://newsapi.org/v2/everything?q=${type}&from=2024-11-27&sortBy=popularity&apiKey=${API_KEY}`
const xhr = new XMLHttpRequest();
xhr.open('GET', input_url, true);

xhr.onload = () => {
    if (xhr.status >= 200 && xhr.status < 300) {
        console.log('Data received:', JSON.parse(xhr.responseText))
    } else {
        console.error('Error fetching data')
    }
}

xhr.onerror = () => {
    console.error("Network error occured");
}

xhr.send()