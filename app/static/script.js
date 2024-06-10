$(document).ready(function() {
    const UNBOOKED_TEXT = "Available";
    var selected_id = null;

    updateSchedule();
    setInterval(updateSchedule, 7000);

    $("#display-blank").show();
    $("#display-info").hide();

    $("#upcoming-blank").show();
    $("#upcoming-body").hide();

    $("#book-btn").on("click", function() {
        console.info("Booking date: " + selected_id)
        $.getJSON({
            url: "/handlers/set_booker",
            data: { "date": selected_id },
            success: function(data) {
                console.info("Successfully booked date: " + selected_id);
                updateSchedule();
            },
            error: function(xhr) {
                message = JSON.parse(xhr.responseText).message;
                alert(message);
                console.error("Error booking date: " + selected_id + ", " + message);
            }
        });
    });

    $("#cancel-btn").on("click", function() {
        console.info("Cancelling date: " + selected_id)
        $.getJSON({
            url: "/handlers/cancel_booking",
            data: { "date": selected_id },
            success: function(data) {
                console.info("Successfully cancelled date: " + selected_id)
                updateSchedule();
            },
            error: function(_, _, error) {
                //alert(xhr.responseText);                      // For debugging purposes
                console.error("Error booking date: " + selected_id + ", " + error);
            }
        });
    });
    
    $(".schedule-cell").hover(
        // On mouseenter
        function() {
            // console.debug("Booker: " + $(this).data("booker"));
            displayInfo($(this).attr('id'));
        },
        // On mouseleave
        function() {
            displaySelected();
        }
    );

    $(".schedule-cell").on("click", function() {
        $("#" + selected_id).removeClass("selected-cell");
        $(this).addClass("selected-cell");

        selected_id = $(this).attr('id');
        displayInfo(selected_id);

        console.debug("Date selected: " + selected_id);
    });

    function findNextBooking() {
        var today = new Date();

        $('.schedule-cell').each(function() {
            var cell_date = new Date($(this).attr('id'));
            
            if (cell_date >= today && $(this).data("booker") != "" && $(this).data("booker") != null) {
                $("#upcoming-date").text($(this).find(".cell-text").text());
                $("#upcoming-booker").text($(this).data("booker"));

                $("#upcoming-blank").hide();
                $("#upcoming-body").show();

                return false;                                   // Break out of for loop
            }

            $("#upcoming-blank").show();
            $("#upcoming-body").hide();
        });
    }

    function displaySelected() {
        if (selected_id != "" && selected_id != null) {
            displayInfo(selected_id);
        }
        else {
            $("#display-blank").show();
            $("#display-info").hide();
        }
    }

    function displayInfo(cell_date) {
        $("#display-info").show();
        $("#display-blank").hide();

        $("#info-title").text($("#" + cell_date).find(".cell-text").text());

        var booker = $("#" + cell_date).data("booker");
        // console.debug("Displaying: " + cell_date + ", " + booker);

        var today = new Date();
        var selected_date = new Date(cell_date);
        selected_date.setHours(23, 59, 59, 999);

        if (booker != "") {
            $("#info-booker").text(booker);
            $("#book-btn").hide();

            if (today <= selected_date) {
                $("#cancel-btn").show();
            }
            else {
                $("#cancel-btn").hide();
            }
        }
        else {
            $("#info-booker").text(UNBOOKED_TEXT);
            $("#cancel-btn").hide();

            if (today <= selected_date) {
                $("#book-btn").show();
            }
            else {
                $("#book-btn").hide();
            }
        }
    }

    function updateSchedule() {
        $('.schedule-cell').each(function() {
            var cell_date = $(this).attr('id');

            $.getJSON({
                url: "/handlers/get_booker",
                data: { "date": cell_date },
                success: function(data) {
                    var cell_id = "#" + cell_date;
                    $(cell_id).data("booker", data.res);            // Sets custom html data attribute for booker

                    if ($(cell_id).data("booker") != "") {
                        $(cell_id).addClass("table-danger");
                        $(cell_id).removeClass("table-success");
                    }
                    else {
                        $(cell_id).addClass("table-success");
                        $(cell_id).removeClass("table-danger");
                    }

                    displaySelected();                              // Refreshes the info card
                    findNextBooking();                              // Refreshes the upcoming card
                },
                error: function(_, _, error) {
                    //alert(xhr.responseText);                      // For debugging purposes
                    console.error("Error retrieving booker data: " + error);
                }
            });
        });
        
        var now = new Date();
        console.info(now.toLocaleDateString() + " " + now.toLocaleTimeString() + ": Schedule updated");
    }
});