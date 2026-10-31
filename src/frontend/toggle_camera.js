function selectCamera(box) {
    const grid = document.getElementById("grid");
    const cameras = Array.from(grid.querySelectorAll(".camera-box"));

    // Click lại camera đang chọn -> quay về bố cục 2x2.
    if (box.classList.contains("selected")) {
        resetCameraLayout(grid, cameras);
        return;
    }

    grid.classList.add("expanded");

    cameras.forEach((camera, index) => {
        camera.classList.remove("selected", "thumbnail");
        camera.style.gridColumn = "";
        camera.style.gridRow = "";

        if (camera === box) {
            camera.classList.add("selected");
            camera.style.gridColumn = "1";
            camera.style.gridRow = "1 / 4";
        } else {
            camera.classList.add("thumbnail");
        }
    });

    // Ba camera còn lại xếp dọc ở bên phải camera được chọn.
    const thumbnails = cameras.filter(camera => camera !== box);
    thumbnails.forEach((camera, index) => {
        camera.style.gridColumn = "2";
        camera.style.gridRow = `${index + 1}`;
    });
}

function resetCameraLayout(grid, cameras) {
    grid.classList.remove("expanded");

    cameras.forEach(camera => {
        camera.classList.remove("selected", "thumbnail");
        camera.style.gridColumn = "";
        camera.style.gridRow = "";
    });
}

function toggleCamera(btn) {
    // Nút mở rộng có cùng hành vi với việc click vào khung camera.
    selectCamera(btn.closest(".camera-box"));
}
