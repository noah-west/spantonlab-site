window.onload = function(){
    activeimage = document.getElementById("active")
    activeimage.click();
}

function openImage(event, imageField) {
    var i, imagecontents, imagelinks;
    console.log(imageField);
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