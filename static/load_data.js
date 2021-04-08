var result_data = {};

const readSingleFile = (e) => {
  var file = e.target.files[0];
  if (!file) {
    return;
  }
  result_data.name = e.target.files[0].name;
  var reader = new FileReader();
  reader.onload = function (e) {
    var contents = e.target.result;
    displayContents(contents);
  };
  reader.readAsText(file);
}

const displayContents = contents => {
  result_data.data = contents;
  contents = JSON.parse(contents);

  document.getElementById('device_id').textContent = contents["device_id"];
  document.getElementById('datetime').textContent = contents["datetime"];

  for (var i = 1; i <= 13; i++) {

    document.getElementById('name_' + i).textContent = contents[i.toString()]["name"];
    document.getElementById('result_' + i).textContent = contents[i.toString()]["result"] + "\n" + contents[i.toString()]["param"];
    document.getElementById('status_' + i).textContent = contents[i.toString()]["status"];

    if (contents[i.toString()]["status"] == "Failed") {
      document.getElementById('result_' + i).style.color = "red";
      document.getElementById('status_' + i).style.color = "red";
    } else {
      document.getElementById('result_' + i).style.color = "green";
      document.getElementById('status_' + i).style.color = "green";
    }

  }

}

document.getElementById('file-input')
  .addEventListener('change', readSingleFile, false);

$('#exampleModalCenter').on('show.bs.modal', function (event) {
  document.getElementById("alert").textContent = "";
  $("#downloadFullCSV").on("click", () => {
    $("#alert").css({ "color": "black" });
    document.getElementById("alert").textContent = "Please Wait your file is being processed...";
    var start_date = document.getElementById("start_date").value;
    var end_date = document.getElementById("end_date").value;
    console.log(start_date);
    if (start_date == "") {
      document.getElementById("alert").textContent = "Please Enter Start Date";
      $("#alert").css({ "color": "red" });
      return
    }
    if (end_date == "") {
      document.getElementById("alert").textContent = "Please Enter End Date";
      $("#alert").css({ "color": "red" });
      return
    }
    console.log(start_date, end_date)
    $.ajax({
      type: "POST",
      url: "/csv_dated",
      data: JSON.stringify({ start_date: start_date, end_date: end_date }),  // serializes the form's elements.
      success: data => {
        document.getElementById("alert").textContent = "Status: " + data;
      }
    });
  })
})

const changeorg = () => {
  document.getElementById("org_id").innerHTML = "<input type='text' id='org_text'><button class='btn btn-primary' id='org_save' type='button'>Save</button>";
  $("#org_save").on("click", () => {
    document.getElementById("org_id").innerHTML = document.getElementById("org_text").value;
  });

}

const download_csv = () => {
  console.log(result_data);
  $.ajax({
    type: "POST",
    url: "/download_csv",
    data: JSON.stringify(result_data),  // serializes the form's elements.
    success: data => {
      alert(data);
    }
  });
}