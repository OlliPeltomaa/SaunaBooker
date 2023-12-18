const timeslot = document.getElementById('timeslot');
const cancelslot = document.getElementById('cancelslot');
const bookform = document.getElementById('booksauna');
const cancelform = document.getElementById('cancelsauna');


const deselectSlots = () => {
    // get the timeslots from the table
    const tds = document.getElementsByTagName('td');

    // if any other slot is active, remove the active class
    for (let i = 0; i < tds.length; i++) {
        if (tds[i].classList.contains('activeSlot')) {
            tds[i].classList.remove('activeSlot');
        }
    }
}

// hide the cancel form and reset value
const hideCancelForm = () => {
    cancelslot.value = '';
    cancelform.classList.add('hidden');
}


const changeTimeslot = (date, hour) => {
    if (!cancelform.classList.contains('hidden')) {
        hideCancelForm();
    }

    // timeslot's id is combination of the date and the hour
    const id = date+'T'+hour;
    const td = document.getElementById(id);

    // if user clicks the same timeslot again, it is reset
    if (td.classList.contains('activeSlot')) {
        td.classList.remove('activeSlot');
        timeslot.value = '';
        bookform.classList.add('hidden');
        return;
    }

    deselectSlots();

    // set new color for the selected slot and update form value
    td.classList.add('activeSlot');
    timeslot.value = id;
    bookform.classList.remove('hidden');
}

const cancelBooking = (id) => {
    deselectSlots();

    // if same slot is already clicked, reset cancelling
    if (cancelslot.value === id) {
        hideCancelForm();
        return;
    }

    // hide booking form
    if (!bookform.classList.contains('hidden')) {
        bookform.classList.add('hidden');
    }

    // make cancelling form visible
    if (cancelform.classList.contains('hidden')) {
        cancelform.classList.remove('hidden');
    }

    // set the cancel form value
    cancelslot.value = id;
}