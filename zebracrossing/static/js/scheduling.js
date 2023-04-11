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

function daysBetween(startDate, endDate) {
  var dateArray = new Array();
  let currentDate = startDate;
  while (currentDate <= endDate) {
    dateArray.push(new Date(currentDate));
    currentDate = startDate.setDate(startDate.getDate() + 1);
  }
  return dateArray;
}

/**
 * Returns the days between start and end divided up by week
 */
function getWeeklyDays(startDate, endDate) {
  let arr = daysBetween(startDate, endDate);
  const res = [];
  let limit = 0;
  while (limit <= arr.length) {
    res.push(arr.slice(limit, 7 + limit));
    limit += 7;
  }
  if (res.slice(-1)[0].length == 0) {
    res.pop(-1);
  }
  return res;
}

/**
 * Returns a list of td nodes long enough to contain numDays number of days
 */

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

function add_td_to_table(weeksBooked, count) {
  var tds = "";
  for (var j = 0; j < weeksBooked[count].length; j++) {
    tds += "<td class='editable'></td>";
  }
  return tds;
}

function drawTable(
  weeksBooked,
  paginationOffset,
  dayRange,
  timeslots,
  schedule,
  count
) {
  const table = document.getElementById("timeslot-table");
  var content_holder = "";
  for (let i = 0; i < Object.keys(timeslots).length; i++) {
    const timeslotTd = document.createElement("TD");
    timeslotTd.classList.add("time");
    timeslotTd.innerHTML = timeslots[i].fields.time.slice(0, 5);

    var table_content = `<tr>
    <td class='time'>${timeslotTd.innerHTML}</td>
    ${add_td_to_table(weeksBooked, count)}
    </tr>`;
    content_holder += table_content;

    var tableData = document.querySelector("tbody");
    tableData.innerHTML = content_holder;
  }
  var days = weeksBooked[count];
  var headers = document.querySelector("#timeslot-table thead tr:first-child");
  var header_obj = `<th>Slot</th>`;
  for (let i = 0; i < days.length; i++) {
    const header = document.createElement("TH");
    header.setAttribute("scope", "col");
    header_obj += `<th>${(header.innerHTML =
      getDayName(days[i]) +
      " " +
      days[i].getDate() +
      " " +
      days[i].toLocaleString("default", { month: "long" }))}</th>`;
    headers.innerHTML = header_obj;
  }

  if (paginationOffset === 0) {
    document.getElementById("previous-button").disabled = true;
    document.getElementById("next-button").disabled = false;
  }

  const visibleSchedule = schedule.slice(
    paginationOffset,
    paginationOffset + dayRange
  );

  for (let i = 0; i < visibleSchedule.length; i++) {
    for (let j = 0; j < visibleSchedule[i].length; j++) {
      table.rows[j + 1].cells[i + 1].innerHTML = visibleSchedule[i][j]
        ? "X"
        : "";
    }
  }
}

function createTableEditDate(startDate, paginationOffset, table_column_index) {
  let currentDate = new Date(startDate);
  return new Date(
    currentDate.setDate(
      new Date(startDate).getDate() +
        paginationOffset +
        (table_column_index - 1)
    )
  );
}

var count = 0;
var startDate = "";
// eslint-disable-next-line no-unused-vars
function processScheduleTable(
  start,
  end,
  timeslots,
  schedule,
  bookingsheet_id
) {
  const starting_date = new Date(start);
  var table_data = [];
  $(function () {
    $(document).on("input", ".editable", function () {
      let table_column_index = $(this).closest("td").index();
      const cell = $(this);
      const slotTime = cell.closest("tr").find(".time").text();
      table_data.push({
        slot_time: slotTime,
        date: createTableEditDate(
          starting_date,
          paginationOffset,
          table_column_index
        ),
        bookingsheet_id: bookingsheet_id,
      });
    });
  });

  const weeksBooked = getWeeklyDays(start, end);
  let paginationOffset = 0;
  const dayRange = 7;

  drawTable(
    weeksBooked,
    paginationOffset,
    dayRange,
    timeslots,
    schedule,
    count
  );

  document.getElementById("previous-button").onclick = function () {
    if (count > 1 && count < weeksBooked.length) {
      document.getElementById("next-button").disabled = false;
    }
    paginationOffset -= dayRange;
    count--;
    drawTable(
      weeksBooked,
      paginationOffset,
      dayRange,
      timeslots,
      schedule,
      count
    );
  };

  document.getElementById("next-button").onclick = function () {
    paginationOffset += dayRange;
    count++;
    if (count >= 1) {
      document.getElementById("previous-button").disabled = false;
    }
    if (count == weeksBooked.length - 1) {
      document.getElementById("next-button").disabled = true;
    }

    drawTable(
      weeksBooked,
      paginationOffset,
      dayRange,
      timeslots,
      schedule,
      count
    );
  };

  document.getElementById("table-edit").onclick = function () {
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
      sendToServer(table_data);
    }
    $(this).html($(this).html() === "Edit" ? "Save" : "Edit");
  };
}
