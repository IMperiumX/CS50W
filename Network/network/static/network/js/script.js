like = document.querySelectorAll(".liked");

like.forEach((element) => {
  like_handeler(element);
});

function like_handeler(element) {
  element.addEventListener("click", () => {
    id = element.getAttribute("data-id");
    is_liked = element.getAttribute("data-is_liked");
    icon = document.querySelector(`#post-like-${id}`);
    count = document.querySelector(`#post-count-${id}`);

    form = new FormData();
    form.append("id", id);
    form.append("is_liked", is_liked);
    fetch("/like/", {
      method: "POST",
      body: form,
    })
      .then((res) => res.json())
      .then((res) => {
        if (res.status == 201) {
          if (res.is_liked === "yes") {
            icon.src = "https://img.icons8.com/plasticine/100/000000/like.png";
            element.setAttribute("data-is_liked", "yes");
          } else {
            icon.src =
              "https://img.icons8.com/carbon-copy/100/000000/like--v2.png";
            element.setAttribute("data-is_liked", "no");
          }
          count.textContent = res.like_count;
        }
      })
      .catch(function (res) {
        alert("Network Error. Please Check your connection.");
      });
  });
}
