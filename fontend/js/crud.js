async function handleAdd() {
    const data = {
        id: document.getElementById("id").value,
        title: document.getElementById("title").value,
        subreddit: document.getElementById("subreddit").value,
        score: parseInt(document.getElementById("score").value),
        comments: parseInt(document.getElementById("comments").value),
        username: document.getElementById("username").value
    };

    await addAPI(data);
    alert("Added!");
}