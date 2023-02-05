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
  for (let i = 0; i < end.getDate()-1; i += 6) {
    currentDate.setDate(start.getDate() + i);
    const endDate = new Date(currentDate);
    endDate.setDate(endDate.getDate() + 6);
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

function add_td_to_table(weeksBooked, count){
  var tds = ""
  for (var j=0; j < weeksBooked[count].length; j++){
  tds += "<td class='editable'></td>"
  }
  return tds
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
  var content_holder = ""
  for (let i = 0; i < Object.keys(timeslots).length; i++) {
    const timeslotTd = document.createElement("TD");  
    timeslotTd.classList.add("time");
    timeslotTd.innerHTML = timeslots[i].fields.time;

    var table_content =
    `<tr>
    <td class='time'>${timeslotTd.innerHTML}</td>
    ${add_td_to_table(weeksBooked, count)}
    </tr>`
    content_holder += table_content

    var tableData = document.querySelector('tbody')
    tableData.innerHTML = content_holder
  }
  var days = weeksBooked[count]
  var headers = document.querySelector('#timeslot-table thead tr:first-child')
  var header_obj = `<th>Slot</th>`
  for (let i = 0; i < days.length; i++) {
    const header = document.createElement("TH");
    header.setAttribute("scope", "col");
    header_obj += `<th>${header.innerHTML = getDayName(days[i]) +" "+ days[i].getDate() + " "+ days[i].toLocaleString('default', { month: 'long' })}</th>`
    headers.innerHTML = header_obj 
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
      table.rows[j+1].cells[i+1].innerHTML = visibleSchedule[i][j] ? "X" : "";
    }
  }
}

var count = 0
// eslint-disable-next-line no-unused-vars
function processScheduleTable(start, end, timeslots, schedule, bookingsheet_id) {
  const weeksBooked = getWeeklyDays(start, end);
  let paginationOffset = 0;
  const dayRange = 7;

  drawTable(weeksBooked, paginationOffset, dayRange, timeslots, schedule, count);

  document.getElementById("previous-button").onclick = function () {
    paginationOffset -= dayRange
    count --;
    drawTable(weeksBooked, paginationOffset, dayRange, timeslots, schedule, count);
  };

  document.getElementById("next-button").onclick = function () {
    paginationOffset += dayRange;
    count ++;
    if (count >= 1){
      document.getElementById("previous-button").disabled = false
    }
    if (count == weeksBooked.length-1){
      document.getElementById("next-button").disabled = true
    }

    drawTable(weeksBooked, paginationOffset, dayRange, timeslots, schedule, count);
  };

  var table_data = []
  $("td").on("input", function () {
    const cell = $(this);
    const slotTime = cell.closest("tr").find(".time").text();
    const headerDate = cell.closest("table").find("th").eq(cell.index()).text();
    table_data.push({ slot_time: slotTime, date: headerDate, bookingsheet_id: bookingsheet_id });
  });

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
