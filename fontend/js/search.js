async function handleSearch() {
    const query = document.getElementById("query").value;
    const top_k = document.getElementById("top_k").value;
    const subreddit = document.getElementById("subreddit").value;

    let filter = null;
    if (subreddit) {
        filter = { subreddit: subreddit };
    }

    const results = await searchAPI({
        query,
        top_k: parseInt(top_k),
        filter
    });

    displayResults(results.results);
}

// function displayResults(results) {
//     const container = document.getElementById("results");
//     container.innerHTML = "";

//     results.forEach(item => {
//         const div = document.createElement("div");
//         div.className = "card";

//         div.innerHTML = `
//             <h3>${item.metadata.title}</h3>
//             <p>Subreddit: ${item.metadata.subreddit}</p>
//             <p>Score: ${item.metadata.score}</p>
//             <p>Similarity: ${item.score.toFixed(4)}</p>
//             <button onclick="handleDelete('${item.id}')">Delete</button>
//         `;

//         container.appendChild(div);
//     });
// }

async function handleDelete(id) {
    await deleteAPI(id);
    alert("Deleted!");
}


function displayResults(results) {
    const container = document.getElementById("results");
    container.innerHTML = "";

    results.forEach(item => {
        const card = `
            <div class="col-md-4">
                <div class="card p-3 mb-3 shadow-sm">
                    <h5>${item.metadata.title}</h5>
                    <p><b>Subreddit:</b> ${item.metadata.subreddit}</p>
                    <p><b>Score:</b> ${item.metadata.score}</p>
                    <p><b>Similarity:</b> ${item.score.toFixed(4)}</p>
                </div>
            </div>
        `;

        container.innerHTML += card;
    });
}