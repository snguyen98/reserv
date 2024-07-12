$(document).ready(function() {
    const UNBOOKED_TEXT = "Available";
    
    var current_user = "";
    getCurrentUser();
    console.debug(`User: ${current_user}`)
    
    // Fetches the schedule and repeats every 7 seconds
    updateSchedule();
    setInterval(updateSchedule, 7000);

    // Initialises cards to be blank
    var selected_id = null;

    $("#display-blank").show();
    $("#display-info").hide();

    $("#upcoming-blank").show();
    $("#upcoming-body").hide();

    /*
    * Defines the action for clicking the book button
    */
    $("#book-btn").on("click", function() {
        console.info("Booking date: " + selected_id);
        
        // Perform an ajax call to the server to book the selected date
        $.getJSON({
            url: "/handlers/set_booker",
            data: { "date": selected_id },
            success: function() {
                console.info(`Successfully booked date: ${selected_id}`);
                // Update to display the new booking
                updateSchedule();
            },
            error: function(xhr) {
                // Displays the error to the user as an message box
                var msg = JSON.parse(xhr.responseText).message;
                alert(msg);
                
                console.error(`Error booking date: ${selected_id}, ${msg}`);
                updateSchedule();
            }
        });
    });

    /*
    * Defines the action for clicking the book button
    */
    $("#cancel-btn").on("click", function() {
        console.info("Cancelling date: " + selected_id)
        $.getJSON({
            url: "/handlers/cancel_booking",
            data: { "date": selected_id },
            success: function() {
                console.info(`Successfully cancelled date: ${selected_id}`);
                // Update to display the cancelled booking
                updateSchedule();
            },
            error: function(xhr) {
                var msg = JSON.parse(xhr.responseText).message;
                alert(msg);

                console.error(`Error cancelling date: ${selected_id}, ${msg}`);
                updateSchedule();
            }
        });
    });
    
    /*
    * Defines the action for hovering over a date cell in the schedule
    */
    $(".schedule-cell").hover(
        // On mouse enter - Display the hovered over cell
        function() {
            // console.debug(`Booker: ${$(this).data("booker")}`);
            displayInfo($(this).attr('id'));
        },
        // On mouse leave - Revert to the clicked on cell
        function() {
            displaySelected();
        }
    );

    /*
    * Defines the action for clicking on a date cell in the schedule
    */
    $(".schedule-cell").on("click", function() {
        // Changes selected cell flag from old cell to the clicked on cell
        $("#" + selected_id).removeClass("selected-cell");
        $(this).addClass("selected-cell");

        // Update selected_id global variable
        selected_id = $(this).attr('id');

        //console.debug("Date selected: " + selected_id);
    });

    /*
    * Updates the booking status of each cell in the schedule
    */
    function updateSchedule() {
        $('.schedule-cell').each(function() {
            var cell_date = $(this).attr('id');

            // Performs an ajax call to get the booking status
            $.getJSON({
                url: "/handlers/get_booker",
                data: { "date": cell_date },
                success: function(data) {
                    var cell_id = "#" + cell_date;
                    
                    // Sets custom html data attribute for booker
                    $(cell_id).data("booker", data.booker);

                    if (data.isBooked) {
                        // Makes the cell red
                        $(cell_id).addClass("table-danger");
                        $(cell_id).removeClass("table-success");
                    }
                    else {
                        // Makes the cell green
                        $(cell_id).addClass("table-success");
                        $(cell_id).removeClass("table-danger");
                    }

                    displaySelected();          // Refreshes the info card
                    findNextBooking();          // Refreshes the upcoming card
                },
                error: function(xhr) {
                    var msg = JSON.parse(xhr.responseText).message;
                    console.error("Error retrieving booker data: " + msg);
                }
            });
        });
        
        var now = new Date();
        datetime = `${now.toLocaleDateString()} ${now.toLocaleTimeString()}`
        console.info(`Schedule updated at: ${datetime}`);
    }

    /*
    * Finds the next booked date from today
    */
    function findNextBooking() {
        // Gets a Date object for today without the time
        var today = new Date(new Date().toDateString());

        // Loops through each cell
        $('.schedule-cell').each(function() {
            var cell_date = new Date($(this).attr('id'));
            // Retrieves the custom html data attribute - booker
            var booker = $(this).data("booker")
            
            // Checks if the cell is today or later and is booked
            if (IsDateInFuture(cell_date) && booker != "" && booker != null) {
                // Sets the upcoming card info to the current cell
                $("#upcoming-date").text($(this).find(".cell-text").text());
                $("#upcoming-booker").text(booker);

                $("#upcoming-blank").hide();
                $("#upcoming-body").show();

                return false;           // Break out of for each loop
            }

            // If there's no booked date in the future, show blank
            $("#upcoming-blank").show();
            $("#upcoming-body").hide();
        });
    }

    /*
    * Checks if there is a selected cell to display on the info card
    */
    function displaySelected() {
        // 
        if (selected_id != "" && selected_id != null) {
            displayInfo(selected_id);
        }
        else {
            // Shows the blank info card if no cell is selected
            $("#display-blank").show();
            $("#display-info").hide();
        }
    }

    /*
    * Displays the booking information on the info card
    */
    function displayInfo(cell_date) {
        // Hides the blank card
        $("#display-info").show();
        $("#display-blank").hide();

        // Sets the title to the date formatted with abbreviated month i.e. Jul
        $("#info-title").text($("#" + cell_date).find(".cell-text").text());

        // Retrieves the custom html data attribute - booker
        var booker = $("#" + cell_date).data("booker");
        // console.debug("Displaying: " + cell_date + ", " + booker);

        var selected_date = new Date(cell_date);

        // Displays the appropriate info whether the date is booked or not
        if (booker != "") {
            $("#info-booker").text(booker);            
            $("#book-btn").hide();
            
            // Hides the corresponding button if the date is in the past
            if (IsDateInFuture(selected_date) && booker == current_user) {
                $("#cancel-btn").show();
            }
            else {
                $("#cancel-btn").hide();
            }
        }
        else {
            $("#info-booker").text(UNBOOKED_TEXT);
            $("#cancel-btn").hide();

            // Hides the corresponding button if the date is in the past
            if (IsDateInFuture(selected_date)) {
                $("#book-btn").show();
            }
            else {
                $("#book-btn").hide();
            }
        }
    }
    
    /*
    * Checks if the supplied date is today or in the future (ignores time)
    */
    function IsDateInFuture(date) {
        var today = new Date();
        today.setHours(0, 0, 0, 0);

        return today <= date;
    }

    /*
    * Performs an ajax call (non-async) to get the currently logged in user
    */
    function getCurrentUser() {
        $.getJSON({
            url: "/handlers/get_current_user",
            async: false,
            success: function(data) {
                // Sets the global variable, current_user to the response
                current_user = data.user;
            },
            error: function(xhr) {
                var msg = JSON.parse(xhr.responseText).message;
                console.error("Error retrieving current user: " + msg);
            }
        });
    }
});