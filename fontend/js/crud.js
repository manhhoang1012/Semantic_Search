

// // LOAD DATA
// async function loadData() {
//     const data = await getListAPI();

//     const container = document.getElementById("list");
//     container.innerHTML = "";

//     data.forEach(item => {
//         const div = document.createElement("div");
//         div.className = "card";

//         div.innerHTML = `
//             <h3>${item.metadata.title}</h3>
//             <p>ID: ${item.id}</p>
//             <p>Subreddit: ${item.metadata.subreddit}</p>
//             <p>Score: ${item.metadata.score}</p>

//             <button onclick="fillForm(
//                 '${item.id}',
//                 '${item.metadata.title}',
//                 '${item.metadata.subreddit}',
//                 ${item.metadata.score},
//                 ${item.metadata.comments},
//                 '${item.metadata.username}'
//             )">Edit</button>

//             <button onclick="handleDelete('${item.id}')">Delete</button>
//         `;

//         container.appendChild(div);
//     });
// }


// ➕ ADD / UPDATE
async function handleAdd() {
    const data = {
        id: document.getElementById("id").value,
        title: document.getElementById("title").value,
        subreddit: document.getElementById("subreddit").value,
        score: parseInt(document.getElementById("score").value),
        comments: parseInt(document.getElementById("comments").value),
        username: document.getElementById("username").value
    };

    await updateAPI(data);

    alert("Saved!");
    loadData();
}


// ❌ DELETE
async function handleDelete(id) {
    await deleteAPI(id);
    alert("Deleted!");
    loadData();
}


// ✏️ EDIT (fill form)
function fillForm(id, title, subreddit, score, comments, username) {
    document.getElementById("id").value = id;
    document.getElementById("title").value = title;
    document.getElementById("subreddit").value = subreddit;
    document.getElementById("score").value = score;
    document.getElementById("comments").value = comments;
    document.getElementById("username").value = username;
}



async function loadData() {
    const data = await getListAPI();

    const tbody = document.getElementById("tableBody");
    tbody.innerHTML = "";

    data.forEach(item => {
        const row = `
            <tr>
                <td>${item.id}</td>
                <td>${item.metadata.title}</td>
                <td>${item.metadata.subreddit}</td>
                <td>${item.metadata.score}</td>
                <td>
                    <button class="btn btn-warning btn-sm"
                        onclick="fillForm(
                            '${item.id}',
                            '${item.metadata.title}',
                            '${item.metadata.subreddit}',
                            ${item.metadata.score},
                            ${item.metadata.comments},
                            '${item.metadata.username}'
                        )">Edit</button>

                    <button class="btn btn-danger btn-sm"
                        onclick="handleDelete('${item.id}')">Delete</button>
                </td>
            </tr>
        `;

        tbody.innerHTML += row;
    });
}