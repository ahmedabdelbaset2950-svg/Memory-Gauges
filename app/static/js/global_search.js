const input = document.getElementById("globalSearch");
const results = document.getElementById("searchResults");

let timer = null;

input.addEventListener("keyup", function () {

    clearTimeout(timer);

    const q = this.value.trim();

    if (q.length < 2) {
        results.style.display = "none";
        results.innerHTML = "";
        return;
    }

    timer = setTimeout(() => {

        fetch(`/search?q=${encodeURIComponent(q)}`)
            .then(r => r.json())
            .then(data => {

                results.innerHTML = "";

                if (data.length === 0) {

                    results.innerHTML = `
                        <div class="search-item">
                            No results found
                        </div>
                    `;

                    results.style.display = "block";
                    return;
                }

                data.forEach(item => {

                    results.innerHTML += `
                        <div class="search-item"
                             onclick="window.location='${item.url}'">

                            <div>

                                <div class="search-type">
                                    ${item.type}
                                </div>

                                <div class="search-title">
                                    ${item.title}
                                </div>

                                <div class="search-sub">
                                    ${item.subtitle || ""}
                                </div>

                            </div>

                        </div>
                    `;

                });

                results.style.display = "block";

            });

    }, 250);

});

document.addEventListener("click", function (e) {

    if (!results.contains(e.target) &&
        e.target !== input) {

        results.style.display = "none";

    }

});