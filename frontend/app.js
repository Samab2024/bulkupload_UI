async function runUpload() {
const region = document.getElementById('region').value;
const profile = document.getElementById('profile').value;
const file = document.getElementById('csvFile').files[0];

const formData = new FormData();
formData.append('region', region);
formData.append('profile', profile);
formData.append('file', file);

const res = await fetch('/bulk-upload', {
method: 'POST',
body: formData
});

const data = await res.json();
document.getElementById('output').innerText = JSON.stringify(data, null, 2);
}
