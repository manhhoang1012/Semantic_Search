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

function displayResults(results) {
    const container = document.getElementById("results");
    container.innerHTML = "";

    results.forEach(item => {
        const div = document.createElement("div");
        div.className = "card";

        div.innerHTML = `
            <h3>${item.metadata.title}</h3>
            <p>Subreddit: ${item.metadata.subreddit}</p>
            <p>Score: ${item.metadata.score}</p>
            <p>Similarity: ${item.score.toFixed(4)}</p>
            <button onclick="handleDelete('${item.id}')">Delete</button>
        `;

        container.appendChild(div);
    });
}

async function handleDelete(id) {
    await deleteAPI(id);
    alert("Deleted!");
}