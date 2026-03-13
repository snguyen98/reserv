$(document).ready(function() {
    // CSRF Header Setup
    var csrf_token = $('meta[name=csrf-token]').attr('content');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });

    if (window.location.pathname == '/') {
        const UNBOOKED_TEXT = "Available";

        var manage = false;
        var curr_user = "";
        
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
        $("#book-form").on("submit", function() {
            console.info("Booking date: " + selected_id);

            $.ajax({
                url: "/handlers/set_booker",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({ "date": selected_id }),
                success: function() {
                    console.info(`Successfully booked date: ${selected_id}`);
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
        * Defines the action for clicking the cancel button
        */
        $("#cancel-form").on("submit", function() {
            console.info("Cancelling date: " + selected_id);

            $.ajax({
                url: "/handlers/cancel_booking",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({ "date": selected_id }),
                success: function() {
                    console.info(`Successfully cancelled date: ${selected_id}`);
                    updateSchedule();
                },
                error: function(xhr) {
                    // Displays the error to the user as an message box
                    var msg = JSON.parse(xhr.responseText).message;
                    alert(msg);
                    
                    console.error(`Error cancelling date: ${selected_id}, ${msg}`);
                    updateSchedule();
                }
            });
        });

        /*
        * Handles the availability toggle button
        */
        $("#availability-list").on("click", "#availability-btn", function() {
            // Pass the user_id (you can store this in a data-attribute on the button)
            let uid = $(this).data("user-id"); 
            console.info("Toggling availability for date: " + selected_id + ", user_id: " + uid);
            
            $.ajax({
                url: "/handlers/toggle_availability",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({ "date": selected_id, "user_id": uid }),
                success: function() {
                    console.info(`Successfully toggled availability for user_id: ${uid}`);
                    updateSchedule();
                },
                error: function(xhr) {
                    var msg = JSON.parse(xhr.responseText).message;
                    alert(msg);

                    console.error(`Error toggling availability for user_id: ${uid}, ${msg}`);
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

            displayInfo(selected_id);
            displayAvailability(selected_id);

            //console.debug("Date selected: " + selected_id);
        });

        /*
        * Updates the booking status of each cell in the schedule
        */
        function updateSchedule() {
            var date_list = [];

            $('.schedule-cell').each(function() {
                date_list.push($(this).attr('id'));
            });

            console.debug(`Updating dates: ${date_list}`)

            // Performs an ajax call to get the booking status
            $.getJSON({
                url: "/handlers/get_bookers",
                data: { "date_list": date_list },
                contentType: "application/json; charset=utf-8",
                success: function(data) {
                    bookings = data.res;

                    for (const date in bookings) {
                        var cell_id = "#" + date;
                        var cellData = bookings[date];
                        $(cell_id).data("unavailable-users", cellData.unavailable);
                        
                        // Sets custom html data attribute for booker
                        $(cell_id).data("booker", cellData.booker);

                        $(cell_id).removeClass("table-danger table-success table-warning");

                        if (cellData.hasUnavailable) {
                            $(cell_id).addClass("table-warning"); 
                        } else if (cellData.isBooked) {
                            $(cell_id).addClass("table-danger");
                        } else {
                            $(cell_id).addClass("table-success");
                        }
                    }
                    displaySelected();          // Refreshes the info card
                    findNextBooking();          // Refreshes the upcoming card

                    var now = new Date();
                    datetime = `${now.toDateString()} ${now.toTimeString()}`
                    console.info(`Schedule updated at: ${datetime}`);
                },
                error: function(xhr) {
                    var msg = JSON.parse(xhr.responseText).message;
                    console.error("Error retrieving booker data: " + msg);
                }
            });
        }

        /*
        * Finds the next booked date from today
        */
        function findNextBooking() {
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
                displayAvailability(selected_id);
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

            hasPerm("manage");

            if (!manage) {
                getCurrentUser();
            }

            var date = new Date(cell_date);

            // Displays the appropriate info whether the date is booked or not
            if (booker != "") {
                $("#info-booker").text(booker);            
                $("#book-btn").hide();
                
                // Hides if date is in the past or user doesn't match booker
                if (IsDateInFuture(date) && (manage || booker == curr_user)) {
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
                if (IsDateInFuture(date)) {
                    $("#book-btn").show();
                }
                else {
                    $("#book-btn").hide();
                }
            }
        }

        /*
        * Updates the status dots and text opacity based on availability
        */
        function displayAvailability(cell_date) {
            // Hides the blank card
            $("#availability-content").show();
            $("#availability-blank").hide();

            // 1. Retrieve the unavailable list for the selected date
            // We can piggyback on the data already stored in the cell during updateSchedule()
            var unavailableList = $("#" + cell_date).data("unavailable-users") || [];

            console.debug("Unavailable users for date: "+ cell_date + ", users: " + unavailableList);

            // 2. Loop through each user in the list
            $("#availability-list .list-group-item").each(function() {
                // Extract the user_id from the LI ID (e.g., availability-5)
                var userId = $(this).attr('id').replace('availability-', '');
                
                var isUnavailable = unavailableList.includes(userId);

                console.log("--- DEBUG ---");
                console.log("Looking for:", JSON.stringify(userId));
                console.log("Inside Array:", JSON.stringify(unavailableList));
                console.log("Found:", unavailableList.includes(userId));
                console.log("Index:", unavailableList.indexOf(userId));

                var dot = $(this).find(".status-indicator");
                var nameText = $(this).find(".username");

                if (isUnavailable) {
                    // Mark as Inactive/Gray
                    dot.removeClass("active").addClass("inactive");
                    nameText.addClass("text-muted").removeClass("text-dark");
                } else {
                    // Mark as Active/Green
                    dot.removeClass("inactive").addClass("active");
                    nameText.addClass("text-dark").removeClass("text-muted");
                }
            });
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
                    // Returns the response
                    curr_user = data.user;
                },
                error: function(xhr) {
                    var msg = JSON.parse(xhr.responseText).message;
                    console.error(`Error retrieving current user: ${msg}`)
                }
            });
        }

        /*
        * Performs an ajax call (non-async) to check if the logged in user has
        * the supplied permission permissions
        */
        function hasPerm(perm) {
            $.getJSON({
                url: "/handlers/check_perm",
                data: { "perm": perm },
                async: false,
                success: function(data) {
                    // Sets the global variable, manage to the response
                    manage = data.res;
                },
                error: function(xhr) {
                    var msg = JSON.parse(xhr.responseText).message;
                    console.error(`Error checking ${perm} permissions: ${msg}`);
                }
            });
        }
    }
});