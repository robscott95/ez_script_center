function menuSearch(id) {
    var input, filter, ul, li, a, i, txtValue;
    input = document.getElementById(id);
    filter = id.value.toUpperCase();
    itemContainer = document.getElementById("tool-menu");
    items = itemContainer.getElementsByTagName('a');

    for(let item of items) {
        toolName = item.getElementsByTagName('h3')[0].textContent

        if (toolName.toUpperCase().indexOf(filter) > -1) {
            item.style.display = ""
        } else {
            item.style.display = "none"
        }
    }
}