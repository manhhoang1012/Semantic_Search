// const BASE_URL = "http://127.0.0.1:5000/api";

// // SEARCH
// async function searchAPI(data) {
//     const res = await fetch(`${BASE_URL}/search`, {
//         method: "POST",
//         headers: {"Content-Type": "application/json"},
//         body: JSON.stringify(data)
//     });
//     return res.json();
// }

// // ADD
// async function addAPI(data) {
//     const res = await fetch(`${BASE_URL}/add`, {
//         method: "POST",
//         headers: {"Content-Type": "application/json"},
//         body: JSON.stringify(data)
//     });
//     return res.json();
// }

// // DELETE
// async function deleteAPI(id) {
//     const res = await fetch(`${BASE_URL}/delete/${id}`, {
//         method: "DELETE"
//     });
//     return res.json();
// }



const BASE_URL = "http://127.0.0.1:5000/api";

// SEARCH
async function searchAPI(data) {
    const res = await fetch(`${BASE_URL}/search`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    });
    return res.json();
}

// ADD / UPDATE
async function updateAPI(data) {
    const res = await fetch(`${BASE_URL}/add`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    });
    return res.json();
}

// DELETE
async function deleteAPI(id) {
    const res = await fetch(`${BASE_URL}/delete/${id}`, {
        method: "DELETE"
    });
    return res.json();
}

// GET LIST
async function getListAPI() {
    const res = await fetch(`${BASE_URL}/list`);
    return res.json();
}