Dropzone.autoDiscover = false;

function init() {
    let dz = new Dropzone("#dropzone", {
        url: "/",
        maxFiles: 1,
        addRemoveLinks: true,
        dictDefaultMessage: "Some Message",
        autoProcessQueue: false
    });
    
    dz.on("addedfile", function() {
        if (dz.files[1]!=null) {
            dz.removeFile(dz.files[0]);        
        }
    });

    dz.on("complete", function (file) {
        let imageData = file.dataURL;
        
        var url = "http://127.0.0.1:5000/classify_image";

        $.post(url, {
            image_data: file.dataURL
        },function(data, status) {
            console.log("Classification response:", data);

            if (!data || data.length==0) {
                $("#resultHolder").hide();
                $("#divClassTable").hide();                
                $("#celebritySummary").hide();
                $("#error").show();
                return;
            }

            let match = null;
            let bestScore = -1;

            // Pick the best matching prediction
            for (let i=0;i<data.length;++i) {
                let maxScoreForThisClass = Math.max(...data[i].class_probability);
                if(maxScoreForThisClass>bestScore) {
                    match = data[i];
                    bestScore = maxScoreForThisClass;
                }
            }

            if (match) {
                $("#error").hide();
                $("#resultHolder").show();
                $("#divClassTable").show();

                // Show the player's card
                $("#resultHolder").html($(`[data-player="${match.class}"`).html());

                // Fill probability table
                let classDictionary = match.class_dictionary;
                for(let personName in classDictionary) {
                    let index = classDictionary[personName];
                    let proabilityScore = match.class_probability[index];
                    let elementName = "#score_" + personName;
                    $(elementName).html(proabilityScore);
                }

                // === Call /describe to get AI summary (existing behaviour) ===
                fetch("http://127.0.0.1:5000/describe", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ label: match.class })
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error("HTTP " + response.status);
                        }
                        return response.json();
                    })
                    .then(descData => {
                        console.log("AI summary response:", descData);
                        const summaryBox = $("#celebritySummary");

                        if (descData && descData.summary) {
                            summaryBox.show();
                            summaryBox.html(
                                `<strong>${descData.name}</strong><br>${descData.summary}`
                            );
                        } else {
                            summaryBox.show();
                            summaryBox.text("Could not load AI summary.");
                        }
                    })
                    .catch(err => {
                        console.error("Error calling /describe:", err);
                        const summaryBox = $("#celebritySummary");
                        summaryBox.show();
                        summaryBox.text("Could not load AI summary.");
                    });
            }
            // dz.removeFile(file);            
        });
    });

    $("#submitBtn").on('click', function (e) {
        dz.processQueue();		
    });
}

/* =========================
   WEBCAM LOOK-ALIKE MODE
   ========================= */

function initWebcam() {
    let stream = null;

    $("#startWebcamBtn").on("click", async function () {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("Webcam not supported in this browser.");
            return;
        }

        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            const video = document.getElementById("webcamVideo");
            video.srcObject = stream;
            $("#captureWebcamBtn").prop("disabled", false);
        } catch (err) {
            console.error("Error starting webcam:", err);
            alert("Could not access webcam. Check permissions.");
        }
    });

    $("#captureWebcamBtn").on("click", function () {
        const video = document.getElementById("webcamVideo");
        const canvas = document.getElementById("webcamCanvas");
        const webcamResult = $("#webcamResult");

        const width = video.videoWidth || 640;
        const height = video.videoHeight || 480;

        if (!width || !height) {
            alert("Webcam not ready yet. Please wait a moment and try again.");
            return;
        }

        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0, width, height);

        const dataUrl = canvas.toDataURL("image/jpeg");

        // Call the same /classify_image endpoint with the captured frame
        $.post("http://127.0.0.1:5000/classify_image", {
            image_data: dataUrl
        }, function (data, status) {
            console.log("Webcam classification:", data);

            if (!data || data.length === 0) {
                webcamResult.show().html(
                    "Couldn't detect a clear face with two eyes. Try again (better lighting, face centered)."
                );
                return;
            }

            // Pick best match from the predictions
            let match = null;
            let bestScore = -1;
            for (let i=0; i<data.length; ++i) {
                let maxScoreForThisClass = Math.max(...data[i].class_probability);
                if (maxScoreForThisClass > bestScore) {
                    match = data[i];
                    bestScore = maxScoreForThisClass;
                }
            }

            if (!match) {
                webcamResult.show().html("No confident prediction. Try again.");
                return;
            }

            const probs = match.class_probability || [];
            const similarity = probs.length ? Math.round(Math.max(...probs)) : 0;

            webcamResult.show().html(
                `You look most like <strong>${match.class.replace(/_/g, " ").toUpperCase()}</strong> `
                + `(similarity ~ <strong>${similarity}%</strong>).<br><em>Loading AI summary...</em>`
            );

            // Call /describe to get AI summary for the look-alike
            fetch("http://127.0.0.1:5000/describe", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ label: match.class })
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error("HTTP " + response.status);
                    }
                    return response.json();
                })
                .then(descData => {
                    let html = `You look most like <strong>${descData.name || match.class}</strong> `
                        + `(similarity ~ <strong>${similarity}%</strong>).`;

                    if (descData && descData.summary) {
                        html += `<hr><strong>About them:</strong> ${descData.summary}`;
                    }

                    webcamResult.html(html);
                })
                .catch(err => {
                    console.error("Error calling /describe (webcam):", err);
                    webcamResult.append("<br><em>Could not load AI summary.</em>");
                });
        });
    });
}

$(document).ready(function() {
    console.log( "ready!" );
    $("#error").hide();
    $("#resultHolder").hide();
    $("#divClassTable").hide();
    $("#celebritySummary").hide();
    $("#webcamResult").hide();

    init();
    initWebcam();
});

