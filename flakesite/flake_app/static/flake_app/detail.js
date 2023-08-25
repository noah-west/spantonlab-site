
document.onreadystatechange = function(e){
    firstImage = document.getElementsByClassName("imagelink")[0]
    firstImage.click();
}

function openImage(event, imageField) {
    var i, imagecontents, imagelinks;
    imagecontents = document.getElementsByClassName("imagecontent");
    for (i = 0; i < imagecontents.length; i++) {
        imagecontents[i].style.display = "none";
    }
  
    imagelinks = document.getElementsByClassName("imagelink");
    for (i = 0; i < imagelinks.length; i++) {
        imagelinks[i].className = imagelinks[i].className.replace(" selected", "");
    }
    
    document.getElementById(imageField).style.display = "inline-table";
    event.currentTarget.className += " selected";
  }

function openCommentForm(event, commentField) {
    comment_form = document.getElementById(commentField).style.display = "block"
}

function closeCommentForm(event, commentField) {
    comment_form = document.getElementById(commentField).style.display = "none"
}