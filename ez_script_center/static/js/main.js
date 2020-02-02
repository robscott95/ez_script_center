function menuSearch(id) {
    let input, filter, ul, li, a, i, txtValue;
    input = document.getElementById(id);
    filter = id.value.toUpperCase();
    let itemContainer = document.getElementById("tool-menu");
    let items = itemContainer.getElementsByTagName('a');

    for (let item of items) {
        let toolName = item.getElementsByTagName('h3')[0].textContent;

        if (toolName.toUpperCase().indexOf(filter) > -1) {
            item.style.display = ""
        } else {
            item.style.display = "none"
        }
    }
}