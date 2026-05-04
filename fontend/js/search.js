
// async function handleSearch() {
//     const query = document.getElementById("query").value;
//     const top_k = document.getElementById("top_k").value;
//     const subreddit = document.getElementById("subreddit").value;

//     let filter = null;
//     if (subreddit) {
//         filter = { subreddit: subreddit };
//     }

//     const results = await searchAPI({
//         query,
//         top_k: parseInt(top_k),
//         filter
//     });

//     displayResults(results);
// }





// function displayResults(data) {
//     const results = data.results || data; // linh hoạt

//     const container = document.getElementById("results");
//     container.innerHTML = "";

//     results.forEach(item => {
//         const card = `
//             <div class="col-md-4">
//                 <div class="card p-3 mb-3 shadow-sm">
//                     <h5>${item.metadata.title}</h5>
//                     <p>Subreddit: ${item.metadata.subreddit}</p>
//                     <p>Score: ${item.metadata.score}</p>
//                     <p>Similarity: ${item.score.toFixed(4)}</p>
//                 </div>
//             </div>
//         `;

//         container.innerHTML += card;
//     });
// }


// // ❌ DELETE
// async function handleDelete(id) {
//     await deleteAPI(id);
//     alert("Deleted!");
//     handleSearch(); // reload kết quả
// }


// // ✏️ UPDATE
// async function handleUpdate(id) {
//     const title = document.getElementById(`title-${id}`).value;
//     const subreddit = document.getElementById(`subreddit-${id}`).value;

//     const data = {
//         id: id,
//         title: title,
//         subreddit: subreddit,
//         score: 0,
//         comments: 0,
//         username: "updated_user"
//     };

//     await updateAPI(data);

//     alert("Updated!");
//     handleSearch();
// }

async function handleSearch() {
    const query = document.getElementById("query").value;
    const top_k = document.getElementById("top_k").value;
    const subreddit = document.getElementById("subreddit").value;

    let filter = null;
    if (subreddit) {
        filter = { subreddit: subreddit };
    }

    const res = await searchAPI({
        query,
        top_k: parseInt(top_k),
        filter
    });

    console.log(res);

    const results = res.results || res; // fix format
    // 🔥 THÊM ĐOẠN NÀY
    if (res.latency !== undefined) {
        document.getElementById("latency").innerText =
            "⏱ Response time: " + res.latency.toFixed(3) + "s";
    }
    displayResults(results);
}


// 🔥 HIỂN THỊ + CRUD
function displayResults(results) {
    const container = document.getElementById("results");
    container.innerHTML = "";

    results.forEach(item => {

        const safeId = item.id.replace(/[^a-zA-Z0-9]/g, "");

        const card = `
            <div class="col-md-4">
                <div class="card p-3 mb-3 shadow-sm">

                    <input class="form-control mb-2" 
                        id="title-${safeId}" 
                        value="${item.metadata.title || ""}">

                    <input class="form-control mb-2" 
                        id="subreddit-${safeId}" 
                        value="${item.metadata.subreddit || ""}">

                    <p><b>Score:</b> ${item.metadata.score}</p>
                    <p><b>Similarity:</b> ${item.score.toFixed(4)}</p>

                   

                </div>
            </div>
        `;

        container.innerHTML += card;
    });
}


// ❌ DELETE
async function handleDelete(id) {
    await deleteAPI(id);
    alert("Deleted!");
    handleSearch(); // reload
}


// ✏️ UPDATE
async function handleUpdate(realId, safeId) {
    const title = document.getElementById(`title-${safeId}`).value;
    const subreddit = document.getElementById(`subreddit-${safeId}`).value;

    const data = {
        id: realId,
        title: title,
        subreddit: subreddit,
        score: 0,
        comments: 0,
        username: "updated_user"
    };

    await updateAPI(data);

    alert("Updated!");
    handleSearch(); // reload
}


//  <div class="d-flex justify-content-between">

//                         <button class="btn btn-success btn-sm"
//                             onclick="handleUpdate('${item.id}', '${safeId}')">
//                             Update
//                         </button>

//                         <button class="btn btn-danger btn-sm"
//                             onclick="handleDelete('${item.id}')">
//                             Delete
//                         </button>

//                     </div>
