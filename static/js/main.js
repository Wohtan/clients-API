window.onload = function disable_previous() {
    if (actual_page == 0) {
        document.getElementById("Previous").className = "page-item disabled";
    }
    if (actual_page == pages_number-1) {
        document.getElementById("Next").className = "page-item disabled";
    }
    var ID = "Page " + (actual_page + 1)
    document.getElementById(ID).className = "page-item active";
}

