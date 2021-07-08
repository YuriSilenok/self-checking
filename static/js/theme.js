document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('group').onchange = filterStudent;
});
function filterStudent(){
    group_id = document.getElementById('group').value
    var xhr = new XMLHttpRequest();
    var url = "api/student?group="+group_id+"&not_discipline"
    xhr.open("GET", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var json = JSON.parse(xhr.responseText);
            student_element = document.getElementById('student');
            while(document.getElementById('student').options.length > 0){
                document.getElementById('student').options.remove(0);}
            for(var ind in json){
                var option_element = document.createElement('option');
                option_element.value = json[ind].id;
                option_element.innerHTML = json[ind].last_name + ' ' + json[ind].first_name[0] + '.' + json[ind].middle_name[0] + '.';
                student_element.appendChild(option_element);
            }
        }
    };
    xhr.send();
}