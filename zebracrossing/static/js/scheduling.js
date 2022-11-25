function getDayName(date) {
  const days = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ];
  return days[date.getDay()];
}

function daysBetween(start, end) {
  const dayList = [];
  const currentDate = new Date(start);
  // eslint-disable-next-line no-unmodified-loop-condition
  for (let i = 0; currentDate < end; i++) {
    currentDate.setDate(start.getDate() + i);
    // Add a copy of the date so that it is not modified by the next iteration
    dayList.push(new Date(currentDate));
  }
  return dayList;
}

/**
 * Returns the days between start and end divided up by week
 */
function getWeeklyDays(start, end) {
  if (!start || !end) {
    alert("Please create a bookingsheet in the database");
  }
  const dayList = [];
  const currentDate = new Date(start);
  // eslint-disable-next-line no-unmodified-loop-condition
  for (let i = 0; currentDate < end; i += 7) {
    currentDate.setDate(start.getDate() + i);
    const endDate = new Date(currentDate);
    endDate.setDate(endDate.getDate() + 7);
    dayList.push(daysBetween(currentDate, endDate));
  }
  return dayList;
}

/**
 * Returns a list of td nodes long enough to contain numDays number of days
 */
function populateRow(numDays) {
  const data = [];
  for (let i = 0; i < numDays; i++) {
    const td = document.createElement("TD");
    td.classList.add("editable");
    data.push(td);
  }
  return data;
}

function sendToServer(schedule) {
  const payloadSchedule = JSON.stringify(schedule);
  $.ajax({
    url: "schedule/save",
    type: "POST",
    data: {
      schedule: payloadSchedule,
      csrfmiddlewaretoken: document.getElementById("csrf-token").innerHTML,
    },
  }).fail(function () {
    console.log("Error Occurred");
  });
}

function drawTable(
  weeksBooked,
  paginationOffset,
  dayRange,
  timeslots,
  schedule
) {
  const table = document.getElementById("timeslot-table");
  for (let i = 0; i < Object.keys(timeslots).length; i++) {
    const timeslotTd = document.createElement("TD");
    timeslotTd.classList.add("time");
    timeslotTd.innerHTML = timeslots[i].toString();
    const rowData = populateRow(dayRange);
    rowData.unshift(timeslotTd);
    const row = table.insertRow();
    row.innerHTML = rowData;
    console.log(row.cells);
  }

  for (let i = 0; i < weeksBooked[paginationOffset].length; i++) {
    const header = document.createElement("TH");
    header.setAttribute("scope", "col");
    header.innerHTML = getDayName(weeksBooked[paginationOffset][i]);
    table.tHead.firstElementChild.appendChild(header);
  }

  if (paginationOffset === Object.keys(weeksBooked).length - 1) {
    document.getElementById("next-button").disabled = true;
  }

  if (paginationOffset === 0) {
    document.getElementById("previous-button").disabled = true;
  }

  const visibleSchedule = schedule.slice(
    paginationOffset,
    paginationOffset + dayRange
  );

  for (let i = 0; i < visibleSchedule.length; i++) {
    for (let j = 0; j < visibleSchedule[i].length; j++) {
      table.rows[j].cells[i].innerHTML = visibleSchedule[i][j] ? "X" : "";
    }
  }
}

// eslint-disable-next-line no-unused-vars
function processScheduleTable(start, end, timeslots, schedule) {
  const weeksBooked = getWeeklyDays(start, end);
  let paginationOffset = 0;
  const dayRange = 7;

  drawTable(weeksBooked, paginationOffset, dayRange, timeslots, schedule);

  document.getElementById("previous-button").onClick(function () {
    paginationOffset -= dayRange;

    if (paginationOffset < 0) {
      paginationOffset = 0;
    }

    drawTable(weeksBooked, paginationOffset, dayRange, timeslots, schedule);
  });

  document.getElementById("next-button").onClick(function () {
    paginationOffset += dayRange;

    if (
      paginationOffset >
      weeksBooked[weeksBooked.length - 1].length - dayRange
    ) {
      paginationOffset = weeksBooked[weeksBooked.length - 1].length - dayRange;
    }

    drawTable(weeksBooked, paginationOffset, dayRange, timeslots, schedule);
  });

  $("td").on("input", function () {
    const cell = $(this);
    const slotTime = cell.closest("tr").find(".time").text();
    const headerDate = cell.closest("table").find("th").eq(cell.index()).text();
    schedule.push({ slot_time: slotTime, date: headerDate });
  });

  document.getElementById("table-edit").onClick(function () {
    const currentTD = document.getElementsByClassName("editable");
    if ($(this).html() == "Edit") {
      $.each(currentTD, function () {
        $(this).prop("contenteditable", true);
      });
    } else {
      $.each(currentTD, function () {
        $(this).prop("contenteditable", false);
      });
    }
    if ($(this).html() === "Save") {
      sendToServer(schedule);
    }
    $(this).html($(this).html() === "Edit" ? "Save" : "Edit");
  });
}
