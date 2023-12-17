/* Javascript for SkyRoomXBlock. */
function SkyRoomXBlock(runtime, element) {
  $("#target-url").click(function (e) {
    e.preventDefault();
    {
      $.ajax({
        type: "POST",
        url: runtime.handlerUrl(element, "mark_as_viewed"),
        data: JSON.stringify({}),
        success: function (data) {
          console.log(data);
          if (data.result === "success") {
            let url = data.url;
            window.open(url, "_blank");
          }else if (data.result === "error") {
            $("#target-url").remove();
            // add an error message under target-url
            $(".skyroom-wrapper").append(`<p>${data.message}</p>`);
          }
        },
      });
    }
  });
}
