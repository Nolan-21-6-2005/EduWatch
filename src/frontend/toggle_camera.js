function toggleCamera(btn){

    const box = btn.closest(".camera-box");
    const grid = document.getElementById("grid");

    if(!grid.classList.contains("expanded")) {

        grid.classList.add("expanded");

        document.querySelectorAll(".camera-box").forEach(cam => {
            if(cam !== box){
                cam.classList.add("hidden");
            }
        });

    box.classList.add("selected");

    btn.innerHTML = "⤢";

    }else{
        grid.classList.remove("expanded");
        
        document.querySelectorAll(".camera-box").forEach(cam => {
            cam.classList.remove(
                "hidden",
                "selected"
            );
        });

        btn.innerHTML = "⛶";
    }
}
