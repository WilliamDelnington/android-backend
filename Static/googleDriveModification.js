import 'dotenv';
import { google } from 'googleapis';
import { GoogleAuth } from 'google-auth-library';

const SCOPE = "https://www.googleapis.com/auth/drive"
const API_KEY = '34cf704a735a0601ae3f77a425bbd55fff0d1015'
const CLIENT_ID = '113939164071096819900'

const auth = new GoogleAuth({scopes: SCOPE})
const service = google.drive({version: 'v3', auth})

const credentialPath = __dirname + process.env.GOOGLE_DRIVE_CREDENTIALS_JSON_FILE_PATH

let authInstance

console.log(__dirname)

function loadGPI() {
    gapi.load("client:auth2", async () => {
        await gapi.client.init({
            apiKey: API_KEY,
            clientId: `${CLIENT_ID}.apps.googleusercontent.com`,
            scope: SCOPE,
        })
        authInstance = gapi.auth2.getAuthInstance()
    })

    document.getElementById("")
}

document.getElementById("upload-file-form").addEventListener("submit", (e) => {
    e.preventDefault();

    const confirmSave = confirm('Are you sure you want to upload this data?');
    if (!confirmSave) {
        return;
    }

    const data = {
        url: document.getElementById("file-upload").files[0]
    }

    // const d = document.createElement("div");
    // d.textContent = URL.createObjectURL(data.url);
    // document.querySelector("body").appendChild(d);

    const formData = new FormData();
})